# RJP-GeoBase

Base cartográfica nacional comum às aplicações RJP Train Live, RJP Navigator e RJP Hidráulica.

O código e os fluxos de validação são públicos; os dados originais da IP **não são redistribuídos** sem confirmação de licença.

## Primeira fase

- Importar as três camadas Shapefile oficiais disponibilizadas localmente (ferrovia, rodovia e estações).
- Validar geometrias e atributos, preservando registos problemáticos no relatório.
- Gerar um pacote GeoPackage e GeoJSON em WGS84, com manifest e checksums.
- Construir artefactos offline por GitHub Actions através de upload manual das fontes autorizadas.

Ver [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) após a configuração inicial.
