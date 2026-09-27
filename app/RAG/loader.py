from pypdf import PdfReader
from app.RAG.chunker import chunk_text

pdf_path = "../../documents/techstore_knowledgedocument.pdf"

reader = PdfReader(pdf_path)

text = ""

for page in reader.pages:
    text += page.extract_text() + "\n"

chunks = chunk_text(text)

print("Număr de pagini:", len(reader.pages))
print("Număr de chunks:", len(chunks))

for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i + 1} ---")
    print(chunk)