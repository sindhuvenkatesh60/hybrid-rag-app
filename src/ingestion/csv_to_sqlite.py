import pandas as pd
import sqlite3
from typing import Tuple




def load_csv_to_sqlite(file_like, table_name: str = "data_table") -> Tuple[sqlite3.Connection, str]:
    df = pd.read_csv(file_like)
    conn = sqlite3.connect(":memory:")
    df.to_sql(table_name, conn, index=False, if_exists="replace")
    return conn, table_name




def get_table_schema(conn: sqlite3.Connection, table_name: str) -> str:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table_name});")
    cols = cur.fetchall()
    # cols: cid, name, type, notnull, dflt_value, pk
    schema = ", ".join([f"{c[1]} {c[2] or ''}".strip() for c in cols])
    return f"CREATE TABLE {table_name} ({schema});"