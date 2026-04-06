import io
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from lumina_brain.main import app


client = TestClient(app)


class TestUploadAPI:
    """Test upload API endpoints"""

    def test_upload_unsupported_file_type(self):
        """Test upload with unsupported file type"""
        files = {"file": ("test.exe", io.BytesIO(b"content"), "application/octet-stream")}
        data = {"category": "test"}

        response = client.post("/upload", files=files, data=data)
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]

    def test_upload_missing_file(self):
        """Test upload without file"""
        data = {"category": "test"}

        response = client.post("/upload", data=data)
        assert response.status_code == 422

    def test_upload_missing_category(self):
        """Test upload without category"""
        files = {"file": ("test.pdf", io.BytesIO(b"content"), "application/pdf")}

        response = client.post("/upload", files=files)
        assert response.status_code == 422

    @patch("lumina_brain.api.endpoints.upload.document_service")
    @patch("lumina_brain.api.endpoints.upload.qdrant_service")
    @patch("lumina_brain.api.endpoints.upload.embedding_service")
    def test_upload_markdown_success(self, mock_embedding, mock_qdrant, mock_doc):
        """Test successful markdown upload"""
        mock_doc.extract_text.return_value = "Test markdown content"
        mock_doc.generate_content_hash.return_value = "abc123"
        mock_doc.generate_document_id.return_value = "doc-uuid-123"
        mock_doc.split_text.return_value = ["chunk1", "chunk2"]
        mock_embedding.encode.return_value = [0.1] * 384
        mock_qdrant.check_document_exists.return_value = False

        files = {"file": ("test.md", io.BytesIO(b"# Test"), "text/markdown")}
        data = {"category": "documentation"}

        response = client.post("/upload", files=files, data=data)

        assert response.status_code == 202
        result = response.json()
        assert result["file_id"] == "doc-uuid-123"
        assert result["file_name"] == "test.md"
        assert result["category"] == "documentation"
        assert result["collection"] == "knowledge_base"
        assert result["status"] == "pending"

    @patch("lumina_brain.api.endpoints.upload.document_service")
    @patch("lumina_brain.api.endpoints.upload.qdrant_service")
    @patch("lumina_brain.api.endpoints.upload.embedding_service")
    def test_upload_text_file_success(self, mock_embedding, mock_qdrant, mock_doc):
        """Test successful text file upload"""
        mock_doc.extract_text.return_value = "Plain text content"
        mock_doc.generate_content_hash.return_value = "def456"
        mock_doc.generate_document_id.return_value = "doc-uuid-456"
        mock_doc.split_text.return_value = ["Plain text content"]
        mock_embedding.encode.return_value = [0.2] * 384
        mock_qdrant.check_document_exists.return_value = False

        files = {"file": ("readme.txt", io.BytesIO(b"Plain text content"), "text/plain")}
        data = {"category": "notes"}

        response = client.post("/upload", files=files, data=data)

        assert response.status_code == 202
        result = response.json()
        assert result["file_name"] == "readme.txt"
        assert result["category"] == "notes"
        assert result["collection"] == "knowledge_base"
        assert result["status"] == "pending"

    @patch("lumina_brain.api.endpoints.upload.document_service")
    def test_upload_empty_content(self, mock_doc):
        """Test upload with empty content"""
        mock_doc.extract_text.return_value = ""

        files = {"file": ("empty.md", io.BytesIO(b""), "text/markdown")}
        data = {"category": "test"}

        response = client.post("/upload", files=files, data=data)
        assert response.status_code == 400
        assert "no extractable text" in response.json()["detail"]

    @patch("lumina_brain.api.endpoints.upload.document_service")
    def test_upload_extraction_error(self, mock_doc):
        """Test upload when text extraction fails"""
        mock_doc.extract_text.side_effect = ValueError("Invalid PDF")

        files = {"file": ("corrupt.pdf", io.BytesIO(b"corrupt"), "application/pdf")}
        data = {"category": "test"}

        response = client.post("/upload", files=files, data=data)
        assert response.status_code == 400
        assert "Failed to extract text" in response.json()["detail"]

    @patch("lumina_brain.api.endpoints.upload.document_service")
    @patch("lumina_brain.api.endpoints.upload.qdrant_service")
    @patch("lumina_brain.api.endpoints.upload.embedding_service")
    def test_upload_idempotent(self, mock_embedding, mock_qdrant, mock_doc):
        """Test that same filename generates same document_id (idempotent)"""
        mock_doc.extract_text.return_value = "Content"
        mock_doc.generate_content_hash.return_value = "hash123"
        mock_doc.generate_document_id.return_value = "same-uuid"
        mock_doc.split_text.return_value = ["chunk1"]
        mock_embedding.encode.return_value = [0.1] * 384
        mock_qdrant.check_document_exists.return_value = False

        files = {"file": ("document.pdf", io.BytesIO(b"PDF content"), "application/pdf")}
        data = {"category": "test"}

        response1 = client.post("/upload", files=files, data=data)
        response2 = client.post("/upload", files=files, data=data)

        assert response1.json()["file_id"] == response2.json()["file_id"]

    @patch("lumina_brain.api.endpoints.upload.document_service")
    @patch("lumina_brain.api.endpoints.upload.qdrant_service")
    @patch("lumina_brain.api.endpoints.upload.embedding_service")
    def test_upload_with_custom_collection(self, mock_embedding, mock_qdrant, mock_doc):
        """Test upload to custom collection"""
        mock_doc.extract_text.return_value = "Test content"
        mock_doc.generate_content_hash.return_value = "hash789"
        mock_doc.generate_document_id.return_value = "doc-uuid-789"
        mock_doc.split_text.return_value = ["chunk1"]
        mock_embedding.encode.return_value = [0.1] * 384
        mock_qdrant.check_document_exists.return_value = False

        files = {"file": ("test.txt", io.BytesIO(b"Content"), "text/plain")}
        data = {"category": "custom", "collection": "my_collection"}

        response = client.post("/upload", files=files, data=data)

        assert response.status_code == 202
        result = response.json()
        assert result["collection"] == "my_collection"
        assert result["status"] == "pending"

    @patch("lumina_brain.api.endpoints.upload.document_service")
    @patch("lumina_brain.api.endpoints.upload.qdrant_service")
    @patch("lumina_brain.api.endpoints.upload.embedding_service")
    def test_upload_multiple_chunks(self, mock_embedding, mock_qdrant, mock_doc):
        """Test upload creates correct number of chunks"""
        long_content = "This is a long document. " * 100
        mock_doc.extract_text.return_value = long_content
        mock_doc.generate_content_hash.return_value = "longhash"
        mock_doc.generate_document_id.return_value = "longdoc"
        mock_doc.split_text.return_value = [f"chunk{i}" for i in range(10)]
        mock_embedding.encode.return_value = [0.1] * 384
        mock_qdrant.check_document_exists.return_value = False

        files = {"file": ("long.md", io.BytesIO(b"content"), "text/markdown")}
        data = {"category": "test"}

        response = client.post("/upload", files=files, data=data)

        assert response.status_code == 202
        result = response.json()
        assert result["file_id"] == "longdoc"
        assert result["status"] == "pending"

    @patch("lumina_brain.api.endpoints.upload.document_service")
    @patch("lumina_brain.api.endpoints.upload.qdrant_service")
    @patch("lumina_brain.api.endpoints.upload.embedding_service")
    def test_upload_embedding_failure(self, mock_embedding, mock_qdrant, mock_doc):
        """Test upload handles embedding generation failure"""
        mock_doc.extract_text.return_value = "Content"
        mock_doc.generate_content_hash.return_value = "hash"
        mock_doc.generate_document_id.return_value = "doc-id"
        mock_doc.split_text.return_value = ["chunk1"]
        mock_embedding.encode.side_effect = Exception("Model error")
        mock_qdrant.check_document_exists.return_value = False

        files = {"file": ("test.txt", io.BytesIO(b"Content"), "text/plain")}
        data = {"category": "test"}

        response = client.post("/upload", files=files, data=data)
        assert response.status_code == 202
        result = response.json()
        assert result["file_id"] == "doc-id"
        assert result["status"] == "pending"
