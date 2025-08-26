import os
from dotenv import load_dotenv


load_dotenv()


QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "hybrid_collection")


# langchain-google-genai reads GOOGLE_API_KEY by default
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")


def assert_config():
    missing = []
    for k, v in {
        "QDRANT_URL": QDRANT_URL,
        "QDRANT_API_KEY": QDRANT_API_KEY,
        "GOOGLE_API_KEY": GOOGLE_API_KEY,
}.items():
        if not v:
            missing.append(k)
            if missing:
                raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")