from langchain_community.embeddings import HuggingFaceEmbeddings


# Small, fast, good-quality sentence embeddings


def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")