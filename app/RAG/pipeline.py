import chromadb
from sentence_transformers import SentenceTransformer
import anthropic
import os
from dotenv import load_dotenv
from pathlib import Path


# =========================
# ENV
# =========================

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)


# =========================
# VECTOR DATABASE
# =========================

chroma_path = Path(__file__).resolve().parent / "chroma_db"

client = chromadb.PersistentClient(
    path=str(chroma_path)
)

collection = client.get_collection(
    name="techstore"
)


# =========================
# EMBEDDING MODEL
# =========================

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# =========================
# CLAUDE
# =========================

claude = anthropic.Anthropic(
    api_key=os.getenv("AI_API_KEY")
)


# =========================
# CONVERSATION MEMORY
# =========================

conversation_history = {}


# =========================
# RAG FUNCTION
# =========================

def ask_rag(query, session_id="default"):

    # Creăm memoria pentru sesiune
    if session_id not in conversation_history:
        conversation_history[session_id] = []

    history = conversation_history[session_id]

    # Transformăm întrebarea în embedding
    query_embedding = embedding_model.encode(
        query
    ).tolist()

    # Căutăm informația relevantă
    # Pentru întrebări despre întregul catalog
    catalog_keywords = [
        "ce laptopuri",
        "ce telefoane",
        "ce produse",
        "toate produsele",
        "aratami toate",
        "arată-mi toate",
        "ce aveti",
        "ce aveți"
    ]

    is_catalog_question = any(
        keyword in query.lower()
        for keyword in catalog_keywords
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=35 if is_catalog_question else 8,
        include=["documents"]
    )

    # Combinăm informațiile găsite
    context = "\n\n".join(
        results["documents"][0]
    )

    # Construim istoricul conversației
    previous_messages = []

    for message in history:
        previous_messages.append({
            "role": message["role"],
            "content": message["content"]
        })

    # Adăugăm întrebarea actuală
    previous_messages.append({
        "role": "user",
        "content": f"""
CONTEXT:
{context}

ÎNTREBARE:
{query}
"""
    })

    # Trimitem către Claude
    response = claude.messages.create(
        model=os.getenv(
            "AI_MODEL",
            "claude-sonnet-4-6"
        ),
        max_tokens=1500,
        system=(
            "Ești un asistent pentru magazinul TechStore. "
            "Folosește informațiile din CONTEXT și istoricul conversației. "
            "Nu inventa informații. "
            "Dacă informația nu se află în CONTEXT, "
            "spune clar că nu ai această informație."
        ),
        messages=previous_messages
    )

    answer = response.content[0].text.strip()

    # Salvăm conversația
    history.append({
        "role": "user",
        "content": query
    })

    history.append({
        "role": "assistant",
        "content": answer
    })

    return answer