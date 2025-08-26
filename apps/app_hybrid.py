import streamlit as st
import pandas as pd
from src.config import assert_config
from src.ingestion.pdf_ingest import pdf_to_chunks
from src.vectorstores.qdrant_store import get_qdrant_store
from src.chains.rag_docs import build_rag_chain
from src.ingestion.csv_to_sqlite import load_csv_to_sqlite, get_table_schema
from src.chains.sql_qa import run_text_to_sql

# Optional OCR for images
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Streamlit Page Config
st.set_page_config(page_title="Hybrid RAG", page_icon="🤖", layout="wide")
st.title("🤖 Hybrid RAG (Structured + Unstructured)")

# Ensure API keys / configs
assert_config()

# File uploaders
col1, col2 = st.columns(2)
with col1:
    unstructured_files = st.file_uploader(
        "Upload PDFs / Images / TXT", 
        type=["pdf", "jpg", "jpeg", "png", "txt"], 
        accept_multiple_files=True
    )
with col2:
    structured_file = st.file_uploader(
        "Upload CSV/Excel", 
        type=["csv", "xlsx"]
    )

# Initialize variables
qa, retriever, conn, schema = None, None, None, None

# Settings
BATCH_SIZE = 50
MAX_CHUNKS_PER_FILE = 500

# -------------------------------
# Structured ingestion → SQLite
# -------------------------------
if structured_file is not None:
    if structured_file.name.lower().endswith(".xlsx"):
        df = pd.read_excel(structured_file)
        structured_file = df.to_csv(index=False).encode()

    conn, table = load_csv_to_sqlite(structured_file, table_name="data_table")
    schema = get_table_schema(conn, table)

    st.success("✅ CSV/Excel loaded into SQLite")
    st.code(schema, language="sql")

# -------------------------------
# Unstructured ingestion → Qdrant (append mode)
# -------------------------------
# -------------------------------
# Unstructured ingestion → Qdrant (append mode)
# -------------------------------
if unstructured_files:
    all_chunks = []
    all_metadatas = []  # Store metadata for each chunk

    for f in unstructured_files:
        name = f.name.lower()
        chunks = []

        # PDF/TXT → chunk text
        if name.endswith(".pdf") or name.endswith(".txt"):
            chunks = pdf_to_chunks(f)

        # Images → OCR text
        elif name.endswith((".jpg", ".jpeg", ".png")):
            if OCR_AVAILABLE:
                image = Image.open(f)
                text = pytesseract.image_to_string(image)
                if text.strip():
                    chunks = [text]
            else:
                st.warning(f"OCR not installed. Skipping image: {f.name}")

        # Limit chunks per file
        chunks = chunks[:MAX_CHUNKS_PER_FILE]
        all_chunks.extend(chunks)

        # Create metadata for each chunk
        for idx, _ in enumerate(chunks):
            all_metadatas.append({
                "source_file": f.name,
                "chunk_index": idx
            })

    if all_chunks:
        # Get store (auto-creates collection if missing)
        store = get_qdrant_store()

        # Batch insert → append to existing collection with metadata
        for i in range(0, len(all_chunks), BATCH_SIZE):
            batch_texts = all_chunks[i:i+BATCH_SIZE]
            batch_metadatas = all_metadatas[i:i+BATCH_SIZE]
            store.add_texts(batch_texts, metadatas=batch_metadatas)
            st.progress(min((i + BATCH_SIZE) / len(all_chunks), 1.0))

        retriever = store.as_retriever(search_kwargs={"k": 4})
        qa = build_rag_chain(retriever)
        st.success(f"✅ {len(all_chunks)} chunks added to Qdrant (unstructured files)")

      

# -------------------------------
# Ask question
# -------------------------------
q = st.text_input("Ask a question (works for both structured + unstructured files):")

if q:
    with st.spinner("Thinking…"):
        # SQL only
        if conn and schema and not qa:
            try:
                result = run_text_to_sql(q, schema, conn)
                st.caption("Generated SQL")
                st.code(result["sql"], language="sql")
                if result["rows"]:
                    df = pd.DataFrame(result["rows"], columns=result["columns"])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No rows returned.")
            except Exception as e:
                st.error(f"SQL Error: {e}")

        # Vector only
        elif qa and not conn:
            ans = qa.run(q)
            st.markdown(f"### Answer\n{ans}")

        # Hybrid: SQL + vector
        elif qa and conn:
            sql_result, vector_result = None, None

            # SQL
            try:
                sql_result = run_text_to_sql(q, schema, conn)
            except:
                pass

            # Vector
            try:
                vector_result = qa.run(q)
            except:
                pass

            # Display results
            if sql_result:
                st.subheader("SQL Result")
                st.code(sql_result["sql"], language="sql")
                if sql_result["rows"]:
                    df = pd.DataFrame(sql_result["rows"], columns=sql_result["columns"])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No SQL rows returned.")

            if vector_result:
                st.subheader("Unstructured Answer")
                st.markdown(vector_result)

        else:
            st.warning("Please upload at least one structured or unstructured file first.")
