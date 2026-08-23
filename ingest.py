import os
from langchain_community.document_loaders import Docx2txtLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag_module.vector_store import get_retriever

DOCS_DIR = os.path.join(os.path.dirname(__file__), 'media', 'documents')

def process_documents(clear_existing: bool = True):
    print("در حال بارگذاری اسناد از پوشه media/documents...")
    
    retriever = get_retriever()
    vectorstore = retriever.vectorstore

    if clear_existing:
        try:
            existing_ids = vectorstore.get()['ids']
            if existing_ids:
                vectorstore.delete(ids=existing_ids)
                print(f"تعداد {len(existing_ids)} چانک قدیمی با موفقیت از دیتابیس پاک شدند.")
        except Exception as e:
            print(f"هشدار در پاک‌سازی داده‌های قبلی: {e}")

    documents = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if file.endswith('.docx') or file.endswith('.doc'):
                    loader = Docx2txtLoader(file_path)
                    documents.extend(loader.load())
                elif file.endswith('.pdf'):
                    loader = PyPDFLoader(file_path)
                    documents.extend(loader.load())
                elif file.endswith('.txt'):
                    loader = TextLoader(file_path, encoding='utf-8', autodetect_encoding=True)
                    documents.extend(loader.load())
            except Exception as e:
                print(f"خطا در بارگذاری فایل {file}: {e}")

    if not documents:
        print("هیچ فایل معتبری در پوشه یافت نشد!")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"تعداد کل چانک‌های تولیدشده: {len(chunks)}")

    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        try:
            vectorstore.add_documents(batch)
            print(f"دسته {i//batch_size + 1} شامل {len(batch)} چانک ذخیره شد.")
        except Exception as e:
            print(f"خطا در ذخیره‌سازی دسته {i//batch_size + 1}: {e}")

    print("عملیات با موفقیت به پایان رسید.")

if __name__ == "__main__":
    process_documents(clear_existing=True)