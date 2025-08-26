import streamlit as st
from src.config import assert_config
from src.ingestion.pdf_ingest import pdf_to_chunks
from src.vectorstores.qdrant_store import upsert_texts, reset_qdrant_collection
from src.chains.rag_docs import build_rag_chain

# Streamlit Page Config
st.set_page_config(page_title="Docs RAG", page_icon="📘", layout="wide")
st.title("📘 RAG on Documents")

# Ensure API keys / configs
assert_config()

qa, retriever = None, None

# PDF Upload
uploaded_pdfs = st.file_uploader(
    "Upload PDFs", type=["pdf"], accept_multiple_files=True
)

if uploaded_pdfs:
    reset_qdrant_collection()   # always reset collection
    
    all_chunks = []
    for f in uploaded_pdfs:
        all_chunks.extend(pdf_to_chunks(f))
    
    # Make sure upsert_texts returns a Qdrant instance
    store = upsert_texts(all_chunks)
    
    if store:
        retriever = store.as_retriever(search_kwargs={"k": 4})
        qa = build_rag_chain(retriever)
        st.success(f"✅ Indexed {len(all_chunks)} chunks in Qdrant (fresh)")
    else:
        st.error("❌ Failed to create Qdrant store. Check your embeddings or collection.")

# Ask questions
q = st.text_input("Ask a question about your documents:")

if q and qa:
    with st.spinner("Thinking…"):
        ans = qa.run(q)
        st.markdown(f"### Answer\n{ans}")
