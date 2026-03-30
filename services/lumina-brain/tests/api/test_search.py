from fastapi.testclient import TestClient
from lumina_brain.main import app
import pytest


client = TestClient(app)


class TestSearchAPI:
    """Test search API endpoints"""

    def test_search_basic(self):
        """Test basic search functionality"""
        response = client.get("/search?query=test")
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert data["query"] == "test"
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_search_with_limit(self):
        """Test search with custom limit"""
        response = client.get("/search?query=test&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 5

    def test_search_with_title_filter(self):
        """Test search with title filter"""
        response = client.get("/search?query=test&title=Test")
        assert response.status_code == 200
        data = response.json()
        assert data["filters"] is not None
        assert "title" in data["filters"]
        assert data["filters"]["title"] == "Test"

    def test_search_with_domain_filter(self):
        """Test search with domain filter"""
        response = client.get("/search?query=test&domain=example.com")
        assert response.status_code == 200
        data = response.json()
        assert data["filters"] is not None
        assert "domain" in data["filters"]
        assert data["filters"]["domain"] == "example.com"

    def test_search_with_time_filter(self):
        """Test search with time range filter"""
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        # Generate proper RFC3339 format with 'Z' suffix
        start_time = (now - datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-4] + 'Z'
        end_time = now.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-4] + 'Z'
        
        response = client.get(f"/search?query=test&start_time={start_time}&end_time={end_time}")
        assert response.status_code == 200
        data = response.json()
        assert data["filters"] is not None
        assert "time_range" in data["filters"]
        assert "start" in data["filters"]["time_range"]
        assert "end" in data["filters"]["time_range"]

    def test_search_with_collection(self):
        """Test search with specific collection"""
        response = client.get("/search?query=test&collection=test-collection")
        assert response.status_code == 200
        data = response.json()
        assert data["collection"] == "test-collection"

    def test_search_invalid_limit(self):
        """Test search with invalid limit"""
        # Test limit too low
        response = client.get("/search?query=test&limit=0")
        assert response.status_code == 422
        
        # Test limit too high
        response = client.get("/search?query=test&limit=11")
        assert response.status_code == 422
