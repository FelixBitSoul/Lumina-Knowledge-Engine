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
            minio_service.delete_file(file_id, filename, collection)

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
    collection: str = Query("knowledge_base", description="Collection name"),
    expiry: int = Query(600, description="Expiry time in seconds (max: 3600)"),
):
    """
    Generate presigned URL for document preview

    - Generates a temporary URL for accessing the original document
    - URL expires after the specified time

    Args:
        file_id: Document ID (based on content hash)
        filename: Original filename
        collection: Qdrant collection name
        expiry: Expiry time in seconds (default: 600, max: 3600)
    """
    # Limit maximum expiry to 1 hour
    if expiry > 3600:
        expiry = 3600

    try:
        presigned_url = minio_service.generate_presigned_url(
            file_id=file_id,
            filename=filename,
            collection_name=collection,
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


@router.get("/chunks/{chunk_id}")
async def get_chunk_details(
    chunk_id: str,
    collection: str = Query("knowledge_base", description="Collection name"),
):
    """
    Get detailed information about a specific chunk.
    Returns chunk metadata including full content, score, original payload, and source file information.
    """
    try:
        # Get chunk by ID from Qdrant
        # Convert chunk_id to integer (since Qdrant uses integer IDs)
        try:
            point_id = int(chunk_id)
        except ValueError:
            # If chunk_id is not an integer, try to generate a hash from it
            import hashlib
            point_id = int(hashlib.md5(chunk_id.encode()).hexdigest(), 16) % 10**18

        # Query Qdrant for the specific point
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        # First, try to get the point directly by ID
        try:
            search_result = qdrant_service.client.retrieve(
                collection_name=collection,
                ids=[point_id],
                with_payload=True,
                with_vectors=False
            )

            if search_result:
                point = search_result[0]
                payload = point.payload or {}

                return {
                    "chunk_id": str(point.id),
                    "content": payload.get("content", "No content"),
                    "score": 0.0,  # Direct retrieval doesn't return score
                    "payload": payload,
                    "source_file": {
                        "file_id": payload.get("file_id", "Unknown"),
                        "file_name": payload.get("file_name", "Unknown"),
                        "category": payload.get("category", "Unknown")
                    }
                }
        except Exception as e:
            # If direct retrieval fails, try searching with a filter
            pass

        # If direct retrieval fails, search with a filter
        search_result = qdrant_service.client.query_points(
            collection_name=collection,
            query=[0.0] * 384,  # Dummy vector
            limit=1,
            with_payload=True,
            with_vectors=False,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="file_id",
                        match=MatchValue(value=chunk_id)
                    )
                ]
            )
        )

        if search_result.points:
            point = search_result.points[0]
            payload = point.payload or {}

            return {
                "chunk_id": str(point.id),
                "content": payload.get("content", "No content"),
                "score": point.score,
                "payload": payload,
                "source_file": {
                    "file_id": payload.get("file_id", "Unknown"),
                    "file_name": payload.get("file_name", "Unknown"),
                    "category": payload.get("category", "Unknown")
                }
            }
        else:
            raise HTTPException(status_code=404, detail=f"Chunk not found: {chunk_id}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_files(
    collection: str = Query("knowledge_base", description="Collection name"),
    limit: int = Query(20, description="Maximum number of files to return"),
    start_after: Optional[str] = Query(None, description="Object name to start after (for pagination)"),
):
    """
    List files in a collection with pagination
    Returns a list of files with metadata including file_id, filename, size, uploaded_at, and type
    """
    try:
        # Get files from MinIO with pagination
        files, next_marker = minio_service.list_files(collection, limit, start_after)

        return {
            "collection": collection,
            "files": files,
            "count": len(files),
            "next_marker": next_marker
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
