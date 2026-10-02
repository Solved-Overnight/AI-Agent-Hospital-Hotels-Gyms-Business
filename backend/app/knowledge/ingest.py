from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader

# Creating the embedding and vector database pipeline.
# The ingestion script creats the Vector Embedding and Vector Database for the clinic knowledge base.

BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "documents"
VECTOR_DB_DIR = BASE_DIR / "vector_db"

def ingest_documents():

    print("Loading clinic documents...")

    loader = DirectoryLoader(
        str(DOCUMENTS_DIR),
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )

    documents = loader.load()

    print(f"Loaded {len(documents)} documents.")

    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50,
    )

    chunks = text_splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    # Local embedding model
    embeddings = HuggingFaceEmbeddings(
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Creating vector database...")

    # Create a Chroma vector database
    vector_store = Chroma(
        collection_name = "clinic_knowledge",
        embedding_function = embeddings,
        persist_directory = str(VECTOR_DB_DIR),
    )


    vector_store.add_documents(chunks)
    print("Clinic knowledge base created successfully.")


if __name__ == "__main__":
    ingest_documents()


