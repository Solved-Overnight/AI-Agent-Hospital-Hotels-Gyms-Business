from pathlib import Path 

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.tools import tool

# crearing the RAG (Retrieval-Augmented Generation) pipeline.

BASE_DIR = Path(__file__).resolve().parent
VECTOR_DB_DIR = BASE_DIR / "vector_db"

embeddings = HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = Chroma(
    collection_name = "clinic_knowledge",
    embedding_function = embeddings,
    persist_directory = str(VECTOR_DB_DIR)
)

retriever = vector_store.as_retriever(
    search_kwargs = {"k":3}
)

# turning the retriever into an agent tool
@tool
def search_clinic_knowledge(query: str) -> str:
    """Search the BrightSmile Dental Clinic knowledge base for clinic-specific information."""

    documents = retriever.invoke(query)

    if not documents:
        return "No relevant clinic information was found."

    results = []

    for document in documents:
        results.append(document.page_content)

    return "\n\n---\n\n".join(results)
