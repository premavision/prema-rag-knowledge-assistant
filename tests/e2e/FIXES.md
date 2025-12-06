# E2E Test Fixes Applied

## Issues Fixed

### 1. Server Startup Error Handling
- **Problem**: Server failures were not properly reported, making debugging difficult
- **Fix**: Enhanced `api_server` and `streamlit_server` fixtures to:
  - Check if server process dies during startup
  - Capture and display stderr/stdout on failure
  - Provide clear error messages with server logs

### 2. API Request Timeouts
- **Problem**: Ingestion and query requests were timing out (default 30s timeout too short)
- **Fix**: Increased timeout to 60 seconds for:
  - Document ingestion requests
  - Query requests
  - All API operations that involve LLM/embedding calls

### 3. Better Error Messages
- **Problem**: Test failures didn't show what went wrong
- **Fix**: Added detailed error messages that include:
  - HTTP status codes
  - Response text (first 500 chars)
  - Clear failure reasons

### 4. Streamlit UI Selectors
- **Problem**: Selectors were too specific and didn't match Streamlit's actual HTML structure
- **Fix**: Updated selectors to be more robust:
  - Changed `input[placeholder*="Folder path"]` to `input[type="text"]` with `.first`
  - Changed `textarea[placeholder*="Question"]` to `textarea` with `.first`
  - Added `.clear()` before filling inputs to ensure clean state

## Known Issues / Requirements

### 1. OpenAI API Key Required
- **Issue**: Tests that involve ingestion or querying require a valid `OPENAI_API_KEY`
- **Status**: Tests will fail with 500 error if API key is not set
- **Solution**: Set `OPENAI_API_KEY` environment variable before running tests
  ```bash
  export OPENAI_API_KEY=your-key-here
  pytest tests/e2e/
  ```

### 2. Test Execution Time
- **Issue**: E2E tests take significant time due to:
  - Server startup (FastAPI + Streamlit)
  - Document ingestion (embedding generation)
  - LLM query processing
- **Status**: Expected behavior for e2e tests
- **Note**: Full test suite may take 5-10 minutes

### 3. Port Conflicts
- **Issue**: Tests use ports 8000 (FastAPI) and 8501 (Streamlit)
- **Status**: Fixtures should handle this, but if ports are in use, tests may fail
- **Solution**: Kill processes on these ports before running tests:
  ```bash
  lsof -ti:8000 | xargs kill -9
  lsof -ti:8501 | xargs kill -9
  ```

## Test Status After Fixes

### Passing Tests
- ✅ Health check endpoint
- ✅ 404 error handling for non-existent documents
- ✅ UI rendering tests (title, header, sidebar)
- ✅ Error handling for invalid paths

### Tests Requiring API Key
- ⚠️ Document ingestion (needs OpenAI API key)
- ⚠️ Document listing (needs ingestion first)
- ⚠️ Query functionality (needs OpenAI API key + ingested documents)
- ⚠️ Complete workflows (needs full setup)

## Running Tests

### With API Key
```bash
export OPENAI_API_KEY=your-key-here
source venv/bin/activate
pytest tests/e2e/ -v
```

### Without API Key (Limited Tests)
```bash
source venv/bin/activate
pytest tests/e2e/test_api.py::TestHealthEndpoint -v
pytest tests/e2e/test_api.py::TestDocumentsEndpoint::test_get_nonexistent_document_returns_404 -v
pytest tests/e2e/test_streamlit_ui.py::TestUIRendering -v
```

## Next Steps

1. **Set up CI/CD**: Configure environment with API key for full test runs
2. **Mock Services**: Consider adding option to mock OpenAI services for faster tests
3. **Test Data**: Ensure test data is properly set up before each test run
4. **Parallel Execution**: Consider running API and UI tests in parallel (separate sessions)
