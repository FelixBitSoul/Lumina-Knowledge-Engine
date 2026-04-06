import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from lumina_brain.main import app

client = TestClient(app)


class TestIngestAPI:
    """Test ingest API endpoints"""

    @patch("lumina_brain.api.endpoints.ingest.minio_service")
    @patch("lumina_brain.api.endpoints.ingest.process_document")
    def test_ingest_web_snapshot_success(self, mock_process, mock_minio):
        """Test successful web snapshot ingestion"""
        # Mock MinIO service
        mock_minio.upload_web_snapshot.return_value = ("raw/collections/test/web/test-hash.json", "test-hash")
        
        # Mock Celery task
        mock_task = MagicMock()
        mock_task.id = "task-123"
        mock_process.delay.return_value = mock_task

        # Test data
        test_data = {
            "url": "https://example.com",
            "title": "Test Page",
            "content": "This is a test page content"
        }

        response = client.post("/ingest", json=test_data, params={"collection": "test"})

        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert result["task_id"] == "task-123"
        assert result["minio_path"] == "raw/collections/test/web/test-hash.json"
        
        # Verify MinIO upload was called
        mock_minio.upload_web_snapshot.assert_called_once_with(
            url="https://example.com",
            title="Test Page",
            content="This is a test page content",
            collection_name="test"
        )
        
        # Verify Celery task was called
        mock_process.delay.assert_called_once_with(
            file_id="test-hash",
            collection="test",
            source_type="web"
        )

    @patch("lumina_brain.api.endpoints.ingest.minio_service")
    def test_ingest_minio_error(self, mock_minio):
        """Test ingest fails when MinIO upload fails"""
        # Mock MinIO service to raise error
        mock_minio.upload_web_snapshot.side_effect = Exception("MinIO upload failed")

        # Test data
        test_data = {
            "url": "https://example.com",
            "title": "Test Page",
            "content": "This is a test page content"
        }

        response = client.post("/ingest", json=test_data)

        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "error"
        assert "MinIO upload failed" in result["message"]

    def test_ingest_missing_fields(self):
        """Test ingest with missing required fields"""
        # Test missing content
        test_data = {
            "url": "https://example.com",
            "title": "Test Page"
        }
        response = client.post("/ingest", json=test_data)
        assert response.status_code == 422

        # Test missing url
        test_data = {
            "title": "Test Page",
            "content": "This is a test page content"
        }
        response = client.post("/ingest", json=test_data)
        assert response.status_code == 422
