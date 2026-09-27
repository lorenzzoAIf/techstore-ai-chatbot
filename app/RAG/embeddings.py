from sentence_transformers import SentenceTransformer
from app.RAG.chunker import chunk_text
from pypdf import PdfReader

pdf_path = "../../documents/techstore_knowledgedocument.pdf"

reader = PdfReader(pdf_path)

text = ""

for page in reader.pages:
    text += page.extract_text() + "\n"

chunks = chunk_text(text)

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(chunks)

print("Număr chunks:", len(chunks))
print("Număr embeddings:", len(embeddings))
print("Dimensiunea unui embedding:", len(embeddings[0]))