from langchain.chains import RetrievalQA
from src.llm.gemini import get_llm




def build_rag_chain(retriever):
    llm = get_llm()
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever, chain_type="stuff")