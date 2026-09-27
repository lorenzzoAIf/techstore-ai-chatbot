import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from pathlib import Path

from app.RAG.chunker import chunk_text


# =========================
# PATHS
# =========================

project_root = Path(__file__).resolve().parents[2]

pdf_path = (
    project_root
    / "documents"
    / "techstore_knowledge_35_products  sss.pdf"
)

chroma_path = (
    Path(__file__).resolve().parent
    / "chroma_db"
)


# =========================
# VECTOR DATABASE
# =========================

client = chromadb.PersistentClient(
    path=str(chroma_path)
)


# Ștergem colecția veche
try:
    client.delete_collection(
        name="techstore"
    )
except Exception:
    pass


collection = client.get_or_create_collection(
    name="techstore"
)


# =========================
# READ PDF
# =========================

reader = PdfReader(
    str(pdf_path)
)

text = ""

for page in reader.pages:
    extracted_text = page.extract_text()

    if extracted_text:
        text += extracted_text + "\n"


# =========================
# CHUNKING
# =========================

chunks = chunk_text(text)


# =========================
# EMBEDDINGS
# =========================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

embeddings = model.encode(
    chunks
)


# =========================
# SAVE TO CHROMA
# =========================

ids = [
    f"chunk_{i}"
    for i in range(len(chunks))
]

collection.add(
    ids=ids,
    documents=chunks,
    embeddings=embeddings.tolist()
)


# =========================
# RESULT
# =========================

print("Chunks salvate:", len(chunks))

print(
    "Vector database este gata!"
)

print(
    "Documente în database:",
    collection.count()
)