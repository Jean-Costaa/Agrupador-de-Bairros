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

# Configuração da página
st.set_page_config(page_title="Polígonos", page_icon="🗺️", layout="wide")

# Sidebar
with st.sidebar:
    st.title("Polígonos Shopee")
    st.divider()
    estado_selecionado = st.selectbox("Selecione o estado", estados_brasileiros, )  # Rio Grande do Norte como padrão
    st.divider()
    arquivos = st.file_uploader("Carregue os arquivos de pedidos", type=["xlsx", "zip"], accept_multiple_files=True)
    df_pedidos = processar_arquivos(arquivos)
    gdf_pedidos = transformar_dataframe(df_pedidos)

# Carrega o mapa base do estado
mapa = carregar_mapa(estado_selecionado)

# Ajusta sistema de coordenadas
gdf_pedidos.set_crs(epsg=4326, inplace=True)
gdf_pedidos = gdf_pedidos.to_crs(mapa.crs)

# Associa pontos a polígonos
join = gpd.sjoin(gdf_pedidos, mapa, how="left", predicate="within")
contagem = join.groupby('index_right').size()
mapa['qtd_pedidos'] = 0
mapa.loc[contagem.index, 'qtd_pedidos'] = contagem.values
mapa_filtrado = mapa[mapa['qtd_pedidos'] > 0]

# Inicializa as zonas caso ainda não existam
if "zonas" not in st.session_state:
    st.session_state.zonas = []

col1, col2, col1 = st.columns([0.1, 2, 0.1])

with col2:
    with st.expander("Criar nova cluster", expanded=False):

        if not mapa.empty and "NM_BAIRRO" in mapa.columns:
            bairros_disponiveis = sorted(mapa["NM_BAIRRO"].dropna().unique().tolist())

            

        with st.form("form_add_zona", clear_on_submit=True):
            col1, col2 = st.columns([2, 1])
            with col1:
                nome_zona = st.text_input("Nome da nova zona")
            with col2:
                cor_zona = st.color_picker("Cor da zona", gerar_cor(len(st.session_state.zonas)))
            
            bairros_zona = st.multiselect("Selecione os bairros da nova zona", options=bairros_disponiveis)

            submit_zona = st.form_submit_button("Adicionar Zona")

            if submit_zona:
                if not nome_zona:
                    st.warning("⚠️ Nome da zona é obrigatório.")
                elif not bairros_zona:
                    st.warning("⚠️ Selecione ao menos um bairro.")
                else:
                    st.session_state.zonas.append({
                        "nome": nome_zona,
                        "bairros": bairros_zona,
                        "cor": cor_zona
                    })
                    st.success(f"✅ Zona '{nome_zona}' adicionada com sucesso!")



    with st.expander("Editar cluster existente", expanded=False):

        if st.session_state.zonas:
            zona_nomes = [zona["nome"] for zona in st.session_state.zonas]
            zona_selecionada = st.selectbox("Selecione uma zona para editar", zona_nomes, key="zona_selecionada")

            zona_idx = zona_nomes.index(zona_selecionada)
            zona_editar = st.session_state.zonas[zona_idx]

            with st.form("form_editar_zona"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    novo_nome = st.text_input("Novo nome da zona", value=zona_editar["nome"])
                with col2:
                    nova_cor = st.color_picker("Nova cor", value=zona_editar["cor"])

                novos_bairros = st.multiselect("Editar bairros da zona", options=bairros_disponiveis, default=zona_editar["bairros"])

                col1, col2 = st.columns([1, 1])
                salvar = col1.form_submit_button("💾 Salvar alterações")
                excluir = col2.form_submit_button("🗑️ Excluir zona")

                if salvar:
                    zona_editar["nome"] = novo_nome
                    zona_editar["cor"] = nova_cor
                    zona_editar["bairros"] = novos_bairros
                    st.session_state.zonas[zona_idx] = zona_editar
                    st.success(f"✅ Zona '{novo_nome}' atualizada com sucesso!")

                if excluir:
                    st.session_state.zonas.pop(zona_idx)
                    st.success(f"🗑️ Zona '{zona_selecionada}' removida com sucesso.")
                    st.rerun()





    # Se houver dados e mapa com pedidos
    if arquivos and not mapa_filtrado.empty:
        media_lat = gdf_pedidos["Latitude"].mean()
        media_lon = gdf_pedidos["Longitude"].mean()
        fmap = folium.Map(location=[media_lat, media_lon], zoom_start=12)

        # Adiciona polígonos básicos com pedidos
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

        # Adiciona zonas personalizadas
        for zona in st.session_state.zonas:
            bairros_filtrados = mapa[mapa["NM_BAIRRO"].isin(zona["bairros"])]
            if bairros_filtrados.empty:
                continue

            zona_unida = bairros_filtrados.dissolve()
            lista_bairros = bairros_filtrados['NM_BAIRRO'].tolist()
            municipio = bairros_filtrados['NM_MUN'].unique()[0] if len(bairros_filtrados['NM_MUN'].unique()) == 1 else "Múltiplos"
            soma_pedidos = int(bairros_filtrados['qtd_pedidos'].sum())

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
                <b>Município:</b> {municipio}<br>
                <b>Bairros:</b> {', '.join(lista_bairros)}<br>
                <b>Total de Pedidos:</b> {format(soma_pedidos, ',').replace(',', '.')}
            """, max_width=350)
            popup_zona.add_to(zona_geojson)
            zona_geojson.add_to(fmap)

        # Pontos de pedidos
        mc = FastMarkerCluster(gdf_pedidos[['Latitude', 'Longitude']])
        fmap.add_child(mc)

        #st_folium(fmap, width=1100, height=550)

        fmap.save('G:\Meu Drive\Projetos\Poligonos_Shopee\mapa_renderizado.html')

        # Carrega e exibe o HTML como iframe
        with open("G:\Meu Drive\Projetos\Poligonos_Shopee\mapa_renderizado.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        html(html_content, height=500, scrolling=True)


        #=================Exportar GeoJSON=================

        if st.button("📤 Exportar zonas como .geojson"):
            if st.session_state.zonas:
                geojson_str = gerar_geojson_zonas(
                    zonas=st.session_state.zonas,
                    mapa=mapa,
                    gdf_pedidos=gdf_pedidos,
                    campo_station="Destination Station",     # Pode mudar para outro campo depois
                    campo_regional=None                      # Pode usar "Regional" se tiver no Excel
                )

                st.download_button(
                    label="📎 Baixar GeoJSON",
                    data=geojson_str,
                    file_name="zonas_exportadas.geojson",
                    mime="application/geo+json"
                )




    else:
        st.info("Carregue os arquivos para exibir o mapa.")
