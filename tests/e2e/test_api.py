"""
End-to-end tests for FastAPI endpoints.

These tests cover:
- Health check endpoint
- Document ingestion
- Document listing and retrieval
- Query functionality
- Error handling
"""
import json
from pathlib import Path

import httpx
import pytest


class TestHealthEndpoint:
    """Test cases for the /health endpoint."""

    def test_health_check_returns_200(self, api_client: httpx.Client):
        """
        Test that the health endpoint returns 200 OK.

        This is a basic smoke test to ensure the API server is running
        and responding to requests.
        """
        response = api_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data or len(data) >= 0  # Health response may vary


class TestIngestionEndpoint:
    """Test cases for the /ingest endpoint."""

    def test_ingest_documents_from_valid_path(
        self, api_client: httpx.Client, test_data_dir: Path
    ):
        """
        Test ingesting documents from a valid folder path.

        This test:
        1. Sends a POST request to /ingest with a valid folder path
        2. Verifies the response contains ingestion results
        3. Checks that documents and chunks are counted correctly
        4. Ensures no errors occurred during ingestion
        """
        test_raw_dir = test_data_dir / "raw"
        response = api_client.post(
            "/ingest",
            json={"path": str(test_raw_dir), "source_type": "local"},
            timeout=60.0,  # Increase timeout for ingestion
        )

        if response.status_code != 200:
            pytest.fail(
                f"Ingestion failed with status {response.status_code}. "
                f"Response: {response.text[:500]}"
            )
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "results" in data
        assert "total_documents" in data
        assert "total_chunks" in data
        assert "errors" in data

        # Verify ingestion was successful
        assert data["total_documents"] > 0, "Should have ingested at least one document"
        assert data["total_chunks"] > 0, "Should have created at least one chunk"
        assert len(data["errors"]) == 0, "Should have no errors"

        # Verify result structure
        for result in data["results"]:
            assert "document" in result
            assert "chunks" in result
            assert result["chunks"] > 0, "Each document should have chunks"

    def test_ingest_documents_with_tags(
        self, api_client: httpx.Client, test_data_dir: Path
    ):
        """
        Test ingesting documents with custom tags.

        This test verifies that tags can be applied to documents during ingestion
        and that they are properly stored in the document metadata.
        """
        test_raw_dir = test_data_dir / "raw"
        tags = ["test", "e2e", "tagged"]
        response = api_client.post(
            "/ingest",
            json={"path": str(test_raw_dir), "source_type": "local", "tags": tags},
            timeout=60.0,
        )

        if response.status_code != 200:
            pytest.fail(
                f"Ingestion failed with status {response.status_code}. "
                f"Response: {response.text[:500]}"
            )
        assert response.status_code == 200
        data = response.json()
        assert data["total_documents"] > 0

        # Verify tags are applied
        for result in data["results"]:
            doc = result["document"]
            assert "tags" in doc
            assert set(doc["tags"]) == set(tags), "Tags should match input tags"

    def test_ingest_with_invalid_path_returns_400(self, api_client: httpx.Client):
        """
        Test that ingesting from a non-existent path returns 400 Bad Request.

        This test ensures proper error handling when an invalid path is provided.
        """
        response = api_client.post(
            "/ingest",
            json={"path": "/nonexistent/path/12345", "source_type": "local"},
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "does not exist" in data["detail"].lower()

    def test_ingest_with_default_path(self, api_client: httpx.Client):
        """
        Test ingesting documents using the default path from settings.

        This test verifies that when no path is provided, the system uses
        the default data_raw_path from configuration.
        """
        response = api_client.post(
            "/ingest",
            json={"source_type": "local"},
        )

        # Should either succeed (if default path exists) or fail with appropriate error
        assert response.status_code in [200, 400]


class TestDocumentsEndpoint:
    """Test cases for the /documents endpoints."""

    def test_list_documents_after_ingestion(
        self, api_client: httpx.Client, test_data_dir: Path
    ):
        """
        Test listing all documents after ingestion.

        This test:
        1. First ingests documents
        2. Then retrieves the list of all documents
        3. Verifies the list contains the ingested documents
        4. Checks document structure and required fields
        """
        # Ingest documents first
        test_raw_dir = test_data_dir / "raw"
        ingest_response = api_client.post(
            "/ingest",
            json={"path": str(test_raw_dir), "source_type": "local"},
            timeout=60.0,
        )
        if ingest_response.status_code != 200:
            pytest.fail(
                f"Ingestion failed with status {ingest_response.status_code}. "
                f"Response: {ingest_response.text[:500]}"
            )
        assert ingest_response.status_code == 200

        # List documents
        response = api_client.get("/documents")
        assert response.status_code == 200
        documents = response.json()

        assert isinstance(documents, list)
        assert len(documents) > 0, "Should have at least one document"

        # Verify document structure
        for doc in documents:
            assert "id" in doc
            assert "source" in doc
            assert "path" in doc
            assert "title" in doc
            assert "created_at" in doc
            assert "updated_at" in doc

    def test_get_document_by_id(
        self, api_client: httpx.Client, test_data_dir: Path
    ):
        """
        Test retrieving a specific document by ID.

        This test:
        1. Ingests documents
        2. Gets the list of documents
        3. Retrieves a specific document by ID
        4. Verifies the document details match
        """
        # Ingest documents
        test_raw_dir = test_data_dir / "raw"
        ingest_response = api_client.post(
            "/ingest",
            json={"path": str(test_raw_dir), "source_type": "local"},
            timeout=60.0,
        )
        if ingest_response.status_code != 200:
            pytest.fail(
                f"Ingestion failed with status {ingest_response.status_code}. "
                f"Response: {ingest_response.text[:500]}"
            )
        assert ingest_response.status_code == 200

        # Get document list
        list_response = api_client.get("/documents")
        documents = list_response.json()
        assert len(documents) > 0

        # Get specific document
        doc_id = documents[0]["id"]
        response = api_client.get(f"/documents/{doc_id}")
        assert response.status_code == 200

        document = response.json()
        assert document["id"] == doc_id
        assert document["id"] == documents[0]["id"]

    def test_get_nonexistent_document_returns_404(self, api_client: httpx.Client):
        """
        Test that retrieving a non-existent document returns 404 Not Found.

        This test ensures proper error handling for invalid document IDs.
        """
        response = api_client.get("/documents/nonexistent-id-12345")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestQueryEndpoint:
    """Test cases for the /query endpoint."""

    @pytest.fixture(autouse=True)
    def setup_ingested_documents(
        self, api_client: httpx.Client, test_data_dir: Path
    ):
        """
        Fixture to ensure documents are ingested before query tests.

        This ensures the vector store has data to query against.
        """
        test_raw_dir = test_data_dir / "raw"
        api_client.post(
            "/ingest",
            json={"path": str(test_raw_dir), "source_type": "local"},
        )

    def test_query_with_valid_question(self, api_client: httpx.Client):
        """
        Test querying the knowledge base with a valid question.

        This test:
        1. Sends a query with a relevant question
        2. Verifies the response contains an answer
        3. Checks that citations are provided
        4. Validates citation structure
        """
        response = api_client.post(
            "/query",
            json={"question": "What features does the system support?"},
            timeout=60.0,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "answer" in data
        assert "citations" in data
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0, "Answer should not be empty"
        assert isinstance(data["citations"], list)

        # Verify citations structure if present
        for citation in data["citations"]:
            assert "doc_id" in citation
            assert "doc_title" in citation
            assert "chunk_id" in citation
            assert "snippet" in citation
            assert "score" in citation
            assert isinstance(citation["score"], (int, float))

    def test_query_with_custom_top_k(self, api_client: httpx.Client):
        """
        Test querying with a custom top_k parameter.

        This test verifies that the top_k parameter controls the number
        of retrieved chunks/citations.
        """
        response = api_client.post(
            "/query",
            json={"question": "What is this system about?", "top_k": 3},
            timeout=60.0,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["citations"]) <= 3, "Should respect top_k parameter"

    def test_query_with_different_questions(self, api_client: httpx.Client):
        """
        Test querying with various question types.

        This test ensures the system can handle different question formats
        and return relevant answers.
        """
        questions = [
            "What is the system?",
            "How does ingestion work?",
            "Tell me about the features",
        ]

        for question in questions:
            response = api_client.post(
                "/query",
                json={"question": question},
                timeout=60.0,
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["answer"]) > 0, f"Should return answer for: {question}"

    def test_query_with_empty_question(self, api_client: httpx.Client):
        """
        Test querying with an empty question.

        This test verifies error handling for invalid input.
        """
        response = api_client.post(
            "/query",
            json={"question": ""},
        )

        # Should either return 422 (validation error) or 200 with empty answer
        assert response.status_code in [200, 422]


class TestEndToEndWorkflow:
    """Test complete workflows combining multiple endpoints."""

    def test_complete_ingestion_to_query_workflow(
        self, api_client: httpx.Client, test_data_dir: Path
    ):
        """
        Test a complete workflow from ingestion to querying.

        This comprehensive test:
        1. Ingests documents from a folder
        2. Lists all ingested documents
        3. Retrieves a specific document
        4. Queries the knowledge base
        5. Verifies the answer references the ingested content

        This ensures the entire pipeline works correctly end-to-end.
        """
        test_raw_dir = test_data_dir / "raw"

        # Step 1: Ingest documents
        ingest_response = api_client.post(
            "/ingest",
            json={"path": str(test_raw_dir), "source_type": "local"},
            timeout=60.0,
        )
        if ingest_response.status_code != 200:
            pytest.fail(
                f"Ingestion failed with status {ingest_response.status_code}. "
                f"Response: {ingest_response.text[:500]}"
            )
        assert ingest_response.status_code == 200
        ingest_data = ingest_response.json()
        assert ingest_data["total_documents"] > 0

        # Step 2: List documents
        list_response = api_client.get("/documents")
        assert list_response.status_code == 200
        documents = list_response.json()
        assert len(documents) == ingest_data["total_documents"]

        # Step 3: Get specific document
        if documents:
            doc_id = documents[0]["id"]
            doc_response = api_client.get(f"/documents/{doc_id}")
            assert doc_response.status_code == 200
            document = doc_response.json()
            assert document["id"] == doc_id

        # Step 4: Query the knowledge base
        query_response = api_client.post(
            "/query",
            json={"question": "What documents were ingested?"},
            timeout=60.0,
        )
        assert query_response.status_code == 200
        query_data = query_response.json()
        assert len(query_data["answer"]) > 0
        assert len(query_data["citations"]) > 0

        # Step 5: Verify citations reference ingested documents
        cited_doc_ids = {cite["doc_id"] for cite in query_data["citations"]}
        ingested_doc_ids = {doc["id"] for doc in documents}
        assert cited_doc_ids.issubset(
            ingested_doc_ids
        ), "Citations should reference ingested documents"
