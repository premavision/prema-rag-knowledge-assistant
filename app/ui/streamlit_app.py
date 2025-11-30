import os
from typing import Any, Dict, List

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")


def call_ingest(folder: str) -> Dict[str, Any] | None:
    try:
        response = requests.post(f"{API_URL}/ingest", json={"path": folder, "source_type": "local"})
        response.raise_for_status()
        return response.json()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Ingestion failed: {exc}")
        return None


def call_query(question: str, top_k: int) -> Dict[str, Any] | None:
    try:
        response = requests.post(f"{API_URL}/query", json={"question": question, "top_k": top_k})
        response.raise_for_status()
        return response.json()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Query failed: {exc}")
        return None


def call_documents() -> List[Dict[str, Any]]:
    try:
        response = requests.get(f"{API_URL}/documents")
        response.raise_for_status()
        return response.json()
    except Exception:
        return []


def main() -> None:
    st.set_page_config(page_title="Prema RAG Knowledge Assistant", layout="wide")
    st.title("Prema RAG Knowledge Assistant")
    st.caption("Ask questions over your documents with citations.")

    with st.sidebar:
        st.header("Ingestion")
        folder = st.text_input("Folder path", value="./data/raw")
        if st.button("Ingest folder"):
            result = call_ingest(folder)
            if result:
                st.success(f"Ingested {result.get('total_documents', 0)} document(s).")

        st.header("Indexed documents")
        docs = call_documents()
        for doc in docs:
            st.write(f"- {doc.get('title')} ({doc.get('path')})")

    st.subheader("Ask a question")
    question = st.text_area("Question", height=120)
    top_k = st.slider("Top K", min_value=1, max_value=10, value=5)
    if st.button("Run RAG"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Retrieving and generating..."):
                result = call_query(question, top_k)
            if result:
                st.markdown("### Answer")
                st.write(result.get("answer", ""))
                st.markdown("### Citations")
                for idx, cite in enumerate(result.get("citations", []), start=1):
                    st.write(
                        f"[{idx}] {cite.get('doc_title')} — score: {cite.get('score'):.3f}\n\n"
                        f"{cite.get('snippet')}"
                    )


if __name__ == "__main__":
    main()
