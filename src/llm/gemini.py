from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import GOOGLE_API_KEY


# Default chat LLM
def get_llm(model: str = "gemini-1.5-flash"):
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY not set")
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2,
    )
