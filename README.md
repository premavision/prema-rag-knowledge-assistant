# 🧠 Prema RAG Knowledge Assistant

A portfolio-grade Retrieval-Augmented Generation (RAG) mini-product for **Prema Vision**.  
The app ingests local documents, indexes them in a vector store, and provides a **FastAPI backend + Streamlit UI** for question-answering with **context-rich citations**.

Designed to be clean, modular, and provider-agnostic — ready for real-world extension.

---

## 🚀 What It Does

- **Ingest any local knowledge base** (PDF, Markdown, TXT)
- **Parse → chunk → embed → store** documents using a consistent pipeline
- **Query with citations** via a FastAPI endpoint  
- **Streamlit chat-style interface**
- **Provider-agnostic architecture** (swap embeddings, models, vector stores)
- **Local vector store with persistence**
- **Lightweight tests** for pipeline components

---

## 🏛 Architecture Overview

### High-level pipeline

```
LocalFolderSource
   → Parser (pdf/md/txt)
      → Chunker
         → EmbeddingClient
            → VectorStore (Chroma)
                     ↓
RetrievalService ← query embedding ← RagService ← LLMClient
                     ↓
            Answer + structured citations
```

### Why this structure?

- Separation of concerns: **sources → parsers → chunking → embeddings → vector store → retrieval → LLM**
- Simple interfaces (`DocumentSource`, `EmbeddingClient`, `LLMClient`, `VectorStore`)  
  → easy swapping between OpenAI / Anthropic / Ollama / pgvector / FAISS
- FastAPI routes remain thin — orchestration lives in **services/**
- Environment-driven configuration from `.env.example`

---

## 📂 Project Layout

```
app/
  analysis/         # stats, theme extraction, LLM wrapper
  api/              # FastAPI routers & dependencies
  core/             # settings, logging
  db/               # SQLModel + engine helpers
  ingestion/        # CSV/JSON/txt/pdf ingestion services
  schemas/          # Pydantic DTOs
  services/         # Orchestration for ingestion & retrieval
data/
  raw/              # user-provided docs
  processed/        # metadata + normalized index
dashboard/
  app.py            # Streamlit UI
scripts/
  ingest_sample.py  # quick demo ingestion
tests/
  ...               # unit tests for core pieces
```

---

## 🧪 Requirements & Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

(virtualenv recommended)

### 2. Configure environment

```bash
cp .env.example .env
```

Set:

- `OPENAI_API_KEY`
- optional: `OPENAI_BASE_URL`, model overrides  
- vector store settings

### 3. Add documents

Place PDFs/MD/TXT into:

```
data/raw/
```

Sample files are in `data/sample/`.

---

## ▶️ Running the App

### FastAPI backend

```bash
uvicorn app.main:app --reload
```

- Health: `GET /health`
- Docs: `http://localhost:8000/docs`

#### Example ingestion

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"path": "./data/raw", "source_type": "local"}'
```

#### Example query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What does this project do?", "top_k": 5}'
```

---

## 💬 Streamlit UI

Run next to FastAPI:

```bash
streamlit run app/ui/streamlit_app.py
```

Uses:

```
API_URL=http://localhost:8000
```

Provides a minimal chat interface that shows generated answers + citations.

---

## 🔒 Security Notes

- Local-only system by default  
- Input validation for ingestion  
- Chunk-level metadata stored with provenance  
- Vector store is persistent (Chroma)  
- Ready to add auth (API keys / JWT / Proxy auth)

---

## 🧬 Design Notes & Trade-offs

- **Chroma** chosen for simplicity; easily replaced via interface  
- **OpenAI** default LLM provider; can swap anything implementing `LLMClient`  
- **JSON document index** for metadata → keeps `/documents` endpoints fast  
- **Parser failures** are reported cleanly in ingestion responses  
- **Token-aware chunking** recommended as next enhancement

---

## 🔮 Future Enhancements

- Connectors for Google Drive / Confluence / Notion  
- Authentication & authorization  
- Richer embeddings & improved chunking  
- Live evaluation harness  
- Feedback storage & ranking

---

## 📄 License

MIT — reuse freely in your own projects or pipelines.
