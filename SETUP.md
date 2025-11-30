# Setup Guide

This guide will help you get the Prema RAG Knowledge Assistant up and running.

## Prerequisites

- Python 3.11+ (tested with Python 3.14)
- pip

## Installation Steps

1. **Create and activate a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env  # If .env.example exists
   # Or create .env manually with:
   ```
   
   Required environment variable:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   Optional environment variables:
   ```
   OPENAI_BASE_URL=https://api.openai.com/v1
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_EMBEDDING_MODEL=text-embedding-3-small
   ```

4. **Prepare data directory**:
   The `data/raw/` directory should contain your documents (PDF, Markdown, or TXT files).
   Sample files are already in `data/sample/` and have been copied to `data/raw/`.

## Running the Application

### FastAPI Server

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

- Health check: `curl http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

### Streamlit UI (Optional)

In a separate terminal:
```bash
streamlit run app/ui/streamlit_app.py
```

The UI will be available at `http://localhost:8501`

## Usage

1. **Ingest documents**:
   ```bash
   curl -X POST http://localhost:8000/ingest \
     -H "Content-Type: application/json" \
     -d '{"path": "./data/raw", "source_type": "local"}'
   ```

2. **Query the knowledge base**:
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "What is this project?", "top_k": 5}'
   ```

3. **List documents**:
   ```bash
   curl http://localhost:8000/documents
   ```

## Troubleshooting

### ChromaDB/Pydantic Compatibility

If you encounter issues with ChromaDB and Pydantic v2, the project includes a compatibility shim in `app/__init__.py` that patches Pydantic to work with older ChromaDB versions.

### Missing Dependencies

If you see import errors, ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### OpenAI API Key

Make sure your `OPENAI_API_KEY` is set in the `.env` file. Without it, the embedding and LLM services will fail.

## Project Structure

- `app/` - Main application code
  - `api/` - FastAPI routes
  - `config/` - Configuration and settings
  - `infra/` - Infrastructure (document store)
  - `models/` - Pydantic models
  - `services/` - Business logic services
  - `ui/` - Streamlit UI
- `data/` - Data directories
  - `raw/` - Input documents
  - `processed/` - Processed metadata
  - `vectorstore/` - ChromaDB vector store
- `tests/` - Unit tests

