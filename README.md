
# 🤖 Hybrid RAG (Structured + Unstructured) Streamlit App

## Description
This project is a **hybrid retrieval-augmented generation (RAG) system** that allows users to ask natural language questions over both **structured** (CSV/Excel) and **unstructured** (PDF, TXT, images) documents.  

The app combines **SQL-based querying** for structured data with **vector search using Qdrant** for unstructured text, creating a **single interface** for hybrid information retrieval.

---

## Features

1. **Structured Data Handling**  
   - Upload CSV or Excel files.  
   - Data is loaded into an **SQLite database**.  
   - Natural language questions are converted to SQL using a text-to-SQL chain.  
   - Returns query results in a table format.

2. **Unstructured Data Handling**  
   - Upload PDFs, TXT files, or images.  
   - PDF/TXT → text chunks automatically extracted.  
   - Images → OCR (via pytesseract) extracts text.  
   - Chunks are stored in **Qdrant vector database** with embeddings and metadata (file name, chunk index).  

3. **Hybrid Q&A**  
   - Queries can retrieve results from **both structured and unstructured sources**.  
   - Uses **RAG (retriever + LLM)** to answer questions based on vector similarity.  
   - Returns SQL results for structured data and generated answers from unstructured data.

4. **Metadata Tracking**  
   - Each text chunk in Qdrant is stored with metadata: `source_file` and `chunk_index`.  
   - Enables filtering, deleting, or tracing answers back to their source.

5. **Streamlit Interface**  
   - Intuitive file uploader and input box for questions.  
   - Displays SQL queries, structured tables, and answers from unstructured data.  
   - Shows progress for file ingestion.

---

## Tech Stack

- **Frontend:** Streamlit  
- **Structured Data:** SQLite, pandas  
- **Unstructured Data:** PDFs/TXT/images, pytesseract OCR  
- **Vector Database:** Qdrant  
- **RAG & NLP:** Custom retriever + chain for natural language queries  
- **Embeddings:** 384-dimensional vectors, cosine similarity  

---

## Getting Started

1. **Clone the repository**

```bash
git clone https://github.com/your-username/hybrid-rag-app.git
cd hybrid-rag-app
