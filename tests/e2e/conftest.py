"""
Pytest fixtures for e2e tests.

This module provides fixtures for:
- Starting/stopping the FastAPI server
- Starting/stopping the Streamlit server
- Test data management
- API client setup
"""
import os
import shutil
import signal
import subprocess
import time
from pathlib import Path
from typing import Generator

import httpx
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

import httpx
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

# Test configuration
API_BASE_URL = "http://localhost:8000"
STREAMLIT_URL = "http://localhost:8501"
TEST_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "test_e2e"
TEST_RAW_DIR = TEST_DATA_DIR / "raw"
TEST_PROCESSED_DIR = TEST_DATA_DIR / "processed"
TEST_VECTORSTORE_DIR = TEST_DATA_DIR / "vectorstore"


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Create and return test data directory."""
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    TEST_RAW_DIR.mkdir(parents=True, exist_ok=True)
    return TEST_DATA_DIR


@pytest.fixture(scope="session", autouse=True)
def setup_test_data(test_data_dir: Path) -> Generator[None, None, None]:
    """Set up test data before tests and clean up after."""
    # Create sample test documents
    test_doc1 = TEST_RAW_DIR / "test_guide.md"
    test_doc1.write_text(
        """# Test Guide

This is a test guide document for e2e testing.

## Features

The system supports:
- Document ingestion
- Vector search
- RAG-based question answering

## Usage

To use the system, first ingest documents, then query them.
"""
    )

    test_doc2 = TEST_RAW_DIR / "test_notes.txt"
    test_doc2.write_text(
        """Test Notes Document

This document contains important notes about the system.

Key points:
1. The system uses ChromaDB for vector storage
2. OpenAI embeddings are used for semantic search
3. GPT models generate answers with citations
"""
    )

    yield

    # Cleanup: Remove test data directories
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)


@pytest.fixture(scope="session")
def api_server(test_data_dir: Path) -> Generator[None, None, None]:
    """
    Start FastAPI server for e2e tests.

    This fixture:
    1. Sets up environment variables for test data paths
    2. Starts the uvicorn server in a subprocess
    3. Waits for the server to be ready
    4. Yields control to tests
    5. Stops the server after tests complete
    """
    # Kill any existing server on the test port
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{8000}"],
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split("\n")
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    time.sleep(0.5)
                except (ProcessLookupError, ValueError):
                    pass
    except Exception:
        pass  # lsof might not be available, continue anyway

    # Set environment variables for test
    env = os.environ.copy()
    env["DATA_RAW_PATH"] = str(TEST_RAW_DIR)
    env["DATA_PROCESSED_PATH"] = str(TEST_PROCESSED_DIR)
    env["CHROMA_PERSIST_DIR"] = str(TEST_VECTORSTORE_DIR)

    # Start server
    process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to be ready
    max_attempts = 30
    server_ready = False
    for attempt in range(max_attempts):
        try:
            response = httpx.get(f"{API_BASE_URL}/health", timeout=2.0)
            if response.status_code == 200:
                server_ready = True
                break
        except Exception:
            time.sleep(0.5)
        
        # Check if process died
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            error_msg = f"API server process died. Return code: {process.returncode}\n"
            if stderr:
                error_msg += f"STDERR: {stderr.decode()}\n"
            if stdout:
                error_msg += f"STDOUT: {stdout.decode()}\n"
            pytest.fail(error_msg)
    
    if not server_ready:
        process.terminate()
        process.wait()
        stdout, stderr = process.communicate()
        error_msg = "API server failed to start within timeout\n"
        if stderr:
            error_msg += f"STDERR: {stderr.decode()}\n"
        if stdout:
            error_msg += f"STDOUT: {stdout.decode()}\n"
        pytest.fail(error_msg)

    yield

    # Cleanup: Stop server
    process.terminate()
    process.wait()


@pytest.fixture(scope="session")
def streamlit_server(api_server: None) -> Generator[None, None, None]:
    """
    Start Streamlit server for e2e tests.

    This fixture:
    1. Sets API_URL environment variable
    2. Starts the Streamlit server in a subprocess
    3. Waits for the server to be ready
    4. Yields control to tests
    5. Stops the server after tests complete
    """
    # Kill any existing Streamlit server on the test port
    import signal
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{8501}"],
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split("\n")
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    time.sleep(0.5)
                except (ProcessLookupError, ValueError):
                    pass
    except Exception:
        pass  # lsof might not be available, continue anyway

    env = os.environ.copy()
    env["API_URL"] = API_BASE_URL

    # Start Streamlit server
    process = subprocess.Popen(
        ["streamlit", "run", "app/ui/streamlit_app.py", "--server.port", "8501", "--server.headless", "true"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to be ready
    max_attempts = 30
    server_ready = False
    for attempt in range(max_attempts):
        try:
            response = httpx.get(STREAMLIT_URL, timeout=2.0)
            if response.status_code == 200:
                server_ready = True
                break
        except Exception:
            time.sleep(0.5)
        
        # Check if process died
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            error_msg = f"Streamlit server process died. Return code: {process.returncode}\n"
            if stderr:
                error_msg += f"STDERR: {stderr.decode()}\n"
            if stdout:
                error_msg += f"STDOUT: {stdout.decode()}\n"
            pytest.fail(error_msg)
    
    if not server_ready:
        process.terminate()
        process.wait()
        stdout, stderr = process.communicate()
        error_msg = "Streamlit server failed to start within timeout\n"
        if stderr:
            error_msg += f"STDERR: {stderr.decode()}\n"
        if stdout:
            error_msg += f"STDOUT: {stdout.decode()}\n"
        pytest.fail(error_msg)

    yield

    # Cleanup: Stop server
    process.terminate()
    process.wait()


@pytest.fixture
def api_client(api_server: None) -> httpx.Client:
    """
    Create an HTTP client for API testing.

    Returns a configured httpx.Client pointing to the test API server.
    """
    return httpx.Client(base_url=API_BASE_URL, timeout=30.0)


@pytest.fixture(scope="session")
def playwright() -> Generator[Playwright, None, None]:
    """
    Initialize Playwright for browser automation.

    This fixture:
    1. Starts Playwright
    2. Installs browsers if needed
    3. Yields the Playwright instance
    4. Closes Playwright after tests
    """
    with sync_playwright() as p:
        yield p


@pytest.fixture
def browser(playwright: Playwright) -> Generator[Browser, None, None]:
    """
    Create a browser instance for UI testing.

    Uses Chromium browser in headless mode for CI compatibility.
    """
    browser = playwright.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture
def browser_context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Create a browser context for UI testing.

    Sets up a clean browser context with default viewport.
    """
    context = browser.new_context(viewport={"width": 1280, "height": 720})
    yield context
    context.close()


@pytest.fixture
def page(browser_context: BrowserContext, streamlit_server: None) -> Generator[Page, None, None]:
    """
    Create a page for UI testing.

    Navigates to the Streamlit app and waits for it to load.
    """
    page = browser_context.new_page()
    page.goto(STREAMLIT_URL)
    # Wait for Streamlit to load
    page.wait_for_selector("h1", timeout=10000)
    yield page
    page.close()


@pytest.fixture(autouse=True)
def clean_vectorstore(test_data_dir: Path) -> Generator[None, None, None]:
    """
    Clean vectorstore and processed data before each test.

    This ensures tests start with a clean state.
    """
    # Cleanup before test
    if TEST_PROCESSED_DIR.exists():
        shutil.rmtree(TEST_PROCESSED_DIR)
    if TEST_VECTORSTORE_DIR.exists():
        shutil.rmtree(TEST_VECTORSTORE_DIR)
    TEST_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    TEST_VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

    yield

    # Optional: cleanup after test (commented out to preserve state for debugging)
    # if TEST_PROCESSED_DIR.exists():
    #     shutil.rmtree(TEST_PROCESSED_DIR)
    # if TEST_VECTORSTORE_DIR.exists():
    #     shutil.rmtree(TEST_VECTORSTORE_DIR)
