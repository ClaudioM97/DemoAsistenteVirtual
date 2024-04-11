"""
rag.py

This module provides functionalities for building and querying a vector database using ChromaDB.
It handles operations like loading PDFs, chunking text, embedding, and retrieving documents based on queries.
"""

import os
import uuid
from typing import List, Any
import chromadb
import chromadb.config
import numpy as np
from PyPDF2 import PdfReader
from sentence_transformers import CrossEncoder
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter
)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def build_vector_database(chunk_size: int, chunk_overlap: int, embedding_model: Any) -> chromadb.Collection:
    """
    Builds a vector database from a PDF file by splitting the text into chunks and embedding them.
    
    Args:
        file: The PDF file to process.
        chunk_size: The number of tokens in one chunk.
        chunk_overlap: The number of tokens shared between consecutive chunks.
    
    Returns:
        A Chroma collection object containing the embedded chunks.
    """
    txt_texts = load_txt_clean()
    #pdf_texts = _load_pdf(file)
    character_split_texts = _split_text_into_chunks(txt_texts, chunk_size, chunk_overlap)
    token_split_texts = _split_chunks_into_tokens(character_split_texts)
    chroma_collection = _create_and_populate_chroma_collection(token_split_texts, embedding_model)
    return chroma_collection

def _split_text_into_chunks(pdf_texts: List[str], chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    Splits the text from a PDF into chunks based on character count.
    
    Args:
        pdf_texts: List of text extracted from PDF pages.
        chunk_size: The number of tokens in one chunk.
        chunk_overlap: The number of tokens shared between consecutive chunks.
    
    Returns:
        A list of text chunks.
    """
    character_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return character_splitter.split_text('\n\n'.join(pdf_texts))

def _split_chunks_into_tokens(character_split_texts: List[str]) -> List[str]:
    """
    Splits text chunks into smaller chunks based on token count.
    
    Args:
        character_split_texts: List of text chunks split by character count.
    
    Returns:
        A list of text chunks split by token count.
    """
    token_splitter = SentenceTransformersTokenTextSplitter(chunk_overlap=0, tokens_per_chunk=256)
    return [text for chunk in character_split_texts for text in token_splitter.split_text(chunk)]

def _create_and_populate_chroma_collection(token_split_texts: List[str], embedding_model) -> chromadb.Collection:
    """
    Creates a Chroma collection and populates it with the given text chunks.
    
    Args:
        token_split_texts: List of text chunks split by token count.
    
    Returns:
        A Chroma collection object populated with the text chunks.
    """
    chroma_client = chromadb.Client()
    document_name = uuid.uuid4().hex
    chroma_collection = chroma_client.create_collection(document_name, embedding_function=embedding_model)
    ids = [str(i) for i in range(len(token_split_texts))]
    chroma_collection.add(ids=ids, documents=token_split_texts)
    return chroma_collection

def query_chroma(chroma_collection: chromadb.Collection, query: str, top_k: int) -> List[str]:
    """
    Queries the Chroma collection for the top_k most relevant chunks to the input query.
    
    Args:
        chroma_collection: The Chroma collection to query.
        query: The input query string.
        top_k: The number of top results to retrieve.
    
    Returns:
        A list of retrieved chunk IDs.
    """
    results = chroma_collection.query(query_texts=[query], n_results=top_k)
    retrieved_id = results['ids'][0]
    return retrieved_id

def get_doc_embeddings(chroma_collection: chromadb.Collection) -> np.ndarray:
    """
    Retrieves the document embeddings from the Chroma collection.
    
    Args:
        chroma_collection: The Chroma collection to retrieve embeddings from.
    
    Returns:
        An array of embeddings.
    """
    embeddings = chroma_collection.get(include=['embeddings'])['embeddings']
    return embeddings

def get_docs(chroma_collection: chromadb.Collection) -> List[str]:
    """
    Retrieves the documents from the Chroma collection.
    
    Args:
        chroma_collection: The Chroma collection to retrieve documents from.
    
    Returns:
        A list of documents.
    """
    documents = chroma_collection.get(include=['documents'])['documents']
    metadata = chroma_collection.get()['metadatas']
    documentos_modificados = []
    
    for document, metadata in zip(documents, metadata):
        documento_modificado = f"{document}\n\nFuente: {metadata['source']}"
        #document_modificado = document + '\n\n' + source_info
        documentos_modificados.append(documento_modificado)
        
    return documentos_modificados


def _load_pdf(file: Any) -> List[str]:
    """
    Loads and extracts text from a PDF file.
    
    Args:
        file: The PDF file to load.
    
    Returns:
        A list of strings, each representing the text of a page.
    """
    pdf = PdfReader(file)
    pdf_texts = [p.extract_text().strip() for p in pdf.pages if p.extract_text()]
    return pdf_texts

def load_txt_clean():
    ruta_carpeta = '/Users/claudiomontiel/Desktop/Proyectos VS/PruebaStreamlit/archivos_clean'
    contenidos_archivos = []
    archivos = os.listdir(ruta_carpeta)
    for archivo in archivos:
        ruta_completa = os.path.join(ruta_carpeta, archivo)
        with open(ruta_completa, 'r', encoding='utf-8') as archivo_abierto:
            contenido = archivo_abierto.read()
            contenidos_archivos.append(contenido)
    
    return contenidos_archivos
 
def get_collection():
    chroma_client = chromadb.PersistentClient(path="../chroma_final")
    collection = chroma_client.get_or_create_collection('docs_publicos')
    return collection
     
def get_chunks_relevants(query,top_docs,collection):
    coleccion = collection
    results = coleccion.query(query_texts=query, n_results=100, include=['documents', 'embeddings'])
    retrieved_documents = results['documents'][0]
    retrieved_documents_ids = results['ids'][0]
    
    cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    pairs = [[query, doc] for doc in retrieved_documents]
    scores = cross_encoder.predict(pairs)
    
    pares_docs_scores = list(zip(retrieved_documents_ids,scores))
    pares_docs_scores_sorted = sorted(pares_docs_scores, key=lambda x: x[1],reverse=True)
    top_k_ids = [par[0] for par in pares_docs_scores_sorted[:top_docs]]
    nueva_coleccion = coleccion.get(ids=top_k_ids,include=['documents','embeddings','metadatas'])
    
    return nueva_coleccion

def coleccion(dict):
    client = chromadb.Client()
    collection = client.get_or_create_collection(name="my_collection")
    collection.add(documents=dict['documents'],embeddings=dict['embeddings'],
                   metadatas=dict['metadatas'],
                   ids=dict['ids'])
    return collection

def get_docs_2(dict) -> List[str]:
    """
    Retrieves the documents from the Chroma collection.
    
    Args:
        chroma_collection: The Chroma collection to retrieve documents from.
    
    Returns:
        A list of documents.
    """
    documents = dict['documents']
    metadata = dict['metadatas']
    documentos_modificados = []
    
    for document, metadata in zip(documents, metadata):
        documento_modificado = f"{document}\n\nFuente: {metadata['source']}"
        #document_modificado = document + '\n\n' + source_info
        documentos_modificados.append(documento_modificado)
        
    return documentos_modificados