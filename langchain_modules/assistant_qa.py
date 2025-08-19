"""
This file has code for loading PDFs from local disk, spplitting them into chunks,
converting info to embeddings and storing the embeddings in a vector store
"""
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI

from config import OPENAI_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def load_and_split_pdf(file_path):
    loader = PyPDFLoader(file_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(pages)
    print(f"Loaded and split into {len(chunks)} chunks.")
    return chunks

def embed_chunks_and_store(chunks, save_path="vector_store/"):
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    vector_store.save_local(save_path)
    print(f"Saved embeddings to {save_path}")
    return vector_store

def load_vector_store(load_path):
    """
    Load a saved FAISS vector store from disk.

    FAISS vector stores use pickle files to save metadata.
    by default, LangChain disables loading pickles unless explicitly specified with allow_dangerous_deserialization=True
    """
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.load_local(load_path, embeddings,allow_dangerous_deserialization=True)
    print(f"Loaded vector store from {load_path}")
    return vector_store


def build_qa_chain(vector_store):
    """
    Builds a Q&A chain using the loaded vector store and OpenAI's GPT model. (Using gpt 3.5 turbo)
    """
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")  

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vector_store.as_retriever(),
        return_source_documents=False  # not showing the sources 
    )
    return qa_chain


