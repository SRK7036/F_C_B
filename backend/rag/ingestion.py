import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader, CSVLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

SUPPORTED = {
    ".pdf": PyMuPDFLoader,
    ".docx": Docx2txtLoader,
    ".csv": CSVLoader,
    ".txt": TextLoader,
}

FOLDER = os.getenv("KB_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "knowledge_base"))
PERSIST_DIR = os.getenv("PERSIST_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db"))
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

def ingest_documents(folder_path: str = FOLDER, persist_dir: str = PERSIST_DIR):
    all_docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    if not os.path.isdir(folder_path):
        raise RuntimeError(f"Knowledge base folder not found: {folder_path}")

    for name in os.listdir(folder_path):
        fp = os.path.join(folder_path, name)
        if not os.path.isfile(fp):
            continue
        ext = os.path.splitext(fp)[1].lower()
        if ext not in SUPPORTED:
            print(f"[skip] Unsupported file: {name}")
            continue
        print(f"[load] {name}")
        loader = SUPPORTED[ext](fp)
        docs = loader.load()
        chunks = splitter.split_documents(docs)
        all_docs.extend(chunks)
        print(f"[ok] {len(chunks)} chunks from {name}")

    if not all_docs:
        print("No documents found to ingest.")
        return

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    db = Chroma.from_documents(all_docs, embedding=embeddings, persist_directory=persist_dir)
    db.persist()
    print(f"[done] {len(all_docs)} chunks indexed → {persist_dir}")

if __name__ == "__main__":
    ingest_documents()
