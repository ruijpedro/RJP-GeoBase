# Fontes cartográficas e publicação

O RJP-GeoBase separa **código público** de **dados de origem e pacotes derivados**. Antes de redistribuir qualquer dado da Infraestruturas de Portugal (IP), confirmar termos de licença e atribuição aplicáveis a cada conjunto de dados.

## Fontes aceites na versão 0.1.0

- `inputs/rail.zip`: Shapefile da rede ferroviária (EPSG:3763).
- `inputs/roads.zip`: Shapefile da rede rodoviária (EPSG:3763).
- `inputs/stations.zip`: Shapefile das estações/apeadeiros (EPSG:3763).

Cada ZIP deve conter `.shp`, `.shx`, `.dbf` e `.prj` relativos ao mesmo ficheiro.

## Tratamento

1. Validar sistema de referência, formato e atributos mínimos.
2. Não corrigir silenciosamente geometrias inválidas: rejeitar e registar a razão no relatório.
3. Reprojetar elementos aceites para WGS84 (EPSG:4326).
4. Gerar `geobase.gpkg`, três GeoJSON, relatório e `manifest.json` com SHA-256.
5. Manter as fontes externas intactas e fora do Git.

## GitHub Actions

Sem fontes no repositório, o workflow executa **apenas os testes**. A compilação dos dados só ocorre quando existirem três ficheiros em `inputs/`, disponibilizados em ambiente autorizado. Não colocar dados de acesso restrito num repositório público. Não fazer upload dos derivados para GitHub Releases sem licenciamento confirmado.

## Limitações

A versão 0.1.0 não calcula PK oficiais nem inclui altimetria, hidrografia ou posicionamento em tempo real. Os PK requerem referências calibradas e gestão de descontinuidades quilométricas.
