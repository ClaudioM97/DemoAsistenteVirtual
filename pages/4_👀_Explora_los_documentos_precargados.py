

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import streamlit as st
import plotly.graph_objs as go
from ragxplorer import RAGxplorer
from PIL import Image

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

st.markdown("""
<style>
div.stButton > button:first-child {
    display: block;
    margin: 20px auto;
}
</style>""", unsafe_allow_html=True)

os.environ['OPENAI_API_KEY'] = st.secrets["OPENAI_API_KEY"]


if "chart" not in st.session_state:
    st.session_state['chart'] = None

if "loaded" not in st.session_state:
    st.session_state['loaded'] = False

st.title("👀 Explora los documentos precargados")

st.markdown('''Con esta funcionalidad vas a poder ingresar tu consulta sobre cualquiera de los documentos precargados. A continuación se presentará un gráfico con los segmentos de texto más idóneos que responden a esa consulta, junto con el documento desde el cual provienen.
                El objetivo final es que puedas identificar, asociar, e ir a consultar de forma directa los documentos que se parecen más a tu pregunta o tema de interés. Es importante notar que la IA no responde directamente lo que aparece en estos segmentos, solo los usa como contexto para cumplir mejor su función de chatbot.

                ''')

col1, col2 = st.columns(2)
st.session_state['query'] = col1.text_area("Ingresa tu consulta aquí")
st.session_state['technique'] = 'Estándar'
st.session_state['top_k'] = col1.select_slider('Segmentos de texto a recuperar', options=[1,2,3,4,5], value=3)
#st.session_state['technique'] = col1.radio("Selecciona la técnica de retrieval", ["Estándar", "HyDE", "Multi_qns"], horizontal=True)
#st.session_state['top_k'] = col1.number_input("Top k", value=5, min_value=1, max_value=10, step=1)

if not st.session_state['loaded']:
    main_page = st.empty()
    main_button = st.empty()
    with main_page.container():
        st.session_state["chosen_embedding_model"] = "all-MiniLM-L6-v2"

    if col1.button("Ejecutar consulta"):
         st.session_state["client"] = RAGxplorer(embedding_model=st.session_state["chosen_embedding_model"])
         main_page.empty()
         main_button.empty()
         with st.spinner("Cargando base vectorial"):
             st.session_state["client"].load_pdf(query=st.session_state['query'])
             st.session_state['chart'] = st.session_state["client"].visualize_query(st.session_state['query'],
                                                                                retrieval_method=st.session_state['technique'],
                                                                                top_k=st.session_state['top_k'])
             st.session_state['loaded'] = True
             st.rerun()
else:
    
    if st.session_state['chart'] is not None:
        col2.plotly_chart(st.session_state['chart'])

    if col1.button("Reiniciar aplicación"):
        st.session_state['loaded'] = False
        st.rerun()

