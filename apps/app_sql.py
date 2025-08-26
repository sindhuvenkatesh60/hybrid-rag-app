import streamlit as st
import pandas as pd
from src.config import assert_config
from src.ingestion.csv_to_sqlite import load_csv_to_sqlite, get_table_schema
from src.chains.sql_qa import run_text_to_sql

st.set_page_config(page_title="SQL QA", page_icon="🗄️", layout="wide")
st.title("🗄️ Text-to-SQL QA")

assert_config()

conn, schema = None, None

uploaded_table = st.file_uploader("Upload CSV/Excel", type=["csv", "xlsx"])

if uploaded_table is not None:
    if uploaded_table.name.lower().endswith(".xlsx"):
        df = pd.read_excel(uploaded_table)
        uploaded_table = df.to_csv(index=False).encode()

    conn, table = load_csv_to_sqlite(uploaded_table, table_name="data_table")
    schema = get_table_schema(conn, table)

    st.success("✅ Table loaded into SQLite (fresh)")
    st.code(schema, language="sql")

q = st.text_input("Ask a question about the table:")

if q and conn and schema:
    with st.spinner("Thinking…"):
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
