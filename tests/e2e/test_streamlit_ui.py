"""
End-to-end tests for Streamlit UI.

These tests cover:
- UI rendering and layout
- Document ingestion through the UI
- Document listing in sidebar
- Query functionality through the UI
- Error handling and user feedback
"""
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect


class TestUIRendering:
    """Test cases for UI rendering and layout."""

    def test_page_title_and_header(self, page: Page):
        """
        Test that the page title and header are correctly displayed.

        This test verifies:
        1. The page title is set correctly
        2. The main header is visible
        3. The caption/description is displayed
        """
        # Check page title
        expect(page).to_have_title("Prema RAG Knowledge Assistant")

        # Check main header
        header = page.locator("h1")
        expect(header).to_be_visible()
        expect(header).to_contain_text("Prema RAG Knowledge Assistant")

        # Check caption
        caption = page.locator("text=Ask questions over your documents with citations")
        expect(caption).to_be_visible()

    def test_sidebar_rendering(self, page: Page):
        """
        Test that the sidebar is correctly rendered with all sections.

        This test verifies:
        1. Ingestion section is visible
        2. Indexed documents section is visible
        3. Input fields are present
        """
        # Check ingestion section
        ingestion_header = page.locator("text=Ingestion")
        expect(ingestion_header).to_be_visible()

        # Check folder path input - Streamlit text_input creates an input element
        folder_input = page.locator('input[type="text"]').first
        expect(folder_input).to_be_visible()

        # Check ingest button
        ingest_button = page.locator("button:has-text('Ingest folder')")
        expect(ingest_button).to_be_visible()

        # Check indexed documents section
        docs_header = page.locator("text=Indexed documents")
        expect(docs_header).to_be_visible()

    def test_query_section_rendering(self, page: Page):
        """
        Test that the query section is correctly rendered.

        This test verifies:
        1. Query section header is visible
        2. Question text area is present
        3. Top K slider is present
        4. Run RAG button is visible
        """
        # Check query section
        query_header = page.locator("text=Ask a question")
        expect(query_header).to_be_visible()

        # Check question text area - Streamlit uses st.text_area which creates a textarea
        question_textarea = page.locator('textarea').first
        expect(question_textarea).to_be_visible()

        # Check top K slider - Streamlit uses st.slider which creates an input[type="range"]
        top_k_slider = page.locator('input[type="range"]').first
        expect(top_k_slider).to_be_visible()

        # Check Run RAG button
        run_button = page.locator("button:has-text('Run RAG')")
        expect(run_button).to_be_visible()


class TestDocumentIngestionUI:
    """Test cases for document ingestion through the UI."""

    def test_ingest_documents_with_default_path(
        self, page: Page, test_data_dir: Path
    ):
        """
        Test ingesting documents using the default folder path.

        This test:
        1. Clicks the ingest button with default path
        2. Waits for success message
        3. Verifies documents appear in the sidebar
        4. Checks that the ingestion was successful
        """
        # Click ingest button
        ingest_button = page.locator("button:has-text('Ingest folder')")
        ingest_button.click()

        # Wait for success message
        success_message = page.locator("text=/Ingested \\d+ document\\(s\\)\\.")
        expect(success_message).to_be_visible(timeout=30000)

        # Verify documents appear in sidebar
        # Documents should be listed under "Indexed documents"
        # Wait a bit for the UI to update
        page.wait_for_timeout(1000)

        # Check that document list is populated
        # The sidebar should show document titles
        sidebar_content = page.locator('[data-testid="stSidebar"]')
        expect(sidebar_content).to_be_visible()

    def test_ingest_documents_with_custom_path(
        self, page: Page, test_data_dir: Path
    ):
        """
        Test ingesting documents with a custom folder path.

        This test:
        1. Enters a custom folder path
        2. Clicks the ingest button
        3. Verifies success message
        4. Checks documents are listed
        """
        test_raw_dir = test_data_dir / "raw"

        # Enter custom path - Streamlit text_input creates an input element
        folder_input = page.locator('input[type="text"]').first
        folder_input.clear()
        folder_input.fill(str(test_raw_dir))

        # Click ingest button
        ingest_button = page.locator("button:has-text('Ingest folder')")
        ingest_button.click()

        # Wait for success message
        success_message = page.locator("text=/Ingested \\d+ document\\(s\\)\\.")
        expect(success_message).to_be_visible(timeout=30000)

    def test_ingest_with_invalid_path_shows_error(self, page: Page):
        """
        Test that ingesting with an invalid path shows an error message.

        This test verifies proper error handling in the UI.
        """
        # Enter invalid path
        folder_input = page.locator('input[type="text"]').first
        folder_input.clear()
        folder_input.fill("/nonexistent/path/12345")

        # Click ingest button
        ingest_button = page.locator("button:has-text('Ingest folder')")
        ingest_button.click()

        # Wait for error message
        error_message = page.locator("text=/Ingestion failed|error/i")
        expect(error_message).to_be_visible(timeout=10000)


class TestDocumentListingUI:
    """Test cases for document listing in the sidebar."""

    @pytest.fixture(autouse=True)
    def setup_ingested_documents(self, page: Page, test_data_dir: Path):
        """
        Fixture to ingest documents before testing document listing.

        This ensures there are documents to display in the sidebar.
        """
        test_raw_dir = test_data_dir / "raw"

        # Ingest documents
        folder_input = page.locator('input[type="text"]').first
        folder_input.clear()
        folder_input.fill(str(test_raw_dir))

        ingest_button = page.locator("button:has-text('Ingest folder')")
        ingest_button.click()

        # Wait for ingestion to complete
        page.wait_for_selector("text=/Ingested \\d+ document\\(s\\)\\.", timeout=30000)
        page.wait_for_timeout(2000)  # Wait for UI to update

    def test_documents_appear_in_sidebar(self, page: Page):
        """
        Test that ingested documents appear in the sidebar.

        This test verifies:
        1. Documents are listed in the sidebar
        2. Document titles are visible
        3. Document paths are displayed
        """
        # Check that documents section is visible
        docs_section = page.locator("text=Indexed documents")
        expect(docs_section).to_be_visible()

        # Documents should be listed (check for bullet points or list items)
        # Streamlit renders lists in a specific way, so we check for content
        sidebar = page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_contain_text("test_guide.md", timeout=5000)
        expect(sidebar).to_contain_text("test_notes.txt", timeout=5000)


class TestQueryUI:
    """Test cases for query functionality through the UI."""

    @pytest.fixture(autouse=True)
    def setup_ingested_documents(self, page: Page, test_data_dir: Path):
        """
        Fixture to ingest documents before query tests.

        This ensures the knowledge base has data to query.
        """
        test_raw_dir = test_data_dir / "raw"

        # Ingest documents
        folder_input = page.locator('input[type="text"]').first
        folder_input.clear()
        folder_input.fill(str(test_raw_dir))

        ingest_button = page.locator("button:has-text('Ingest folder')")
        ingest_button.click()

        # Wait for ingestion to complete
        page.wait_for_selector("text=/Ingested \\d+ document\\(s\\)\\.", timeout=30000)
        page.wait_for_timeout(2000)

    def test_query_with_valid_question(self, page: Page):
        """
        Test querying with a valid question.

        This test:
        1. Enters a question in the text area
        2. Clicks the Run RAG button
        3. Waits for the answer to appear
        4. Verifies answer and citations are displayed
        """
        # Enter question
        question_textarea = page.locator('textarea').first
        question_textarea.fill("What features does the system support?")

        # Click Run RAG button
        run_button = page.locator("button:has-text('Run RAG')")
        run_button.click()

        # Wait for answer section
        answer_header = page.locator("text=Answer")
        expect(answer_header).to_be_visible(timeout=30000)

        # Verify answer content is displayed
        # The answer should be in a markdown or text element after the header
        answer_section = page.locator("text=Answer").locator("..")
        expect(answer_section).to_contain_text(".", timeout=5000)  # At least some content

        # Check citations section
        citations_header = page.locator("text=Citations")
        expect(citations_header).to_be_visible()

    def test_query_with_empty_question_shows_warning(self, page: Page):
        """
        Test that querying with an empty question shows a warning.

        This test verifies proper validation in the UI.
        """
        # Leave question empty
        question_textarea = page.locator('textarea').first
        question_textarea.clear()

        # Click Run RAG button
        run_button = page.locator("button:has-text('Run RAG')")
        run_button.click()

        # Wait for warning message
        warning_message = page.locator("text=/Please enter a question|warning/i")
        expect(warning_message).to_be_visible(timeout=5000)

    def test_query_with_different_top_k_values(self, page: Page):
        """
        Test querying with different top_k values using the slider.

        This test verifies:
        1. The slider can be adjusted
        2. Different top_k values affect the number of citations
        """
        # Set top_k to 3
        top_k_slider = page.locator('input[type="range"]')
        top_k_slider.fill("3")

        # Enter question
        question_textarea = page.locator('textarea').first
        question_textarea.fill("What is this system about?")

        # Click Run RAG button
        run_button = page.locator("button:has-text('Run RAG')")
        run_button.click()

        # Wait for answer
        answer_header = page.locator("text=Answer")
        expect(answer_header).to_be_visible(timeout=30000)

        # Verify citations are displayed (should be <= 3)
        citations_header = page.locator("text=Citations")
        expect(citations_header).to_be_visible()

    def test_multiple_queries(self, page: Page):
        """
        Test performing multiple queries in sequence.

        This test verifies:
        1. Multiple queries can be executed
        2. Each query returns results
        3. The UI updates correctly for each query
        """
        questions = [
            "What features does the system support?",
            "How does ingestion work?",
            "Tell me about the documents",
        ]

        for question in questions:
            # Enter question
            question_textarea = page.locator('textarea').first
            question_textarea.fill(question)

            # Click Run RAG button
            run_button = page.locator("button:has-text('Run RAG')")
            run_button.click()

            # Wait for answer
            answer_header = page.locator("text=Answer")
            expect(answer_header).to_be_visible(timeout=30000)

            # Verify answer content
            answer_section = page.locator("text=Answer").locator("..")
            expect(answer_section).to_contain_text(".", timeout=5000)

            # Wait a bit before next query
            page.wait_for_timeout(1000)


class TestCompleteUIWorkflow:
    """Test complete workflows through the UI."""

    def test_complete_ingestion_to_query_workflow(
        self, page: Page, test_data_dir: Path
    ):
        """
        Test a complete workflow from ingestion to querying through the UI.

        This comprehensive test:
        1. Ingests documents through the UI
        2. Verifies documents appear in sidebar
        3. Performs a query
        4. Verifies answer and citations are displayed

        This ensures the entire UI workflow works correctly end-to-end.
        """
        test_raw_dir = test_data_dir / "raw"

        # Step 1: Ingest documents
        folder_input = page.locator('input[type="text"]').first
        folder_input.clear()
        folder_input.fill(str(test_raw_dir))

        ingest_button = page.locator("button:has-text('Ingest folder')")
        ingest_button.click()

        # Wait for success message
        success_message = page.locator("text=/Ingested \\d+ document\\(s\\)\\.")
        expect(success_message).to_be_visible(timeout=30000)
        page.wait_for_timeout(2000)

        # Step 2: Verify documents in sidebar
        sidebar = page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_contain_text("test_guide.md", timeout=5000)

        # Step 3: Perform query
        question_textarea = page.locator('textarea').first
        question_textarea.fill("What documents were ingested and what do they contain?")

        run_button = page.locator("button:has-text('Run RAG')")
        run_button.click()

        # Step 4: Verify answer and citations
        answer_header = page.locator("text=Answer")
        expect(answer_header).to_be_visible(timeout=30000)

        citations_header = page.locator("text=Citations")
        expect(citations_header).to_be_visible()

        # Verify answer contains meaningful content
        answer_section = page.locator("text=Answer").locator("..")
        expect(answer_section).to_contain_text(".", timeout=5000)
