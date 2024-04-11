
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from functions import display_in_pairs
from streamlit_searchbox import st_searchbox
from functions import filter_fichas
import json
from PIL import Image

st.set_page_config(layout="wide")

with open( "app/style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)
    
    
st.markdown(
    """
        <style>
            [data-testid="stSidebar"] {
                background-image: url("https://brainfood.cl/wp-content/themes/theme_brainfood/assets/svgs/imagotipo-brainfood.svg");
                background-repeat: no-repeat;
                padding-top: 80px;
                background-position: 20px -20px;
                background-size: 170px 170px; 
            }
        </style>
        """,
    unsafe_allow_html=True,
)   

st.markdown("""
<style>
    .css-1d391kg, .css-1e5imcs, div[data-testid="stSidebar"] {
        border-radius: 0px !important;
    }
    .st-bq, .st-br, .css-10trblm, .css-1v3fvcr {
        border-radius: 0px !important;
    }
</style>
""", unsafe_allow_html=True)

page_bg_img = '''
<style>
[data-testid="stAppViewContainer"]{
background-image: url("https://brainfood.cl/wp-content/uploads/2023/02/header-estrategia.svg");
background-size: cover;
background-position: bottom 300px right -850px;
background-repeat: no-repeat;
}
[data-testid="stSidebar"]{
background-color:rgba(64, 64, 64, 1)

}

</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

st.title('📂 Fichas documentos precargados')

with open('lista_diccionarios.txt', 'r',encoding='utf-8') as archivo:
    contenido = archivo.read()
    lista_diccionarios = json.loads(contenido)


st.markdown('''En esta sección se encuentran precargados diferentes documentos públicos pertenecientes a blogs de retail y memorias anuales de Falabella.
                Sin embargo, en lugar de leer alguno de ellos de forma completa, hemos creado fichas de resumen para estos documentos usando IA.
                El objetivo final es que cada vez que recibas un documento nuevo, puedas guardarlo en una carpeta y la IA genere la ficha de forma automática, para ayudarte a acercarte a los documentos nuevos, y a la vez tener un respaldo amigable del contenido de los antiguos.
                ''', unsafe_allow_html=True)


tab1,tab2,tab3,tab4 = st.tabs(["Memorias", "Blogs - tendencias de retail","Blogs - competencia en retail",
                      "Blogs - experiencia del cliente"])


search_term = st.sidebar.text_input("Buscar en cada barra por la ficha:")

with tab1:
    st.header('Memorias disponibles')
    fichas_memorias = [lista_diccionarios[7],lista_diccionarios[8],lista_diccionarios[9],
                       lista_diccionarios[10],lista_diccionarios[11]]
    filtered_fichas_tb1 = filter_fichas(fichas_memorias, search_term)
    if filtered_fichas_tb1:
        display_in_pairs(filtered_fichas_tb1)
    else:
        st.write("No se encontraron fichas que coincidan con el término de búsqueda.")
    
    
with tab2:
    st.header('Blogs disponibles')
    fichas_blogs_tendencias = [lista_diccionarios[2],
                               lista_diccionarios[3],
                               lista_diccionarios[4],
                               lista_diccionarios[10],
                               lista_diccionarios[11]]
    filtered_fichas_tb2 = filter_fichas(fichas_blogs_tendencias, search_term)
    if filtered_fichas_tb2:
        display_in_pairs(filtered_fichas_tb2)
    else:
        st.write("No se encontraron fichas que coincidan con el término de búsqueda.")
   
                    
with tab3:
    st.header('Blogs disponibles')
    fichas_blogs_competencia = [lista_diccionarios[0],
                               lista_diccionarios[1],
                               lista_diccionarios[6],
                               lista_diccionarios[12],
                               lista_diccionarios[14],
                               lista_diccionarios[15]]
    filtered_fichas_tb3 = filter_fichas(fichas_blogs_competencia, search_term)
    if filtered_fichas_tb3:
        display_in_pairs(filtered_fichas_tb3)
    else:
        st.write("No se encontraron fichas que coincidan con el término de búsqueda.")
        
        
with tab4:
    st.header('Blogs disponibles')
    fichas_blogs_experiencia = [lista_diccionarios[5],
                               lista_diccionarios[13]
                               ]
    filtered_fichas_tb4 = filter_fichas(fichas_blogs_experiencia, search_term)
    if filtered_fichas_tb4:
        display_in_pairs(filtered_fichas_tb4)
    else:
        st.write("No se encontraron fichas que coincidan con el término de búsqueda.")