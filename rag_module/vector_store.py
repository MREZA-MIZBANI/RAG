import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DB_DIR = os.path.join(BASE_DIR, 'data', 'vector_db')



def get_embeddings_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")



def add_documents_to_vectorstore(chunks):
    embeddings = get_embeddings_model()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR,
        collection_name="legaltexts_rag_collection"
    )
    return vectorstore






def get_retriever():
    embeddings = get_embeddings_model()
    vectorstore = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embeddings,
        collection_name="legaltexts_rag_collection",
        collection_metadata={"hnsw:space": "cosine"}
    )
    
    return vectorstore.as_retriever(search_kwargs={"k": 4})