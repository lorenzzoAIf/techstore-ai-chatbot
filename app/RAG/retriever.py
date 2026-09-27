import chromadb
from sentence_transformers import SentenceTransformer


# Conectăm la vector database
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_collection(
    name="techstore"
)

# Modelul pentru embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")


# Întrebarea utilizatorului
query = "Cât costă laptopul ASUS TUF A18?"


# Transformăm întrebarea în embedding
query_embedding = model.encode(query).tolist()


# Căutăm informația relevantă
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=1
)


# Afișăm rezultatul
print("Întrebarea:", query)
print("\nInformația găsită:")
print(results["documents"][0][0])