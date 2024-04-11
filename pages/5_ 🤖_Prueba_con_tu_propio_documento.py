__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import openai
import streamlit as st
from dotenv import load_dotenv
import os
from functions import *
from streamlit_profiler import Profiler
from PIL import Image

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

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

#p = Profiler()
#p.start()
st.title("🤖 Prueba con tu propio documento")

st.markdown('''En este apartado podrás cargar tu propio documento en formato PDF para que nuestro asistente virtual responda todas las preguntas que tengas sobre éste.
                Además, puedes solicitarle tareas que vayan mas allá de preguntas sobre determinados tópicos. Por ejemplo, puedes pedir que realice resuménes, extraiga información relevante, analice secciones específicas del documento, entre otras.
                El objetivo final es que puedas identificar, asociar, e ir a consultar de forma directa los documentos que se parecen más a  tu pregunta o tema de interés. Es importante notar que la IA no responde directamente lo que aparece en estos segmentos, sólo los usa como contexto para darte la respuesta en la función de chatbot.<br><br>
                Por otro lado, como ésta es una versión piloto, el robot sólo puede interpretar el texto de los archivos, aún no comprende las tablas ni las imágenes.
                No obstante, es una funcionalidad que está en desarrollo. Te recomendamos probar con distintas maneras de formular tu pregunta, por ejemplo, resume o extrae los puntos más importantes entrega resultados muy distintos. Al ser un piloto, también te recomendamos probar con un documento PDF de texto liviano para que la carga no tome tanto tiempo.
                ''',unsafe_allow_html=True)

uploaded_file = st.file_uploader("Carga tu archivo PDF", type="pdf")

if uploaded_file is not None:
     with st.spinner("Procesando..."):
        
         st.write("Archivo cargado:", uploaded_file.name)
    
         text = extract_text_from_pdf(uploaded_file)
         text_clean = clean_text(text)
         text_chunks = get_text_chunks(text_clean)
         conversation_chain = get_conversation_chain(text_chunks)
         memory = load_memory(st)
         
         
if question := st.chat_input("Escribe tu pregunta aquí"):
        st.session_state.messages.append({"role": "user", "content": question})
        st.chat_message("user").write(question)
        
        with st.spinner("Generando respuesta..."):
            response = conversation_chain(
                {
                "question": question,
                "chat_history": memory.load_memory_variables({})["history"],   
                }
            )
            answer = response["answer"]
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.chat_message("assistant").write(answer)
            
#p.stop()

st.sidebar.button('Limpiar historial del chat', on_click=reset_conversation)