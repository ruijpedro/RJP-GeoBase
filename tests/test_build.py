from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import geopandas as gpd
from shapely.geometry import LineString, Point
from build import validate

def test_accept_valid_station():
    df = gpd.GeoDataFrame([{"Designacao":"Exemplo","Linha":"Linha X","Estado":"Com Exploração","geometry":Point(-9,39)}], crs="EPSG:4326")
    good, problems = validate(df,"stations")
    assert len(good)==1 and not problems

def test_reject_wrong_type():
    df = gpd.GeoDataFrame([{"Designacao":"Exemplo","Linha":"Linha X","Estado":"Com Exploração","geometry":LineString([(0,0),(1,1)])}],crs="EPSG:4326")
    good, problems = validate(df,"stations")
    assert len(good)==0 and problems[0]["reason"]=="wrong_geometry_type"

def test_required_attribute():
    df = gpd.GeoDataFrame([{"designacao":"","exploracao":"Com Exploração","geometry":LineString([(0,0),(1,1)])}],crs="EPSG:4326")
    good, issues = validate(df,"railway")
    assert len(good)==0 and issues[0]["reason"]=="missing_required_attribute"
