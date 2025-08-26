from typing import List
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from src.embeddings import get_embeddings
from src.config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION

# -------------------------------
# Qdrant client (singleton)
# -------------------------------
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=120)

# -------------------------------
# Reset collection (optional)
# -------------------------------
def reset_qdrant_collection():
    """Delete old collection so we can re-ingest fresh docs."""
    try:
        client.delete_collection(QDRANT_COLLECTION)
        print(f"✅ Deleted old Qdrant collection: {QDRANT_COLLECTION}")
    except Exception as e:
        print(f"⚠️ Could not delete collection (maybe it doesn't exist yet): {e}")

# -------------------------------
# Get Qdrant store
# -------------------------------
def get_qdrant_store() -> Qdrant:
    """Return Qdrant store object connected to the collection.
    Creates the collection if it does not exist.
    """
    # Check if collection exists
    try:
        client.get_collection(QDRANT_COLLECTION)
    except Exception:
        # Collection missing → create it
        embedding_dim = len(get_embeddings().embed_query("test"))  # fix AttributeError
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE)
        )
        print(f"✅ Created new Qdrant collection: {QDRANT_COLLECTION}")

    return Qdrant(
        client=client,
        collection_name=QDRANT_COLLECTION,
        embeddings=get_embeddings()
    )

# -------------------------------
# Upsert batch of texts (append)
# -------------------------------
def upsert_texts(texts: List[str]) -> None:
    """Append a batch of texts to Qdrant collection."""
    if not texts:
        return
    store = get_qdrant_store()
    store.add_texts(texts)
