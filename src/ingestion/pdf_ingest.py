from PyPDF2 import PdfReader
from src.utils.text_splitter import split_text


def extract_pdf_text(file_like) -> str:
    reader = PdfReader(file_like)
    out = []
    for p in reader.pages:
        out.append(p.extract_text() or "")
    return "\n".join(out)   # <-- moved return OUTSIDE the loop


def pdf_to_chunks(file_like):
    text = extract_pdf_text(file_like)
    return split_text(text)
