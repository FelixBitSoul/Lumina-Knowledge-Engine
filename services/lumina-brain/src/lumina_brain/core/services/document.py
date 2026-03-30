import hashlib
import uuid
from typing import BinaryIO

import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentService:
    """Service for handling document processing operations"""

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 60):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

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

        if ext == "pdf":
            return self.extract_text_from_pdf(file_content)
        elif ext in ("md", "markdown"):
            return self.extract_text_from_markdown(file_content)
        elif ext in ("txt", "text"):
            return self.extract_text_from_text(file_content)
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")

    def generate_content_hash(self, content: str) -> str:
        """Generate SHA-256 hash of content"""
        return hashlib.sha256(content.encode()).hexdigest()

    def generate_document_id(self, file_name: str) -> str:
        """Generate deterministic UUID from file name for idempotent uploads"""
        hash_object = hashlib.sha256(file_name.encode())
        hash_hex = hash_object.hexdigest()[:32]
        return str(uuid.UUID(hash_hex))

    def split_text(self, text: str) -> list[str]:
        """Split text into chunks using RecursiveCharacterTextSplitter"""
        return self.text_splitter.split_text(text)


document_service = DocumentService()
