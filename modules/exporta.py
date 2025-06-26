from shapely.geometry import mapping
import geopandas as gpd
import json

def gerar_geojson_zonas(zonas, mapa, gdf_pedidos, campo_station="Destination Station", campo_regional=None):
    """
    Gera um GeoJSON das zonas com base nas geometrias e dados dos pedidos.

    Parâmetros:
    - zonas: lista de dicionários com nome, bairros e cor.
    - mapa: GeoDataFrame com os bairros e geometrias.
    - gdf_pedidos: GeoDataFrame com os pedidos georreferenciados.
    - campo_station: nome da coluna nos pedidos para preencher 'station_name'.
    - campo_regional: nome da coluna nos pedidos para preencher 'regional' (opcional).

    Retorna:
    - String no formato GeoJSON pronta para exportação.
    """

    features = []

    for zona in zonas:
        bairros_filtrados = mapa[mapa["NM_BAIRRO"].isin(zona["bairros"])]
        if bairros_filtrados.empty:
            continue

        zona_unida = bairros_filtrados.dissolve()
        geometria = zona_unida.geometry.values[0]

        # Localizar pedidos dentro da zona
        gdf_zona = gpd.GeoDataFrame(geometry=[geometria], crs=mapa.crs)
        pedidos_na_zona = gpd.sjoin(gdf_pedidos, gdf_zona, how="inner", predicate="within")

        # Pegar valores
        station_name = (
            pedidos_na_zona[campo_station].mode().iloc[0]
            if not pedidos_na_zona.empty and campo_station in pedidos_na_zona.columns
            else "Desconhecida"
        )

        regional = (
            pedidos_na_zona[campo_regional].mode().iloc[0]
            if campo_regional and campo_regional in pedidos_na_zona.columns and not pedidos_na_zona.empty
            else "SPM"
        )

        feature = {
            "type": "Feature",
            "geometry": mapping(geometria),
            "properties": {
                "name": f"{zona['nome']}",
                "station_name": station_name,
                "regional": regional
            }
        }

        features.append(feature)

    geojson_final = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:EPSG::4674"
            }
        },
        "features": features
    }

    return json.dumps(geojson_final, ensure_ascii=False, indent=2)
