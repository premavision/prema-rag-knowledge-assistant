# End-to-End (E2E) Tests

This directory contains comprehensive end-to-end tests for the Prema RAG Knowledge Assistant application.

## Overview

The e2e test suite covers:

1. **API Endpoints** (`test_api.py`):
   - Health check endpoint
   - Document ingestion
   - Document listing and retrieval
   - Query functionality
   - Error handling

2. **Streamlit UI** (`test_streamlit_ui.py`):
   - UI rendering and layout
   - Document ingestion through the UI
   - Document listing in sidebar
   - Query functionality through the UI
   - Error handling and user feedback

## Test Structure

```
tests/e2e/
├── __init__.py
├── conftest.py          # Pytest fixtures for test setup
├── test_api.py          # API endpoint tests
├── test_streamlit_ui.py # Streamlit UI tests
└── README.md            # This file
```

## Prerequisites

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

3. **Set up environment variables**:
   - Ensure `.env` file exists with `OPENAI_API_KEY` set
   - The tests use test-specific data directories (automatically created)

## Running Tests

### Run all e2e tests:
```bash
pytest tests/e2e/
```

### Run only API tests:
```bash
pytest tests/e2e/test_api.py
```

### Run only UI tests:
```bash
pytest tests/e2e/test_streamlit_ui.py
```

### Run with verbose output:
```bash
pytest tests/e2e/ -v
```

### Run a specific test:
```bash
pytest tests/e2e/test_api.py::TestHealthEndpoint::test_health_check_returns_200
```

## Test Fixtures

The `conftest.py` file provides several fixtures:

- **`api_server`**: Starts/stops the FastAPI server for testing
- **`streamlit_server`**: Starts/stops the Streamlit server for testing
- **`api_client`**: HTTP client for API testing
- **`page`**: Playwright page object for UI testing
- **`test_data_dir`**: Test data directory with sample documents
- **`clean_vectorstore`**: Cleans vectorstore before each test

## Test Data

Test data is automatically created in `data/test_e2e/`:
- `data/test_e2e/raw/` - Sample documents for ingestion
- `data/test_e2e/processed/` - Processed documents
- `data/test_e2e/vectorstore/` - Vector store data

The test data is cleaned up after test sessions, but may persist for debugging purposes.

## Test Coverage

### API Tests (`test_api.py`)

#### Health Endpoint
- ✅ Health check returns 200 OK

#### Ingestion Endpoint
- ✅ Ingest documents from valid path
- ✅ Ingest documents with custom tags
- ✅ Error handling for invalid paths
- ✅ Default path handling

#### Documents Endpoint
- ✅ List all documents after ingestion
- ✅ Get document by ID
- ✅ Error handling for non-existent documents

#### Query Endpoint
- ✅ Query with valid question
- ✅ Query with custom top_k parameter
- ✅ Query with different question types
- ✅ Error handling for empty questions

#### End-to-End Workflow
- ✅ Complete ingestion to query workflow

### UI Tests (`test_streamlit_ui.py`)

#### UI Rendering
- ✅ Page title and header
- ✅ Sidebar rendering
- ✅ Query section rendering

#### Document Ingestion UI
- ✅ Ingest with default path
- ✅ Ingest with custom path
- ✅ Error handling for invalid paths

#### Document Listing UI
- ✅ Documents appear in sidebar after ingestion

#### Query UI
- ✅ Query with valid question
- ✅ Warning for empty questions
- ✅ Query with different top_k values
- ✅ Multiple sequential queries

#### Complete UI Workflow
- ✅ Complete ingestion to query workflow through UI

## Troubleshooting

### Tests fail with "server failed to start"
- Ensure ports 8000 (FastAPI) and 8501 (Streamlit) are not in use
- Check that all dependencies are installed
- Verify `.env` file exists with valid `OPENAI_API_KEY`

### UI tests fail with timeout
- Increase timeout values in test files if needed
- Check that Streamlit server is starting correctly
- Verify browser is installed: `playwright install chromium`

### Vector store errors
- The test fixtures automatically clean the vectorstore before each test
- If issues persist, manually delete `data/test_e2e/vectorstore/`

## Adding New Tests

When adding new e2e tests:

1. **For API tests**: Add test methods to appropriate test classes in `test_api.py`
2. **For UI tests**: Add test methods to appropriate test classes in `test_streamlit_ui.py`
3. **Use fixtures**: Leverage existing fixtures from `conftest.py`
4. **Add descriptions**: Include descriptive docstrings explaining what each test verifies
5. **Follow naming**: Use descriptive test names following the pattern `test_<what>_<expected_result>`

## Continuous Integration

These tests are designed to run in CI environments:
- Headless browser mode (Chromium)
- Automatic server startup/teardown
- Isolated test data directories
- No manual intervention required

## Notes

- Tests may take several minutes to run due to:
  - Server startup time
  - Document ingestion (embedding generation)
  - LLM query processing
- The tests use real OpenAI API calls (ensure API key is set)
- Test data is automatically generated and cleaned up
- Vector store is cleaned before each test for isolation
