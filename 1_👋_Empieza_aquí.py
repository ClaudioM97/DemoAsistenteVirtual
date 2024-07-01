
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


import streamlit as st
from PIL import Image
import base64

with open( "app/style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)
    
st.markdown(
    """
        <style>
            [data-testid="stSidebar"] {
                background-image: url("https://brainfood.cl/wp-content/themes/theme_brainfood/assets/svgs/imagotipo-brainfood.svg");
                background-repeat: no-repeat;
                padding-top: 50px;
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

st.sidebar.markdown(
    """
    <style>
    .spacer {
        margin-top: 150px; 
    }
    </style>
    <div class="spacer"></div>
    ¿Quieres saber más de nosotros? <br><br>
    Visita <a href="https://brainfood.cl" target="_blank">Brain Food</a> para más información.<br>
    También puedes seguirnos en <a href="https://cl.linkedin.com/company/brain-food-spa" target="_blank">Linkedin</a>.
    """,
    unsafe_allow_html=True
)

st.title('👋 ¡Bienvenido al Asistente IA de Brain Food!')

st.markdown('''Esta aplicación basada en Inteligencia Artificial Generativa (GenAI) busca apoyar tu trabajo como director de empresa, permitiéndote  explorar tus documentos de forma más efectiva, facilitar tu preparación para reuniones para llegar a los puntos en que aportas más valor, y ayudarte a buscar asociaciones entre documentos para algún informe o charla que tengas que preparar.
    Todavía en estado de piloto, para probar su efectividad y recibir tu feedback, hemos desarrollado cuatro funcionalidades basadas en GenAI:
            ''')

with st.container():
    st.subheader('''1. Fichas documentos precargados
            ''')
    st.markdown('''En esta sección se encuentran precargados diferentes documentos públicos pertenecientes a blogs de retail y memorias anuales de Falabella.
                Sin embargo, en lugar de leer alguno de ellos de forma completa, hemos creado fichas de resumen para estos documentos usando IA.
                En tales fichas, se resume el documento en los siguientes elementos clave: fecha de creación del documento, fecha de guardado (fecha en la cual se crea la ficha), tipo de documento, título, autor, resumen, ideas principales y finalmente, keywords.
                El objetivo final es que cada vez que recibas un documento nuevo, puedas guardarlo en una carpeta y la IA genere la ficha de forma automática, para ayudarte a acercarte a los documentos nuevos, y a la vez tener un respaldo amigable del contenido de los antiguos.
                ''', unsafe_allow_html=True)
    
with st.container():
    st.subheader('2. Habla con los documentos precargados')
    st.markdown('''Aquí podras profundizar en aquellos documentos precargados que fueron de tu interés en la sección anterior a través de una
                conversación con nuestro asistente virtual. Puedes hacerle preguntas sobre lo que quieras saber más en detalle de los documentos.
                El objetivo final es que puedas interactuar de forma natural con tus documentos, que puedas ir directamente a los temas que para ti como director son clave, y que puedas guardar tus “preguntas tipo” mes a mes.
                ''',unsafe_allow_html=True)
    
with st.container():
    st.subheader('3. Prueba con tu propio documento')
    st.markdown('''En este apartado podrás cargar tu propio documento en formato PDF para que nuestro asistente virtual responda todas las preguntas que tengas sobre este.
                Además, puedes solicitarle tareas que vayan mas allá de preguntas sobre determinados tópicos. Por ejemplo, puedes pedir que realice resuménes, extraiga información relevante, analice secciones específicas del documento, entre otras.
                El objetivo final es que puedas identificar, asociar, e ir a consultar de forma directa los documentos que se parecen más a  tu pregunta o tema de interés. Es importante notar que la IA no responde directamente lo que aparece en estos segmentos, sólo los usa como contexto para darte la respuesta en la función de chatbot.<br><br>
                Por otro lado, como ésta es una versión piloto, el robot sólo puede interpretar el texto de los archivos, aún no comprende las tablas ni las imágenes.
                No obstante, es una funcionalidad que está en desarrollo. Te recomendamos probar con distintas maneras de formular tu pregunta – por ejemplo, resume o extrae los puntos más importantes entrega resultados muy distintos. Al ser un piloto, también te recomendamos probar con un documento PDF de texto liviano para que la carga no tome tanto tiempo.
                ''',unsafe_allow_html=True)