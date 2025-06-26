import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, LinearRing, Polygon
from folium.plugins import FastMarkerCluster
import folium.features
import folium
import pandas as pd
import openpyxl
import os
from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent.parent  # raiz do projeto
MAPAS_DIR  = BASE_DIR / "data" 

# Mapeamento de nomes de estados → caminho do arquivo GeoJSON
MAPAS_ESTADOS = {
    "Acre": r"BR_bairros_municipios_Acre.geojson",
    "Alagoas": r"BR_bairros_municipios_Alagoas.geojson",
    "Amapá": r"BR_bairros_municipios_Amapá.geojson",
    "Amazonas": r"BR_bairros_municipios_Amazonas.geojson",
    "Bahia": r"BR_bairros_municipios_Bahia.geojson",
    "Ceará": r"BR_bairros_municipios_Ceará.geojson",
    "Distrito Federal": r"BR_bairros_municipios_Distrito Federal.geojson",
    "Espírito Santo": r"BR_bairros_municipios_Espírito Santo.geojson",
    "Goiás": r"BR_bairros_municipios_Goiás.geojson",
    "Maranhão": r"BR_bairros_municipios_Maranhão.geojson",
    "Mato Grosso": r"BR_bairros_municipios_Mato Grosso.geojson",
    "Mato Grosso do Sul": r"BR_bairros_municipios_Mato Grosso do Sul.geojson",
    "Minas Gerais": r"BR_bairros_municipios_Minas Gerais.geojson",
    "Pará": r"BR_bairros_municipios_Pará.geojson",
    "Paraíba": r"BR_bairros_municipios_Paraíba.geojson",
    "Paraná": r"BR_bairros_municipios_Paraná.geojson",
    "Pernambuco": r"BR_bairros_municipios_Pernambuco.geojson",
    "Piauí": r"BR_bairros_municipios_Piauí.geojson",
    "Rio de Janeiro": r"BR_bairros_municipios_Rio de Janeiro.geojson",
    "Rio Grande do Norte": r"BR_bairros_municipios_Rio Grande do Norte.geojson",
    "Rio Grande do Sul": r"BR_bairros_municipios_Rio Grande do Sul.geojson",
    "Rondônia": r"BR_bairros_municipios_Rondônia.geojson",
    "Roraima": r"BR_bairros_municipios_Roraima.geojson",
    "Santa Catarina": r"BR_bairros_municipios_Santa Catarina.geojson",
    "São Paulo": r"BR_bairros_municipios_São Paulo.geojson",
    "Sergipe": r"BR_bairros_municipios_Sergipe.geojson",
    "Tocantins": r"BR_bairros_municipios_Tocantins.geojson"
}



def carregar_mapa(estado):
    nome_arquivo = MAPAS_ESTADOS.get(estado)
    if not nome_arquivo:
        raise ValueError(f"Estado '{estado}' não configurado.")

    caminho = MAPAS_DIR / nome_arquivo

    if not caminho.exists():               # avisa no Streamlit
        import streamlit as st
        st.error(f"GeoJSON não encontrado: {caminho}")
        return gpd.GeoDataFrame()

    # elimina limite de tamanho do driver, caso o ficheiro seja grande
    os.environ.setdefault("OGR_GEOJSON_MAX_OBJ_SIZE", "0")

    return gpd.read_file(caminho)          



