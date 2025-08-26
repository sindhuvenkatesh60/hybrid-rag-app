import re
import sqlite3
from typing import Any, Dict
from src.llm.gemini import get_llm

SQL_SYSTEM_PROMPT = (
    "You are an expert SQLite analyst.\n"
    "Given a user's request and the table schema, respond with ONLY a valid SQLite SELECT query.\n"
    "Do NOT include explanations or code fences.\n"
    "Never modify data. No DDL or DML. No DROP/DELETE/UPDATE/INSERT."
)

def extract_sql(text: str) -> str:
    """Cleans and validates the SQL query returned by the LLM."""
    # Remove code fences if the model returns ```sql ... ```
    text = re.sub(r"```(?:sql)?", "", text, flags=re.IGNORECASE).strip()
    # Keep only the first statement and ensure it's SELECT
    stmt = text.split(";")[0]
    if not stmt.lower().strip().startswith("select"):
        raise ValueError(f"Generated non-SELECT statement: {stmt}")
    return stmt + ";"

def run_text_to_sql(question: str, schema: str, conn: sqlite3.Connection) -> Dict[str, Any]:
    """Converts natural language into SQL, executes it, and returns results."""
    llm = get_llm()
    prompt = f"{SQL_SYSTEM_PROMPT}\n\nSCHEMA:\n{schema}\n\nQUESTION:\n{question}\n\nSQL:"
    sql = extract_sql(llm.invoke(prompt).content)

    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description] if cur.description else []
    return {"sql": sql, "columns": cols, "rows": rows}
