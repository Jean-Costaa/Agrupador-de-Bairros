# Agrupador de Bairros por Zona — Streamlit

## Conceito

Esta aplicação desenvolvida com [Streamlit](https://streamlit.io/) permite que usuários agrupem bairros de uma determinada cidade em "zonas personalizadas". Cada zona pode conter um ou mais bairros definidos manualmente. Ao final, é possível visualizar os agrupamentos no mapa e exportar um arquivo `.geojson` compatível com o sistema da empresa.

## ✨ Funcionalidades

- ✅ Visualização interativa de bairros no mapa.
- ➕ Criação de zonas personalizadas com múltiplos bairros.
- 📝 Nomeação de cada zona (ex: Zona 01, Zona Comercial etc.).
- 🔄 Edição e exclusão de zonas já criadas.
- 🗂️ Exportação do agrupamento completo em formato `.geojson`.
- 📤 Upload de CT
- 💾 Armazenamento temporário em cache local durante a sessão.


## 🛠️ Tecnologias Utilizadas

- **[Python 3.10+]**
- **Streamlit** – para criação da interface web interativa
- **GeoPandas** – para manipulação de dados geográficos
- **Folium**– para renderização de mapas 
- **Shapely** – para operações geométricas
- **Pandas** – para tratamento de dados tabulares

## 📁 Estrutura do Projeto

```bash

📁 Poligonos_shopee/

├── 📁 Poligonos_shopee/  
│   ├── 📁 modules/
│   │   ├── cor.py
│   │   ├── exporta.py
│   │   ├── mapa.py
│   │   ├── teste.ipynb
│   │   ├── uploads.py
│   ├── comando.txt
│   ├── mapa_renderizado.htm
│   ├── README.md
│   ├── requirements.txt
```


## Como Usar
1. Clonar o repositório
```bash

    git clone https://github.com/seu-usuario/nome-do-projeto.git
    cd nome-do-projeto
```

2. Instalar as dependências
```bash
    pip install -r requirements.txt
```

3. Executar o o site
```bash
    streamlit run app.py
```


## 📄 Licença
Este projeto está licenciado sob a MIT License.

## 👨‍💻 Autor
Jean Costa  - https://github.com/Jean-Costaa
