from typing import Literal

AGG_KEYWORDS = {
    "sum", "total", "count", "average", "avg", "mean", "median", "max", "min",
    "group by", "top", "highest", "lowest", "difference", "trend"
}

def route(question: str) -> Literal["sql", "vector", "both"]:
    """
    Simple query router:
    - If the question contains aggregation/statistical keywords → send to SQL
    - Otherwise → send to vector (RAG / PDFs)
    """
    q = question.lower()
    if any(k in q for k in AGG_KEYWORDS):
        return "sql"
    return "vector"
