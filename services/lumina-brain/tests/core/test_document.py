import hashlib
import uuid
import pytest
from lumina_brain.core.services.document import DocumentService


class TestDocumentService:
    """Test document processing service"""

    def setup_method(self):
        """Setup test fixtures"""
        self.service = DocumentService(chunk_size=600, chunk_overlap=60)

    def test_generate_content_hash(self):
        """Test SHA-256 hash generation"""
        content = "This is a test document content"
        hash_result = self.service.generate_content_hash(content)

        assert isinstance(hash_result, str)
        assert len(hash_result) == 64
        expected = hashlib.sha256(content.encode()).hexdigest()
        assert hash_result == expected

    def test_generate_content_hash_deterministic(self):
        """Test that hash generation is deterministic"""
        content = "Same content twice"
        hash1 = self.service.generate_content_hash(content)
        hash2 = self.service.generate_content_hash(content)

        assert hash1 == hash2

    def test_generate_document_id_from_filename(self):
        """Test deterministic UUID generation from filename"""
        filename = "test_document.pdf"
        doc_id = self.service.generate_document_id(filename)

        assert isinstance(doc_id, str)
        uuid.UUID(doc_id)

    def test_generate_document_id_deterministic(self):
        """Test that document ID is deterministic (idempotent)"""
        filename = "same_file.pdf"
        id1 = self.service.generate_document_id(filename)
        id2 = self.service.generate_document_id(filename)

        assert id1 == id2

    def test_generate_document_id_different_files(self):
        """Test that different files get different IDs"""
        id1 = self.service.generate_document_id("file1.pdf")
        id2 = self.service.generate_document_id("file2.pdf")

        assert id1 != id2

    def test_split_text(self):
        """Test text splitting into chunks"""
        text = "This is a test document. " * 100
        chunks = self.service.split_text(text)

        assert isinstance(chunks, list)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 600

    def test_split_text_small_content(self):
        """Test splitting small content (smaller than chunk_size)"""
        text = "Short content"
        chunks = self.service.split_text(text)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_split_text_empty_content(self):
        """Test splitting empty content returns empty list"""
        chunks = self.service.split_text("")

        assert len(chunks) == 0

    def test_extract_text_from_markdown(self):
        """Test markdown text extraction"""
        content = b"# Hello World\n\nThis is a test."
        result = self.service.extract_text_from_markdown(content)

        assert isinstance(result, str)
        assert "Hello World" in result
        assert "This is a test" in result

    def test_extract_text_from_text(self):
        """Test plain text extraction"""
        content = b"Just plain text content"
        result = self.service.extract_text_from_text(content)

        assert result == "Just plain text content"

    def test_extract_text_unsupported_extension(self):
        """Test unsupported file extension raises error"""
        with pytest.raises(ValueError) as exc_info:
            self.service.extract_text(b"content", "xyz")
        assert "Unsupported file extension" in str(exc_info.value)

    def test_extract_text_various_extensions(self):
        """Test various supported extensions"""
        content = b"test content"

        assert self.service.extract_text(content, ".md") == "test content"
        assert self.service.extract_text(content, "markdown") == "test content"
        assert self.service.extract_text(content, ".txt") == "test content"
        assert self.service.extract_text(content, "text") == "test content"

    def test_custom_chunk_size(self):
        """Test custom chunk size configuration"""
        service = DocumentService(chunk_size=100, chunk_overlap=10)
        text = "A" * 200

        chunks = service.split_text(text)

        for chunk in chunks:
            assert len(chunk) <= 100

    def test_chunk_overlap(self):
        """Test that chunks have overlap content"""
        service = DocumentService(chunk_size=50, chunk_overlap=10)
        text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 10

        chunks = service.split_text(text)

        if len(chunks) > 1:
            first_chunk_end = chunks[0][-10:]
            second_chunk_start = chunks[1][:10]
            assert first_chunk_end == second_chunk_start
