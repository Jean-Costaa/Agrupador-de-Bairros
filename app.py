import streamlit as st
import geopandas as gpd
import folium
from folium.plugins import FastMarkerCluster
from streamlit_folium import st_folium
from streamlit.components.v1 import html
from modules.uploads import processar_arquivos, transformar_dataframe
from modules.mapa import carregar_mapa
from modules.exporta import gerar_geojson_zonas
from modules.cor import gerar_cor

estados_brasileiros = [
    "Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará",
    "Distrito Federal", "Espírito Santo", "Goiás", "Maranhão",
    "Mato Grosso", "Mato Grosso do Sul", "Minas Gerais", "Pará",
    "Paraíba", "Paraná", "Pernambuco", "Piauí", "Rio de Janeiro",
    "Rio Grande do Norte", "Rio Grande do Sul", "Rondônia",
    "Roraima", "Santa Catarina", "São Paulo", "Sergipe", "Tocantins"
]

st.set_page_config(page_title="Polígonos", page_icon="🚀", layout="wide")

with st.sidebar:
    st.title("Polígonos Shopee")
    st.divider()
    estado_selecionado = st.selectbox("Selecione o estado", estados_brasileiros)
    st.divider()
    arquivos = st.file_uploader("Carregue os arquivos de pedidos", type=["xlsx", "zip"], accept_multiple_files=True)
    df_pedidos = processar_arquivos(arquivos)
    gdf_pedidos = transformar_dataframe(df_pedidos)

mapa = carregar_mapa(estado_selecionado)

# Ajuste coordenadas e contagem
mapa["BAIRRO_MUN"] = mapa["NM_BAIRRO"] + " - " + mapa["NM_MUN"]
gdf_pedidos.set_crs(epsg=4326, inplace=True)
gdf_pedidos = gdf_pedidos.to_crs(mapa.crs)
join = gpd.sjoin(gdf_pedidos, mapa, how="left", predicate="within")
contagem = join.groupby('index_right').size()
mapa['qtd_pedidos'] = 0
mapa.loc[contagem.index, 'qtd_pedidos'] = contagem.values
mapa_filtrado = mapa[mapa['qtd_pedidos'] > 0]

if "zonas" not in st.session_state:
    st.session_state.zonas = []
else:
    # Corrige zonas antigas sem o campo 'tipo'
    for zona in st.session_state.zonas:
        if "tipo" not in zona:
            zona["tipo"] = "Bairros"
            zona["elementos"] = zona.get("bairros", [])

col1, col2, col3 = st.columns([0.1, 2, 0.1])

with col2:
    with st.expander("Criar nova cluster", expanded=False):
        tipo_zona = st.radio("Agrupar por:", ["Bairros", "Municípios"], horizontal=True, key="tipo_zona_criacao")

        with st.form("form_add_zona", clear_on_submit=True):
            col1, col2 = st.columns([2, 1])
            with col1:
                nome_zona = st.text_input("Nome da nova zona")
            with col2:
                cor_zona = st.color_picker("Cor da zona", gerar_cor(len(st.session_state.zonas)))

            if tipo_zona == "Bairros":
                opcoes_disponiveis = sorted(mapa["BAIRRO_MUN"].dropna().unique().tolist())
            else:
                opcoes_disponiveis = sorted(mapa["NM_MUN"].dropna().unique().tolist())

            elementos_selecionados = st.multiselect(f"Selecione os {'bairros' if tipo_zona == 'Bairros' else 'municípios'} da nova zona", options=opcoes_disponiveis)
            submit_zona = st.form_submit_button("Adicionar Zona")

            if submit_zona:
                if not nome_zona:
                    st.warning("⚠️ Nome da zona é obrigatório.")
                elif not elementos_selecionados:
                    st.warning("⚠️ Selecione ao menos um bairro ou município.")
                else:
                    st.session_state.zonas.append({
                        "nome": nome_zona,
                        "tipo": tipo_zona,
                        "elementos": elementos_selecionados,
                        "cor": cor_zona
                    })
                    st.success(f"✅ Zona '{nome_zona}' adicionada com sucesso!")

    with st.expander("Editar cluster existente", expanded=False):
        if st.session_state.zonas:
            zona_nomes = [zona["nome"] for zona in st.session_state.zonas]
            zona_selecionada = st.selectbox("Selecione uma zona para editar", zona_nomes, key="zona_selecionada")

            zona_idx = zona_nomes.index(zona_selecionada)
            zona_editar = st.session_state.zonas[zona_idx]

            if zona_editar["tipo"] == "Bairros":
                opcoes_disponiveis = sorted(mapa["BAIRRO_MUN"].dropna().unique().tolist())
            else:
                opcoes_disponiveis = sorted(mapa["NM_MUN"].dropna().unique().tolist())

            with st.form("form_editar_zona"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    novo_nome = st.text_input("Novo nome da zona", value=zona_editar["nome"])
                with col2:
                    nova_cor = st.color_picker("Nova cor", value=zona_editar["cor"])

                novos_elementos = st.multiselect(f"Editar {'bairros' if zona_editar['tipo'] == 'Bairros' else 'municípios'} da zona", options=opcoes_disponiveis, default=zona_editar["elementos"])

                col1, col2 = st.columns([1, 1])
                salvar = col1.form_submit_button("💾 Salvar alterações")
                excluir = col2.form_submit_button("🗑️ Excluir zona")

                if salvar:
                    zona_editar["nome"] = novo_nome
                    zona_editar["cor"] = nova_cor
                    zona_editar["elementos"] = novos_elementos
                    st.session_state.zonas[zona_idx] = zona_editar
                    st.success(f"✅ Zona '{novo_nome}' atualizada com sucesso!")

                if excluir:
                    st.session_state.zonas.pop(zona_idx)
                    st.success(f"🗑️ Zona '{zona_selecionada}' removida com sucesso.")
                    st.rerun()

    if arquivos and not mapa_filtrado.empty:
        media_lat = gdf_pedidos["Latitude"].mean()
        media_lon = gdf_pedidos["Longitude"].mean()
        fmap = folium.Map(location=[media_lat, media_lon], zoom_start=12)

        for _, row in mapa_filtrado.iterrows():
            geojson = folium.GeoJson(
                row.geometry,
                style_function=lambda feature: {
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.1
                }
            )
            popup = folium.Popup(f"""
                <strong>Município:</strong> {row.get('NM_MUN', 'N/A')}<br>
                <strong>Bairro:</strong> {row.get('NM_BAIRRO', 'N/A')}<br>
                <strong>Qtd. Pedidos:</strong> {int(row['qtd_pedidos']):,.0f}
            """, max_width=300)
            geojson.add_child(popup)
            geojson.add_to(fmap)

        for zona in st.session_state.zonas:
            if zona["tipo"] == "Bairros":
                dados_filtrados = mapa[mapa["BAIRRO_MUN"].isin(zona["elementos"])]
            else:
                dados_filtrados = mapa[mapa["NM_MUN"].isin(zona["elementos"])]

            if dados_filtrados.empty:
                continue

            zona_unida = dados_filtrados.dissolve()
            lista_bairros = dados_filtrados['NM_BAIRRO'].tolist()
            municipios = dados_filtrados['NM_MUN'].unique()
            municipio_lbl = ", ".join(sorted(municipios)) if len(municipios) > 0 else "Múltiplos"
            soma_pedidos = int(dados_filtrados['qtd_pedidos'].sum())

            zona_geojson = folium.GeoJson(
                zona_unida,
                name=zona["nome"],
                style_function=lambda feature, cor=zona["cor"]: {
                    "color": cor,
                    "weight": 2,
                    "fillOpacity": 0.4,
                    "fillColor": cor
                }
            )
            popup_zona = folium.Popup(f"""
                <b>Zona:</b> {zona["nome"]}<br>
                <b>Município(s):</b> {municipio_lbl}<br>
                <b>Total de Bairros:</b> {len(lista_bairros)}<br>
                <b>Total de Pedidos:</b> {format(soma_pedidos, ',').replace(',', '.')}
            """, max_width=350)
            popup_zona.add_to(zona_geojson)
            zona_geojson.add_to(fmap)

        mc = FastMarkerCluster(gdf_pedidos[['Latitude', 'Longitude']])
        fmap.add_child(mc)
        fmap.save('mapa_renderizado.html')

        with open("mapa_renderizado.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        html(html_content, height=500, scrolling=True)

        if st.button("📤 Exportar zonas como .geojson"):
            if st.session_state.zonas:
                geojson_str = gerar_geojson_zonas(
                    zonas=st.session_state.zonas,
                    mapa=mapa,
                    gdf_pedidos=gdf_pedidos,
                    campo_station="Destination Station",
                    campo_regional=None
                )

                st.download_button(
                    label="📌 Baixar GeoJSON",
                    data=geojson_str,
                    file_name="zonas_exportadas.geojson",
                    mime="application/geo+json"
                )
    else:
        st.info("Carregue os arquivos para exibir o mapa.")