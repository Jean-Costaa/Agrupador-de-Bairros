from shapely.geometry import mapping
import geopandas as gpd
import json

def gerar_geojson_zonas(zonas, mapa, gdf_pedidos, campo_station="Destination Station", campo_regional=None):
    features = []

    for zona in zonas:
        # Compatibilidade para zonas antigas sem 'tipo' e 'elementos'
        tipo = zona.get("tipo", "Bairros")
        elementos = zona.get("elementos", zona.get("bairros", []))

        if tipo == "Bairros":
            dados_filtrados = mapa[mapa["BAIRRO_MUN"].isin(elementos)]
        else:
            dados_filtrados = mapa[mapa["NM_MUN"].isin(elementos)]

        if dados_filtrados.empty:
            continue

        zona_unida = dados_filtrados.dissolve()
        geometria = zona_unida.geometry.values[0]

        # Localizar pedidos dentro da zona
        gdf_zona = gpd.GeoDataFrame(geometry=[geometria], crs=mapa.crs)
        pedidos_na_zona = gpd.sjoin(gdf_pedidos, gdf_zona, how="inner", predicate="within")

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
                "name": zona['nome'],
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
