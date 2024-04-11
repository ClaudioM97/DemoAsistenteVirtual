from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import Chroma
import chromadb
import chromadb.config
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain_community.document_loaders import TextLoader
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationSummaryMemory
from langchain.memory import ConversationBufferMemory
from langchain.memory import ConversationBufferWindowMemory
from unstructured.cleaners.core import clean
import pytesseract 
from unidecode import unidecode
from pdf2image import convert_from_bytes
import os
import streamlit as st
from langchain_openai import ChatOpenAI

@st.cache_data
def extract_text_from_pdf(uploaded_pdf):
    images = convert_from_bytes(uploaded_pdf.getvalue())
    ocr_text_list = []
    for i, image in enumerate(images):
        page_content = pytesseract.image_to_string(image)
        page_content = '***PDF Page {}***\n'.format(i+1) + page_content
        ocr_text_list.append(page_content)
    ocr_text = ' '.join(ocr_text_list)
    return ocr_text

@st.cache_data
def extract_text_from_pdf_2(uploaded_pdf):
    images = convert_from_bytes(uploaded_pdf)
    ocr_text_list = []
    for i, image in enumerate(images):
        page_content = pytesseract.image_to_string(image)
        page_content = '***PDF Page {}***\n'.format(i+1) + page_content
        ocr_text_list.append(page_content)
    ocr_text = ' '.join(ocr_text_list)
    return ocr_text

@st.cache_data
def clean_text(ocr_text_from_pdf):
    return clean(ocr_text_from_pdf,extra_whitespace=True,trailing_punctuation=True,lowercase=True)

@st.cache_data
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap = 100,
        separators=["\n\n", "\n", "(?<=\. )", " ", ""])
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings(model = 'text-embedding-3-small')
    #vectorstore = Chroma.from_documents(text_chunks, embeddings)
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


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

@st.cache_resource
def get_conversation_chain(text_chunks):
    embeddings = OpenAIEmbeddings(model = 'text-embedding-3-small')
    vectorstore = Chroma.from_texts(text_chunks, embeddings)
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
        llm=ChatOpenAI(model_name='gpt-3.5-turbo-0125', temperature=0),
        retriever=vectorstore.as_retriever(search_type = 'mmr'),
        condense_question_llm=ChatOpenAI(model_name="gpt-3.5-turbo-0125"),
        condense_question_prompt=QA_CHAIN_PROMPT
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
    embeddings = OpenAIEmbeddings(model = 'text-embedding-3-large')
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
        llm=ChatOpenAI(model_name='gpt-3.5-turbo-0125', temperature=0),
        retriever=vectordb.as_retriever(search_type = 'mmr',search_kwargs={"k": k}),
        #condense_question_llm=ChatOpenAI(model_name="gpt-3.5-turbo-0125"),
        condense_question_prompt=QA_CHAIN_PROMPT
    )
    return conversation_chain
    
    
def reset_conversation():
    st.session_state['messages'] = [
        {"role": "assistant", 
         "content": "El historial del chat ha sido limpiado. ¿Cómo puedo asistirte ahora? 😊"}
    ]
    
