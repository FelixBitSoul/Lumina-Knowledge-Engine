import json
import pytest
from unittest.mock import patch, MagicMock
from lumina_brain.tasks.document_tasks import download_file_from_minio


class TestDocumentTasks:
    """Test document processing tasks"""

    @patch("minio.Minio")
    def test_download_file_from_minio_web(self, mock_minio_client):
        """Test downloading web snapshot from MinIO"""
        # Mock MinIO client
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"url": "https://example.com", "content": "test"}'
        mock_minio_instance = MagicMock()
        mock_minio_instance.get_object.return_value = mock_response
        mock_minio_client.return_value = mock_minio_instance
        
        # Call the function
        content = download_file_from_minio("test-hash", "test-collection", "web")
        
        # Verify content
        assert content == b'{"url": "https://example.com", "content": "test"}'
        
        # Verify MinIO get_object was called with correct path
        mock_minio_instance.get_object.assert_called_once()
        call_args = mock_minio_instance.get_object.call_args
        assert call_args[1]["object_name"] == "raw/collections/test-collection/web/test-hash.json"

    @patch("minio.Minio")
    def test_download_file_from_minio_document(self, mock_minio_client):
        """Test downloading regular document from MinIO"""
        # Mock MinIO client
        mock_response = MagicMock()
        mock_response.read.return_value = b"test content"
        mock_minio_instance = MagicMock()
        mock_minio_instance.get_object.return_value = mock_response
        mock_minio_client.return_value = mock_minio_instance
        
        # Call the function
        content = download_file_from_minio("test-hash", "test-collection", "document", "test.txt")
        
        # Verify content
        assert content == b"test content"
        
        # Verify MinIO get_object was called with correct path
        mock_minio_instance.get_object.assert_called_once()
        call_args = mock_minio_instance.get_object.call_args
        assert call_args[1]["object_name"] == "raw/collections/test-collection/docs/test-hash.txt"

    @patch("minio.Minio")
    def test_download_file_from_minio_document(self, mock_minio_client):
        """Test downloading regular document from MinIO"""
        # Mock MinIO client
        mock_response = MagicMock()
        mock_response.read.return_value = b"test content"
        mock_minio_instance = MagicMock()
        mock_minio_instance.get_object.return_value = mock_response
        mock_minio_client.return_value = mock_minio_instance
        
        # Call the function
        content = download_file_from_minio("test-hash", "test-collection", "document", "test.txt")
        
        # Verify content
        assert content == b"test content"
        
        # Verify MinIO get_object was called with correct path
        mock_minio_instance.get_object.assert_called_once()
        call_args = mock_minio_instance.get_object.call_args
        assert call_args[1]["object_name"] == "raw/collections/test-collection/docs/test-hash.txt"
