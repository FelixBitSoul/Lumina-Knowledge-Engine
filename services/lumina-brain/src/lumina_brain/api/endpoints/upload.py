import logging
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Header, Depends
from celery.result import AsyncResult
from sqlalchemy.orm import Session

from lumina_brain.config.settings import settings
from lumina_brain.core.services.document import document_service
from lumina_brain.core.services.embedding import embedding_service
from lumina_brain.core.services.minio import minio_service
from lumina_brain.core.services.qdrant import qdrant_service
from lumina_brain.core.services.database import get_db
from lumina_brain.core.utils.path_utils import get_minio_object_path
from lumina_brain.core.models import Document, DocumentProcessing, SourceType, DocumentStatus
from lumina_brain.tasks.document_tasks import process_document

router = APIRouter()
logger = logging.getLogger(__name__)

# Use configuration from settings instead of hardcoded values


def _validate_file_upload(file: UploadFile, category: str, collection: Optional[str]) -> tuple[str, str, str]:
    """Validate file upload parameters and return processed values"""
    target_collection = collection or settings.upload.default_collection
    logger.info(f"[UPLOAD] Target collection: {target_collection}")

    if not file.filename:
        logger.error("[UPLOAD] File name is empty")
        raise HTTPException(status_code=400, detail="File name cannot be empty")

    file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
    logger.info(f"[UPLOAD] File extension: {file_extension}")

    if file_extension.lower() not in settings.upload.allowed_extensions:
        logger.error(f"[UPLOAD] Unsupported file type: {file_extension}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Allowed: {', '.join(settings.upload.allowed_extensions)}",
        )

    return target_collection, file_extension, file.filename


async def _read_and_validate_file(file: UploadFile) -> bytes:
    """Read file content and validate size"""
    try:
        logger.info(f"[UPLOAD] Reading file content...")
        file_content = await file.read()
        logger.info(f"[UPLOAD] File content read successfully, size: {len(file_content)} bytes")

        # Check file size
        if len(file_content) > settings.upload.max_file_size:
            logger.error(f"[UPLOAD] File too large: {len(file_content)} bytes")
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {settings.upload.max_file_size / (1024 * 1024)} MB.",
            )
        return file_content
    except Exception as e:
        logger.error(f"[UPLOAD] Failed to read file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")


def _process_file_content(file_content: bytes, file_extension: str) -> tuple[str, str, str]:
    """Process file content and generate document ID"""
    try:
        logger.info(f"[UPLOAD] Extracting text from file...")
        text = document_service.extract_text(file_content, file_extension)
        logger.info(f"[UPLOAD] Text extracted successfully, length: {len(text)} characters")
    except Exception as e:
        logger.error(f"[UPLOAD] Failed to extract text: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to extract text: {str(e)}")

    if not text or len(text.strip()) == 0:
        logger.error("[UPLOAD] File contains no extractable text")
        raise HTTPException(status_code=400, detail="File contains no extractable text")

    # Generate file_id based on content hash
    logger.info(f"[UPLOAD] Generating file_id from content hash...")
    file_id = document_service.generate_document_id(text)
    content_hash = document_service.generate_content_hash(text)
    logger.info(f"[UPLOAD] Generated file_id: {file_id}, content_hash: {content_hash}")

    return text, file_id, content_hash

def _check_document_exists(file_id: str, collection: str) -> None:
    """Check if document already exists in collection"""
    logger.info(f"[UPLOAD] Checking if document exists in collection: {collection}")
    if qdrant_service.check_document_exists(file_id, collection):
        logger.warning(f"[UPLOAD] Document already exists: {file_id}")
        raise HTTPException(
            status_code=409,
            detail=f"Document already exists: {file_id}",
        )
    logger.info(f"[UPLOAD] Document does not exist, proceeding with upload")

def _upload_to_minio(file_content: bytes, file_id: str, filename: str, collection: str) -> None:
    """Upload file to MinIO"""
    try:
        logger.info(f"[UPLOAD] Uploading file to MinIO...")
        minio_service.upload_bytes(file_content, file_id, filename, collection)
        logger.info(f"[UPLOAD] File uploaded to MinIO successfully")
    except Exception as e:
        logger.error(f"[UPLOAD] Failed to upload to MinIO: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload to MinIO: {str(e)}")

def _store_metadata_in_postgres(db: Session, file_id: str, filename: str, category: str, collection: str, content_hash: str) -> None:
    """Store document metadata in PostgreSQL"""
    try:
        logger.info(f"[UPLOAD] Storing metadata in PostgreSQL...")
        
        # Calculate minio path using utility function
        minio_path = get_minio_object_path(file_id, collection, "document", filename)
        
        # Create Document record
        document = Document(
            id=file_id,
            file_name=filename,
            category=category,
            collection=collection,
            source_type=SourceType.DOCUMENT,
            content_hash=content_hash,
            minio_path=minio_path
        )
        db.add(document)
        
        # Create DocumentProcessing record
        processing = DocumentProcessing(
            document_id=file_id,
            task_id=file_id,
            status=DocumentStatus.PENDING,
            progress=0,
            total=100
        )
        db.add(processing)
        
        # Commit changes
        db.commit()
        logger.info(f"[UPLOAD] Metadata stored in PostgreSQL successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"[UPLOAD] Failed to store metadata in PostgreSQL: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to store metadata: {str(e)}")

def _start_processing_task(file_id: str, collection: str, filename: str, category: str) -> str:
    """Start Celery task for document processing"""
    logger.info(f"[UPLOAD] Starting Celery task for file_id: {file_id}")
    task = process_document.apply_async(
        args=[file_id, collection, "document", filename, category],
        task_id=file_id,
    )
    logger.info(f"[UPLOAD] Celery task started successfully, task_id: {task.id}")
    return task.id

def _build_response_data(task_id: str, file_id: str, filename: str, category: str, collection: str) -> dict:
    """Build response data for upload endpoint"""
    # Use localhost instead of 0.0.0.0 for WebSocket URL
    websocket_host = "localhost" if settings.api.host == "0.0.0.0" else settings.api.host
    return {
        "task_id": task_id,
        "file_id": file_id,
        "file_name": filename,
        "category": category,
        "collection": collection,
        "status": "pending",
        "websocket_url": f"ws://{websocket_host}:{settings.api.port}/ws/{file_id}",
        "message": "Document uploaded successfully. Processing in background.",
    }


@router.post("", status_code=202)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    category: str = Form(..., description="Category for the document"),
    collection: Optional[str] = Form(None, description="Collection name (default: knowledge_base)"),
    authorization: Optional[str] = Header(None, description="API authorization token"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Upload document and start asynchronous processing.

    - Extracts text from the uploaded file
    - Generates SHA-256 hash of the content
    - Generates deterministic UUID from content (idempotent upload)
    - Uploads file to MinIO
    - Starts Celery task for processing (extraction, chunking, embedding, storage)

    Returns task_id and file_id for status tracking.
    """
    # API Authorization
    if authorization:
        # In a real implementation, you would validate the authorization token
        # For now, we'll just log it
        logger.info(f"[UPLOAD] Authorization token provided: {authorization[:20]}...")
    else:
        logger.info("[UPLOAD] No authorization token provided")

    logger.info(f"[UPLOAD] Starting upload process for file: {file.filename}, category: {category}, collection: {collection}")

    # Validate file upload
    target_collection, file_extension, filename = _validate_file_upload(file, category, collection)

    # Read and validate file
    file_content = await _read_and_validate_file(file)

    # Process file content
    text, file_id, content_hash = _process_file_content(file_content, file_extension)

    # Check if document exists
    _check_document_exists(file_id, target_collection)

    # Upload to MinIO
    _upload_to_minio(file_content, file_id, filename, target_collection)

    # Store metadata in PostgreSQL
    _store_metadata_in_postgres(db, file_id, filename, category, target_collection, content_hash)

    # Start processing task
    task_id = _start_processing_task(file_id, target_collection, filename, category)

    # Build response data
    response_data = _build_response_data(task_id, file_id, filename, category, target_collection)

    logger.info(f"[UPLOAD] Upload process completed successfully, response: {response_data}")
    return response_data


def _build_pending_response(task_id: str) -> dict:
    """Build response for pending task status"""
    return {
        "task_id": task_id,
        "status": "pending",
        "progress": 0,
        "message": "Task is waiting to be processed",
    }


def _build_progress_response(task_id: str, task_result) -> dict:
    """Build response for in-progress task status"""
    return {
        "task_id": task_id,
        "status": "processing",
        "progress": task_result.info.get("progress", 0),
        "total": task_result.info.get("total", 100),
        "current_step": task_result.info.get("status"),
    }


def _build_success_response(task_id: str, task_result) -> dict:
    """Build response for completed task status"""
    return {
        "task_id": task_id,
        "status": "completed",
        "result": task_result.result,
    }


def _build_failure_response(task_id: str, task_result) -> dict:
    """Build response for failed task status"""
    return {
        "task_id": task_id,
        "status": "failed",
        "error": str(task_result.info),
    }


def _build_default_response(task_id: str, task_result) -> dict:
    """Build default response for unknown task status"""
    return {
        "task_id": task_id,
        "status": task_result.state.lower(),
    }


# Mapping of task states to response builder functions
_TASK_STATUS_BUILDERS = {
    "PENDING": _build_pending_response,
    "PROGRESS": _build_progress_response,
    "SUCCESS": _build_success_response,
    "FAILURE": _build_failure_response,
}


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Get status of asynchronous document processing task.

    Returns current status and progress information.
    """
    logger.info(f"[TASK STATUS] Getting task status for task_id: {task_id}")
    task_result = AsyncResult(task_id)
    logger.info(f"[TASK STATUS] Task state: {task_result.state}")

    # Use dictionary dispatch to build response based on task state
    builder = _TASK_STATUS_BUILDERS.get(task_result.state, _build_default_response)
    response = builder(task_id, task_result)

    logger.info(f"[TASK STATUS] Response: {response}")
    return response
