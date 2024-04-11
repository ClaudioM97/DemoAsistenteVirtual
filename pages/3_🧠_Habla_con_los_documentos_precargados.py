import streamlit as st
import os
from functions import *
from dotenv import load_dotenv
import openai
from PIL import Image

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

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


st.markdown("""
<style>
button {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Habla con los documentos precargados")

st.markdown('''
Explora en detalle los documentos que fueron de tu interés mediante diálogos con nuestro asistente virtual, enfocándote en temas clave y guardando preguntas recurrentes para facilitar la interacción natural y eficiente con tu información crítica. <br><br>
        Al costado izquierdo, puedes seleccionar el número de segmentos de texto a recuperar.
        Piensa en los segmentos como pequeñas porciones o trozos de los documentos pre cargados en los que se basa el robot para encontrar y darte las respuestas más precisas. 
        Al seleccionar el número de estos segmentos, estás personalizando cómo el chatbot busca la información antes de responder a tus preguntas. 
        Si escoges, por ejemplo, tres segmentos; el chatbot buscará los tres fragmentos de texto que contengan la información que sea más pertinente para responder a tu pregunta.
        ¡Pruébalo tu mismo! 🤝
         ''',unsafe_allow_html=True)

k_value = st.sidebar.select_slider('Segmentos de texto a recuperar', options=[1,2,3,4,5], value=3)

if k_value:
    question = st.chat_input("Escribe tu pregunta aquí")
    vector_db = get_vdb()
    conversation_chain = qa_chain(vector_db,k_value)
    memory = load_memory(st)
    
    if question:
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
            

st.sidebar.button('Limpiar historial del chat', on_click=reset_conversation)