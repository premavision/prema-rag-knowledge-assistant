# Prema RAG Knowledge Assistant

Portfolio-grade mini-product for Prema Vision that ingests local documents, indexes them in a vector store, and exposes a FastAPI + Streamlit interface for question-answering with citations.

## Why this structure?
- Clear separation of concerns: sources → parsers → chunking → embeddings → vector store → retrieval → LLM.
- Interfaces for `DocumentSource`, `EmbeddingClient`, `LLMClient`, and `VectorStore` keep the RAG core provider-agnostic.
- Configuration-driven via environment (`.env.example`) so swapping models or stores is trivial.
- FastAPI routes stay thin; orchestration lives in services for testability and reuse.

## Architecture (flow)
```
LocalFolderSource → Parser (pdf/md/txt) → Chunker → EmbeddingClient → VectorStore (Chroma)
                                                     ↑                       ↓
                                         RetrievalService ← query embed ← RagService → LLMClient → answer + citations
```
- **Ingestion**: scan a folder, parse supported files, normalize metadata, chunk with overlap, embed chunks, and upsert vectors + metadata into Chroma. Metadata is also tracked in a JSON document store.
- **Query**: embed the user question, retrieve top-K chunks, build a prompt that includes labeled context blocks, generate an answer, and map `[n]` markers back to citation objects.
- **Extensibility**: swap `LocalFolderSource` for future Google Drive/Confluence/Notion sources; replace OpenAI clients or Chroma with other providers by implementing the interfaces.
- **Surface**: FastAPI serves `/health`, `/ingest`, `/documents`, `/documents/{id}`, and `/query`; Streamlit consumes the same API for a simple chat-like UI.

## Stack
- Python 3.11+, FastAPI, Pydantic, Chroma (persistent local vector store), OpenAI (LLM + embeddings), pypdf/markdown2 parsers, Streamlit UI.
- Tooling recommendations: black, ruff, isort.

## Setup
1) Install dependencies (virtualenv recommended):
   ```bash
   pip install -r requirements.txt
   ```
2) Copy env template and fill values:
   ```bash
   cp .env.example .env
   # set OPENAI_API_KEY, optional OPENAI_BASE_URL/model overrides, etc.
   ```
3) Add or copy sample docs to `data/raw/` (sample files in `data/sample/`).

## Run
```bash
uvicorn app.main:app --reload
```
- Health: `curl http://localhost:8000/health`
- Ingest: `curl -X POST http://localhost:8000/ingest -H "Content-Type: application/json" -d '{"path": "./data/raw", "source_type": "local"}'`
- Query: `curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"question": "What is this project?", "top_k": 5}'`
- Documents: `curl http://localhost:8000/documents`

### Streamlit UI
Run alongside FastAPI:
```bash
streamlit run app/ui/streamlit_app.py
```
Uses `API_URL` env var (defaults to `http://localhost:8000`).

## Tests
Basic unit tests for chunking, retrieval pipeline (mocked), and prompt building (mocked LLM) are under `tests/`.
```bash
pytest
```

## Design notes & trade-offs
- **Vector store**: Chroma chosen for simplicity and local persistence. Easy to switch to pgvector or FAISS by implementing `VectorStore`.
- **Models**: OpenAI as default; configurable via env. Interfaces allow swapping to other providers.
- **Document tracking**: Lightweight JSON index in `data/processed/documents.json` to back `/documents` endpoints; chunk metadata lives in Chroma.
- **Error handling**: Parser failures are surfaced in ingestion results; LLM/embedding config issues return HTTP errors when misconfigured.

## Future enhancements
- Additional connectors (Google Drive, Confluence, Notion).
- Authn/authz on APIs and UI.
- Better chunking/token-aware splitting and metadata enrichment (tags, owners).
- Evaluation harness and feedback storage.
