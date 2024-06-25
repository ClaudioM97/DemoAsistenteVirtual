from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import Chroma
import chromadb
import chromadb.config
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain_community.document_loaders import TextLoader
from langchain.prompts import PromptTemplate
from langchain.prompts import PromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.memory import ConversationSummaryMemory
from langchain.memory import ConversationBufferMemory
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.document_loaders import PyPDFLoader
from unstructured.cleaners.core import clean
import pytesseract 
from unidecode import unidecode
from pdf2image import convert_from_bytes
import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai import AzureChatOpenAI

modelo = AzureChatOpenAI(api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                        azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
                        api_version="2024-02-15-preview",
                        temperature=0)

embeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv('AZURE_DEPLOYMENT'),
        openai_api_version=os.getenv("API_VERSION_GPT3"),
        api_key=os.getenv("OPENAI_APIKEY_GPT3"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_GPT3")
    )


general_system_template = f'''
Eres un asistente virtual de un director empresarial, es decir, miembro del directorio de varias empresas. Debes responder de manera concisa y precisa, las preguntas que tenga sobre distintos tipos de documentos tales como:
informes financieros, reportes empresariales, memorias anuales, articulos, y cualquier otro que sea relevante para un director empresarial en su gestion.

Responde la pregunta del final, utilizando solo el siguiente contexto (delimitado por <context></context>).
Si no sabes la respuesta, menciona explicitamente que no la sabes de manera educada y cordial.
<context>
{{chat_history}}

{{context}} 
</context>
'''

general_user_template = "Question:```{question}```"
messages = [
            SystemMessagePromptTemplate.from_template(general_system_template),
            HumanMessagePromptTemplate.from_template(general_user_template)
]
qa_prompt = ChatPromptTemplate.from_messages(messages)


def extract_text(uploaded_pdf):
    loader = PyPDFLoader(uploaded_pdf)
    pages = loader.load()
    text = ""

    for page in pages:
        text += page.page_content
    
    text = text.replace('\t', ' ')

    return text


def clean_text(ocr_text_from_pdf):
    return clean(ocr_text_from_pdf,extra_whitespace=True,trailing_punctuation=True,lowercase=True)


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap = 100,
        separators=["\n\n", "\n", "(?<=\. )", " ", ""])
    chunks = text_splitter.split_text(text)
    return chunks


def load_memory(st):
    memory = ConversationBufferWindowMemory(k=3, return_messages=True)
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "¡Bienvenido! 👨🏻‍💻 soy tu asistente virtual. ¿En qué puedo ayudarte? 😊"}
        ]
    for index, msg in enumerate(st.session_state.messages):
        st.chat_message(msg["role"]).write(msg["content"])
        if msg["role"] == "user" and index < len(st.session_state.messages) - 1:
            memory.save_context(
                {"input": msg["content"]},
                {"output": st.session_state.messages[index + 1]["content"]},
            )

    return memory


def get_conversation_chain(text_chunks):
    #embeddings = OpenAIEmbeddings(model = 'text-embedding-3-small')
    embeddingss = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv('AZURE_DEPLOYMENT'),
        openai_api_version=os.getenv("API_VERSION_GPT3"),
        api_key=os.getenv("OPENAI_APIKEY_GPT3"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_GPT3")
    )
    vectorstore = Chroma.from_texts(text_chunks, embeddingss)
    #vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    
    template = """
    Dado un historial de conversacion, reformula la pregunta para hacerla mas facil de buscar en una base de datos.
    Por ejemplo, si la IA dice "¿Quieres saber el clima actual en Estambul?", y el usuario responde "si", entonces la IA deberia reformular la pregunta como "¿Cual es el clima actual en Estambul?".
    No debes cambiar el idioma de la pregunta, solo reformularla. Si no es necesario reformular la pregunta o si no es una pregunta, simplemente muestra el mismo texto

    ### Historial de conversación ###
    {chat_history}
    Ultimo mensaje: {question}
    Pregunta reformulada:
    """
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
        
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=modelo,
        #llm=ChatOpenAI(model_name='gpt-3.5-turbo-0125', temperature=0),
        retriever=vectorstore.as_retriever(search_type = 'mmr'),
        condense_question_llm=modelo,
        #condense_question_llm=ChatOpenAI(model_name="gpt-3.5-turbo-0125"),
        condense_question_prompt=QA_CHAIN_PROMPT,
        combine_docs_chain_kwargs={'prompt': qa_prompt}
    )
    return conversation_chain


def remove_accents(input_str):
    return unidecode(input_str)

def filter_fichas(data, search_term):
    search_term = remove_accents(search_term.lower())
    filtered_fichas = []
    for ficha in data:
        if (search_term in remove_accents(ficha['Título'].lower()) or
            search_term in remove_accents(ficha['Autor'].lower()) or
            search_term in remove_accents(ficha['Keywords'].lower())):
            filtered_fichas.append(ficha)
    return filtered_fichas

@st.cache_data
def display_in_pairs(data):
    num_columns = len(data)
    num_pairs = num_columns // 2
    remainder = num_columns % 2

    columns = st.columns(2)
    
    for i in range(num_pairs):
        with columns[0]:
            with st.expander(data[i]['Título']):
                for key, value in data[i].items():
                    st.write(f"{key}: {value}")
        with columns[1]:
            with st.expander(data[num_pairs + i]['Título']):
                for key, value in data[num_pairs + i].items():
                    st.write(f"{key}: {value}")

    if remainder == 1:
        with columns[0]:
            with st.expander(data[-1]['Título']):
                for key, value in data[-1].items():
                    st.write(f"{key}: {value}")
                    
#@st.cache_resource
def get_vdb():
    #persist_directory = '/Users/claudiomontiel/Desktop/Proyectos VS/PruebaStreamlit/chroma_st'
    #embeddings = OpenAIEmbeddings(model = 'text-embedding-3-large')
    vectordb = Chroma(persist_directory="chroma_st",
                      embedding_function=embeddings)
    return vectordb
    


def qa_chain(vectordb,k):
    template = """
    Dado un historial de conversacion, reformula la pregunta para hacerla mas facil de buscar en una base de datos.
    Por ejemplo, si la IA dice "¿Quieres saber el clima actual en Estambul?", y el usuario responde "si", entonces la IA deberia reformular la pregunta como "¿Cual es el clima actual en Estambul?".
    No debes cambiar el idioma de la pregunta, solo reformularla. Si no es necesario reformular la pregunta o si no es una pregunta, simplemente muestra el mismo texto

    ### Historial de conversación ###
    {chat_history}
    Ultimo mensaje: {question}
    Pregunta reformulada:
    """
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
        
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=modelo,
        #llm=ChatOpenAI(model_name='gpt-3.5-turbo-0125', temperature=0),
        retriever=vectordb.as_retriever(search_type = 'mmr',search_kwargs={"k": k}),
        condense_question_llm=modelo,
        #condense_question_llm=ChatOpenAI(model_name="gpt-3.5-turbo-0125"),
        condense_question_prompt=QA_CHAIN_PROMPT,
        combine_docs_chain_kwargs={'prompt': qa_prompt}
    )
    return conversation_chain
    
    
def reset_conversation():
    st.session_state['messages'] = [
        {"role": "assistant", 
         "content": "El historial del chat ha sido limpiado. ¿Cómo puedo asistirte ahora? 😊"}
    ]
    
