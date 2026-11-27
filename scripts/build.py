#!/usr/bin/env python3
"""Build validated offline packages from authorized IP source archives."""
import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.validation import explain_validity

LAYERS = {
    "rail": ("rail.zip", "railway"),
    "roads": ("roads.zip", "roads"),
    "stations": ("stations.zip", "stations"),
}
REQUIRED = {
    "railway": ["designacao", "exploracao"],
    "roads": ["roadnumber", "categoria"],
    "stations": ["Designacao", "Linha", "Estado"],
}

def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_shapefile(archive):
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
        shp = [name for name in names if name.lower().endswith(".shp") and not name.startswith("__MACOSX")]
        if len(shp) != 1:
            raise ValueError(f"Expected exactly one shapefile in {archive}: found {len(shp)}")
        stem = shp[0][:-4].lower()
        for extension in (".shx", ".dbf", ".prj"):
            if not any(item.lower() == stem + extension for item in names):
                raise ValueError(f"Missing {extension} in {archive}")
    frame = gpd.read_file(f"zip://{archive.resolve()}")
    if frame.crs is None:
        raise ValueError(f"Missing CRS: {archive}")
    if frame.crs.to_epsg() != 3763:
        raise ValueError(f"Unexpected CRS {frame.crs}: expected EPSG:3763")
    return frame

def validate(frame, layer):
    absent = [c for c in REQUIRED[layer] if c not in frame.columns]
    if absent:
        raise ValueError(f"Missing required fields for {layer}: {absent}")
    problems = []
    allowed = {"stations": {"Point", "MultiPoint"}, "railway": {"LineString", "MultiLineString"}, "roads": {"LineString", "MultiLineString"}}[layer]
    kept = []
    for i, feature in frame.iterrows():
        shape = feature.geometry
        reason = None
        if shape is None or shape.is_empty:
            reason = "empty_geometry"
        elif shape.geom_type not in allowed:
            reason = "wrong_geometry_type"
        elif not shape.is_valid:
            reason = "invalid_geometry: " + explain_validity(shape)
        elif any(pd.isna(feature[col]) or str(feature[col]).strip() == "" for col in REQUIRED[layer]):
            reason = "missing_required_attribute"
        if reason:
            problems.append({"row": int(i), "reason": reason})
        else:
            kept.append(i)
    return frame.loc[kept].copy(), problems

def build(source_dir, output_dir, version):
    output_dir.mkdir(parents=True, exist_ok=True)
    layer_frames = {}
    report = {"version": version, "generated_at": datetime.now(timezone.utc).isoformat(), "layers": {}, "source_sha256": {}}
    for source_key, (archive_name, layer) in LAYERS.items():
        archive = source_dir / archive_name
        if not archive.is_file():
            raise FileNotFoundError(f"Source missing: {archive}")
        original = read_shapefile(archive)
        validated, issues = validate(original, layer)
        validated = validated.to_crs(epsg=4326)
        validated.insert(0, "geobase_id", [f"{layer}-{i + 1:06d}" for i in validated.index])
        layer_frames[layer] = validated
        report["source_sha256"][archive_name] = digest(archive)
        report["layers"][layer] = {"received": len(original), "accepted": len(validated), "rejected": len(issues), "issues": issues}
    gpkg = output_dir / "geobase.gpkg"
    if gpkg.exists():
        gpkg.unlink()
    for layer, frame in layer_frames.items():
        frame.to_file(gpkg, driver="GPKG", layer=layer, mode="w" if not gpkg.exists() else "a", index=False)
        frame.to_file(output_dir / f"{layer}.geojson", driver="GeoJSON", index=False)
    report_path = output_dir / "validation-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    files = [p for p in output_dir.glob("*") if p.is_file()]
    manifest = {"schema": 1, "version": version, "crs": "EPSG:4326", "generated_at": report["generated_at"], "files": [{"name": p.name, "bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(files)]}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: {j: v for j, v in d.items() if j != "issues"} for k, d in report["layers"].items()}, indent=2))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", type=Path, default=Path("inputs"))
    ap.add_argument("--output", type=Path, default=Path("dist"))
    ap.add_argument("--version", default="0.1.0")
    args = ap.parse_args()
    build(args.sources, args.output, args.version)
