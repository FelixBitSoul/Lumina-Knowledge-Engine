import hashlib
import uuid
from typing import BinaryIO

import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter

from lumina_brain.config.settings import settings


class DocumentService:
    """Service for handling document processing operations"""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        # Use values from settings or defaults
        self.chunk_size = chunk_size or getattr(settings.upload, 'chunk_size', 600)
        self.chunk_overlap = chunk_overlap or getattr(settings.upload, 'chunk_overlap', 60)
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        
        # Mapping of file extensions to extraction methods
        self._extractors = {
            "pdf": self.extract_text_from_pdf,
            "md": self.extract_text_from_markdown,
            "markdown": self.extract_text_from_markdown,
            "txt": self.extract_text_from_text,
            "text": self.extract_text_from_text,
        }

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file using PyMuPDF"""
        text_parts = []
        pdf_document = fitz.open(stream=file_content, filetype="pdf")

        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text_parts.append(page.get_text())

        pdf_document.close()
        return "\n".join(text_parts)

    def extract_text_from_markdown(self, file_content: bytes) -> str:
        """Extract text from Markdown file"""
        return file_content.decode("utf-8")

    def extract_text_from_text(self, file_content: bytes) -> str:
        """Extract text from plain text file"""
        return file_content.decode("utf-8")

    def extract_text(self, file_content: bytes, file_extension: str) -> str:
        """Extract text from file based on extension"""
        ext = file_extension.lower().lstrip(".")

        # Use dictionary dispatch to get the appropriate extractor
        extractor = self._extractors.get(ext)
        if extractor is None:
            raise ValueError(f"Unsupported file extension: {file_extension}")
        
        return extractor(file_content)

    def generate_content_hash(self, content: str) -> str:
        """Generate SHA-256 hash of content"""
        return hashlib.sha256(content.encode()).hexdigest()

    def generate_document_id(self, content: str) -> str:
        """Generate deterministic UUID from content for idempotent uploads"""
        hash_object = hashlib.sha256(content.encode())
        hash_hex = hash_object.hexdigest()[:32]
        return str(uuid.UUID(hash_hex))

    def split_text(self, text: str) -> list[str]:
        """Split text into chunks using RecursiveCharacterTextSplitter"""
        return self.text_splitter.split_text(text)


document_service = DocumentService()
