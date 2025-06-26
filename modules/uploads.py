import pandas as pd
import openpyxl
import io
import zipfile
import geopandas as gpd
from shapely.geometry import Point, LinearRing, Polygon


def processar_arquivos(arquivos):
    """Processa os arquivos carregados e retorna um DataFrame consolidado."""
    df_pedidos = pd.DataFrame()
    
    for arquivo in arquivos:
        if arquivo.name.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(arquivo.read()), "r") as zip_ref:
                for nome_arquivo in zip_ref.namelist():
                    if nome_arquivo.endswith(".xlsx"):
                        with zip_ref.open(nome_arquivo) as file:
                            df = pd.read_excel(file)
                            df_pedidos = pd.concat([df_pedidos, df], ignore_index=True)
                            
        elif arquivo.name.endswith(".xlsx"):
            df = pd.read_excel(arquivo)
            df_pedidos = pd.concat([df_pedidos, df], ignore_index=True)
    
    if "Zipcode" in df_pedidos.columns:
        df_pedidos["Zipcode"] = df_pedidos["Zipcode"].astype(str).str.replace("-", "")

    return df_pedidos



def transformar_dataframe(df_pedidos):
    """Transforma o DataFrame de pedidos para o formato desejado."""    

    #Adicionar uma coluna 'geometry' com pontos
    df_pedidos['geometry'] = None

    for index, row in df_pedidos.iterrows():
        df_pedidos.loc[index, 'geometry'] = Point(row['Longitude'], row['Latitude'])

    #Transformar o DataFrame em um GeoDataFrame
    gdf_pedidos = gpd.GeoDataFrame(df_pedidos, geometry='geometry')

    return gdf_pedidos
