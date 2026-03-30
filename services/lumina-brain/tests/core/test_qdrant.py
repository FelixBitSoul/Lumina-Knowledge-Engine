import pytest
from lumina_brain.core.services.qdrant import qdrant_service
from datetime import datetime, timezone


class TestQdrantService:
    """Test Qdrant service functionality"""

    def test_generate_id_from_url(self):
        """Test deterministic UUID generation from URL"""
        url = "https://example.com/test"
        id1 = qdrant_service.generate_id_from_url(url)
        id2 = qdrant_service.generate_id_from_url(url)
        assert id1 == id2, "Same URL should generate same ID"

        different_url = "https://example.com/other"
        different_id = qdrant_service.generate_id_from_url(different_url)
        assert id1 != different_id, "Different URLs should generate different IDs"

    def test_extract_domain(self):
        """Test domain extraction from URL"""
        test_cases = [
            ("https://example.com/test", "example.com"),
            ("http://subdomain.example.com/path", "subdomain.example.com"),
            ("https://www.google.com/search?q=test", "www.google.com"),
        ]

        for url, expected_domain in test_cases:
            domain = qdrant_service.extract_domain(url)
            assert domain == expected_domain, f"Failed to extract domain from {url}"

    def test_upsert_and_search(self):
        """Test document upsert and search functionality"""
        # Test data
        test_url = "https://example.com/test-document"
        test_title = "Test Document"
        test_content = "This is a test document for Qdrant service"
        test_vector = [0.1] * 384  # Dummy vector

        # Upsert document
        point_id = qdrant_service.upsert_document(
            url=test_url,
            title=test_title,
            content=test_content,
            vector=test_vector
        )

        assert point_id is not None, "Upsert should return a point ID"

        # Search for the document
        search_results = qdrant_service.search(
            query_vector=test_vector,
            limit=5
        )

        assert len(search_results) > 0, "Search should return results"

        # Check if the document is in the results
        found = False
        for result in search_results:
            if result["url"] == test_url:
                found = True
                break
        assert found, "Upserted document should be found in search"

    def test_search_with_filters(self):
        """Test search with metadata filters"""
        # Test data
        test_url1 = "https://example.com/test1"
        test_url2 = "https://example.com/test2"
        test_title1 = "Test Document 1"
        test_title2 = "Test Document 2"
        test_content = "This is a test document"
        test_vector = [0.1] * 384  # Dummy vector

        # Upsert two documents
        qdrant_service.upsert_document(
            url=test_url1,
            title=test_title1,
            content=test_content,
            vector=test_vector
        )

        qdrant_service.upsert_document(
            url=test_url2,
            title=test_title2,
            content=test_content,
            vector=test_vector
        )

        # Search with title filter
        filters = {"title": "Test Document 1"}
        filtered_results = qdrant_service.search_with_filters(
            query_vector=test_vector,
            limit=5,
            filters=filters
        )

        assert len(filtered_results) > 0, "Filtered search should return results"

        # Check if only the matching document is returned
        for result in filtered_results:
            assert "Test Document 1" in result["title"], "Should only return documents matching the filter"

    def test_search_with_domain_filter(self):
        """Test search with domain filter"""
        # Test data
        test_url = "https://example.com/test"
        test_title = "Test Document"
        test_content = "This is a test document"
        test_vector = [0.1] * 384  # Dummy vector

        # Upsert document
        qdrant_service.upsert_document(
            url=test_url,
            title=test_title,
            content=test_content,
            vector=test_vector
        )

        # Search with domain filter
        filters = {"domain": "example.com"}
        filtered_results = qdrant_service.search_with_filters(
            query_vector=test_vector,
            limit=5,
            filters=filters
        )

        assert len(filtered_results) > 0, "Domain-filtered search should return results"

        # Check if only the matching domain documents are returned
        for result in filtered_results:
            assert result["domain"] == "example.com", "Should only return documents from the specified domain"

    def test_updated_at_field(self):
        """Test that updated_at field is properly set"""
        # Test data
        test_url = "https://example.com/test-updated-at"
        test_title = "Test Document"
        test_content = "This is a test document"
        test_vector = [0.1] * 384  # Dummy vector

        # Upsert document
        qdrant_service.upsert_document(
            url=test_url,
            title=test_title,
            content=test_content,
            vector=test_vector
        )

        # Search for the document
        search_results = qdrant_service.search(
            query_vector=test_vector,
            limit=5
        )

        # Check if updated_at field is present and in correct format
        found = False
        for result in search_results:
            if result["url"] == test_url:
                found = True
                assert "updated_at" in result, "Document should have updated_at field"
                # Try to parse the datetime to ensure it's in valid format
                try:
                    datetime.fromisoformat(result["updated_at"])
                except ValueError:
                    pytest.fail("updated_at field should be in ISO format")
                break
        assert found, "Upserted document should be found"
