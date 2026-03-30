import hashlib
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from qdrant_client.models import Distance, PointStruct, VectorParams

from lumina_brain.config.settings import settings
from lumina_brain.core.services.document import document_service
from lumina_brain.core.services.embedding import embedding_service
from lumina_brain.core.services.qdrant import qdrant_service

router = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "md", "markdown", "txt", "text"}
COLLECTION_NAME = "documents"


def _ensure_collection(collection_name: str):
    """Create collection with payload indexes if it doesn't exist"""
    try:
        qdrant_service.client.get_collection(collection_name=collection_name)
    except Exception:
        qdrant_service.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

        qdrant_service.client.create_payload_index(
            collection_name=collection_name,
            field_name="file_name",
            field_schema="keyword",
        )

        qdrant_service.client.create_payload_index(
            collection_name=collection_name,
            field_name="category",
            field_schema="keyword",
        )

        qdrant_service.client.create_payload_index(
            collection_name=collection_name,
            field_name="content_hash",
            field_schema="keyword",
        )


@router.post("")
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    category: str = Form(..., description="Category for the document"),
    collection: Optional[str] = Form(None, description="Collection name (default: documents)"),
) -> dict:
    """
    Upload and index a document (PDF, Markdown, or Text).

    - Extracts text from the uploaded file
    - Generates SHA-256 hash of the content
    - Generates deterministic UUID from filename (idempotent upload)
    - Splits text into chunks (chunk_size=600, overlap=60)
    - Stores chunks in Qdrant with metadata

    Returns the number of chunks created and the document_id.
    """
    target_collection = collection or COLLECTION_NAME
    _ensure_collection(target_collection)

    if not file.filename:
        raise HTTPException(status_code=400, detail="File name cannot be empty")

    file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
    if file_extension.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

    try:
        text = document_service.extract_text(file_content, file_extension)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text: {str(e)}")

    if not text or len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="File contains no extractable text")

    content_hash = document_service.generate_content_hash(text)
    document_id = document_service.generate_document_id(file.filename)

    chunks = document_service.split_text(text)

    points = []
    for i, chunk in enumerate(chunks):
        try:
            vector = embedding_service.encode(chunk)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {str(e)}")

        # Generate integer ID by hashing the chunk content
        chunk_content = f"{document_id}_{i}_{chunk[:100]}"
        chunk_id = int(hashlib.sha256(chunk_content.encode()).hexdigest(), 16) % 10**18
        points.append(
            PointStruct(
                id=chunk_id,
                vector=vector,
                payload={
                    "file_name": file.filename,
                    "content_hash": content_hash,
                    "category": category,
                    "content": chunk,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "document_id": document_id,
                },
            )
        )

    try:
        qdrant_service.client.upsert(
            collection_name=target_collection,
            points=points,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store in Qdrant: {str(e)}")

    return {
        "document_id": document_id,
        "chunks_created": len(chunks),
        "file_name": file.filename,
        "category": category,
        "content_hash": content_hash,
        "collection": target_collection,
    }
