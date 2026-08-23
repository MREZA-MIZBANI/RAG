import os
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .vector_store import get_retriever

def delete_doc_chunks_from_chroma(doc_id: int):
    try:
        retriever = get_retriever()
        vectorstore = retriever.vectorstore
        vectorstore.delete(where={"doc_id": str(doc_id)})
    except Exception as e:
        print(f"خطا در پاک‌سازی چانک‌های ChromaDB: {e}")

def process_docx_and_store(file_path: str, doc_id: int):
    if not os.path.exists(file_path):
        return None

    loader = Docx2txtLoader(file_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)

    full_text = ""
    for chunk in chunks:
        chunk.metadata["doc_id"] = str(doc_id)
        full_text += chunk.page_content + "\n"

    retriever = get_retriever()
    vectorstore = retriever.vectorstore
    vectorstore.add_documents(chunks)

    return full_text