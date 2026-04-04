from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta

from lumina_brain.core.services.minio import minio_service
from lumina_brain.core.services.qdrant import qdrant_service

router = APIRouter()


@router.delete("/{file_id}")
async def delete_document(
    file_id: str,
    collection: str = Query("knowledge_base", description="Collection name"),
    filename: Optional[str] = Query(None, description="Original filename"),
):
    """
    Delete document from Qdrant and MinIO

    - Deletes all chunks from Qdrant with the specified file_id
    - Deletes the original file from MinIO (if filename is provided)

    Args:
        file_id: Document ID (based on content hash)
        collection: Qdrant collection name
        filename: Original filename (required for MinIO deletion)
    """
    try:
        # Delete from Qdrant
        qdrant_service.delete_by_file_id(file_id, collection)

        # Delete from MinIO if filename is provided
        if filename:
            minio_service.delete_file(file_id, filename)

        return {
            "file_id": file_id,
            "status": "deleted",
            "message": "Document deleted successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/preview-url")
async def get_document_preview_url(
    file_id: str,
    filename: str = Query(..., description="Original filename"),
    expiry: int = Query(600, description="Expiry time in seconds (max: 3600)"),
):
    """
    Generate presigned URL for document preview

    - Generates a temporary URL for accessing the original document
    - URL expires after the specified time

    Args:
        file_id: Document ID (based on content hash)
        filename: Original filename
        expiry: Expiry time in seconds (default: 600, max: 3600)
    """
    # Limit maximum expiry to 1 hour
    if expiry > 3600:
        expiry = 3600

    try:
        presigned_url = minio_service.generate_presigned_url(
            file_id=file_id,
            filename=filename,
            expiry=expiry,
        )

        return {
            "file_id": file_id,
            "filename": filename,
            "preview_url": presigned_url,
            "expires_in": expiry,
            "expires_at": (datetime.now() + timedelta(seconds=expiry)).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/status")
async def get_document_status(
    file_id: str,
    collection: str = Query("knowledge_base", description="Collection name"),
):
    """
    Check if document exists in Qdrant

    Args:
        file_id: Document ID (based on content hash)
        collection: Qdrant collection name
    """
    exists = qdrant_service.check_document_exists(file_id, collection)

    if exists:
        return {
            "file_id": file_id,
            "status": "completed",
            "message": "Document has been indexed",
        }
    else:
        return {
            "file_id": file_id,
            "status": "not_found",
            "message": "Document not found in the index",
        }
