import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from lumina_brain.core.services.database import get_db
from lumina_brain.core.services.minio import MinIOService
from lumina_brain.core.services.qdrant import QdrantService
from lumina_brain.core.models import Document, DocumentMetadata, DocumentProcessing, DocumentStatus
from lumina_brain.config.settings import settings

# Initialize services
minio_service = MinIOService()
qdrant_service = QdrantService()

router = APIRouter()
logger = logging.getLogger(__name__)


def _build_document_response(doc):
    """Build document response data"""
    doc_data = {
        "id": doc.id,
        "file_name": doc.file_name,
        "category": doc.category,
        "collection": doc.collection,
        "source_type": doc.source_type.value,
        "content_hash": doc.content_hash,
        "minio_path": doc.minio_path,
        "created_at": doc.created_at,
        "updated_at": doc.updated_at,
        "processing": None
    }
    
    # Add processing status if available
    if doc.processing:
        doc_data["processing"] = {
            "status": doc.processing.status.value,
            "progress": doc.processing.progress,
            "total": doc.processing.total,
            "current_step": doc.processing.current_step,
            "error_message": doc.processing.error_message,
            "chunks_created": doc.processing.chunks_created,
            "started_at": doc.processing.started_at,
            "completed_at": doc.processing.completed_at
        }
    
    return doc_data


def _build_list_query(db, collection, category, status):
    """Build query for listing documents"""
    query = db.query(Document).outerjoin(DocumentProcessing)
    
    # Apply filters
    if collection:
        query = query.filter(Document.collection == collection)
    if category:
        query = query.filter(Document.category == category)
    if status:
        query = query.filter(DocumentProcessing.status == status)
    
    return query


@router.get("", response_model=Dict[str, Any])
def list_documents(
    collection: Optional[str] = Query(None, description="Filter by collection"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[DocumentStatus] = Query(None, description="Filter by processing status"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db),
):
    """
    List documents with optional filtering and pagination
    """
    logger.info(f"[DOCUMENTS] Listing documents with filters: collection={collection}, category={category}, status={status}, limit={limit}, offset={offset}")
    
    # Build query
    query = _build_list_query(db, collection, category, status)
    
    # Get total count
    total_count = query.count()
    
    # Get paginated results
    documents = query.limit(limit).offset(offset).all()
    
    # Build response
    result = [_build_document_response(doc) for doc in documents]
    
    # Calculate pagination info
    page = offset // limit + 1
    total_pages = (total_count + limit - 1) // limit
    
    # Return paginated response
    response = {
        "files": result,
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "page": page,
        "total_pages": total_pages
    }
    
    logger.info(f"[DOCUMENTS] Found {len(result)} documents out of {total_count} total")
    return response


def _build_document_detail_response(document):
    """Build detailed document response with metadata"""
    # Start with basic document data
    result = _build_document_response(document)
    
    # Add metadata
    result["metadata"] = []
    for meta in document.metadata_items:
        result["metadata"].append({
            "key": meta.key,
            "value": meta.value,
            "created_at": meta.created_at
        })
    
    return result


def _get_document_by_id(db, document_id):
    """Get document by ID with error handling"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")
    return document


@router.get("/{document_id}", response_model=dict)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    """
    Get document by ID
    """
    logger.info(f"[DOCUMENTS] Getting document by ID: {document_id}")
    
    # Get document
    document = _get_document_by_id(db, document_id)
    
    # Build response
    result = _build_document_detail_response(document)
    
    logger.info(f"[DOCUMENTS] Found document: {document.file_name}")
    return result


@router.post("/{document_id}/metadata")
def add_document_metadata(
    document_id: str,
    key: str,
    value: str,
    db: Session = Depends(get_db),
):
    """
    Add metadata to document
    """
    logger.info(f"[DOCUMENTS] Adding metadata to document {document_id}: {key} = {value}")
    
    # Get document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")
    
    # Check if metadata already exists
    existing_meta = db.query(DocumentMetadata).filter(
        and_(
            DocumentMetadata.document_id == document_id,
            DocumentMetadata.key == key
        )
    ).first()
    
    if existing_meta:
        # Update existing metadata
        existing_meta.value = value
        db.commit()
        logger.info(f"[DOCUMENTS] Updated existing metadata: {key} = {value}")
    else:
        # Add new metadata
        new_meta = DocumentMetadata(
            document_id=document_id,
            key=key,
            value=value
        )
        db.add(new_meta)
        db.commit()
        logger.info(f"[DOCUMENTS] Added new metadata: {key} = {value}")
    
    return {"message": "Metadata added successfully"}


@router.delete("/{document_id}/metadata/{key}")
def delete_document_metadata(
    document_id: str,
    key: str,
    db: Session = Depends(get_db),
):
    """
    Delete metadata from document
    """
    logger.info(f"[DOCUMENTS] Deleting metadata from document {document_id}: {key}")
    
    # Get metadata
    metadata = db.query(DocumentMetadata).filter(
        and_(
            DocumentMetadata.document_id == document_id,
            DocumentMetadata.key == key
        )
    ).first()
    
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Metadata not found: {key}")
    
    # Delete metadata
    db.delete(metadata)
    db.commit()
    logger.info(f"[DOCUMENTS] Deleted metadata: {key}")
    
    return {"message": "Metadata deleted successfully"}


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    collection: str = Query(..., description="Qdrant collection name"),
    filename: str = Query(..., description="Original filename"),
    db: Session = Depends(get_db),
):
    """
    Delete document from Qdrant and MinIO
    """
    logger.info(f"[DOCUMENTS] Deleting document: {document_id}, collection: {collection}, filename: {filename}")
    
    # Get document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")
    
    try:
        # Delete from Qdrant
        logger.info(f"[DOCUMENTS] Deleting vectors from Qdrant for document: {document_id}")
        qdrant_service.delete_by_file_id(document_id, collection)
        logger.info(f"[DOCUMENTS] Vectors deleted from Qdrant successfully")
        
        # Delete from MinIO
        logger.info(f"[DOCUMENTS] Deleting file from MinIO: {filename}")
        minio_service.delete_file(document_id, filename, collection)
        logger.info(f"[DOCUMENTS] File deleted from MinIO successfully")
        
        # Delete from database (cascades to metadata and processing)
        db.delete(document)
        db.commit()
        logger.info(f"[DOCUMENTS] Deleted document from database: {document_id}")
        
        return {"file_id": document_id, "status": "deleted", "message": "Document deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"[DOCUMENTS] Failed to delete document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
