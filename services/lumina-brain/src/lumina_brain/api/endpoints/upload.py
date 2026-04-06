import logging
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Header
from celery.result import AsyncResult

from lumina_brain.config.settings import settings
from lumina_brain.core.services.document import document_service
from lumina_brain.core.services.embedding import embedding_service
from lumina_brain.core.services.minio import minio_service
from lumina_brain.core.services.qdrant import qdrant_service
from lumina_brain.tasks.document_tasks import process_document

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"pdf", "md", "markdown", "txt", "text"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
COLLECTION_NAME = "knowledge_base"


@router.post("", status_code=202)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    category: str = Form(..., description="Category for the document"),
    collection: Optional[str] = Form(None, description="Collection name (default: knowledge_base)"),
    authorization: Optional[str] = Header(None, description="API authorization token"),
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

    target_collection = collection or COLLECTION_NAME
    logger.info(f"[UPLOAD] Target collection: {target_collection}")

    if not file.filename:
        logger.error("[UPLOAD] File name is empty")
        raise HTTPException(status_code=400, detail="File name cannot be empty")

    file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
    logger.info(f"[UPLOAD] File extension: {file_extension}")

    if file_extension.lower() not in ALLOWED_EXTENSIONS:
        logger.error(f"[UPLOAD] Unsupported file type: {file_extension}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    try:
        logger.info(f"[UPLOAD] Reading file content...")
        file_content = await file.read()
        logger.info(f"[UPLOAD] File content read successfully, size: {len(file_content)} bytes")

        # Check file size
        if len(file_content) > MAX_FILE_SIZE:
            logger.error(f"[UPLOAD] File too large: {len(file_content)} bytes")
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024)} MB.",
            )
    except Exception as e:
        logger.error(f"[UPLOAD] Failed to read file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

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

    # Check if document already exists
    logger.info(f"[UPLOAD] Checking if document exists in collection: {target_collection}")
    if qdrant_service.check_document_exists(file_id, target_collection):
        logger.warning(f"[UPLOAD] Document already exists: {file_id}")
        raise HTTPException(
            status_code=409,
            detail=f"Document already exists: {file_id}",
        )
    logger.info(f"[UPLOAD] Document does not exist, proceeding with upload")

    # Upload file to MinIO
    try:
        logger.info(f"[UPLOAD] Uploading file to MinIO...")
        minio_service.upload_bytes(file_content, file_id, file.filename, target_collection)
        logger.info(f"[UPLOAD] File uploaded to MinIO successfully")
    except Exception as e:
        logger.error(f"[UPLOAD] Failed to upload to MinIO: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload to MinIO: {str(e)}")

    # Start Celery task
    logger.info(f"[UPLOAD] Starting Celery task for file_id: {file_id}")
    task = process_document.apply_async(
        args=[file_id, target_collection, "document", file.filename, category],
        task_id=file_id,
    )
    logger.info(f"[UPLOAD] Celery task started successfully, task_id: {task.id}")

    # Use localhost instead of 0.0.0.0 for WebSocket URL
    websocket_host = "localhost" if settings.api.host == "0.0.0.0" else settings.api.host
    response_data = {
        "task_id": task.id,
        "file_id": file_id,
        "file_name": file.filename,
        "category": category,
        "collection": target_collection,
        "status": "pending",
        "websocket_url": f"ws://{websocket_host}:{settings.api.port}/ws/{file_id}",
        "message": "Document uploaded successfully. Processing in background.",
    }
    logger.info(f"[UPLOAD] Upload process completed successfully, response: {response_data}")

    return response_data


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Get status of asynchronous document processing task.

    Returns current status and progress information.
    """
    logger.info(f"[TASK STATUS] Getting task status for task_id: {task_id}")
    task_result = AsyncResult(task_id)
    logger.info(f"[TASK STATUS] Task state: {task_result.state}")

    if task_result.state == "PENDING":
        response = {
            "task_id": task_id,
            "status": "pending",
            "progress": 0,
            "message": "Task is waiting to be processed",
        }
    elif task_result.state == "PROGRESS":
        response = {
            "task_id": task_id,
            "status": "processing",
            "progress": task_result.info.get("progress", 0),
            "total": task_result.info.get("total", 100),
            "current_step": task_result.info.get("status"),
        }
    elif task_result.state == "SUCCESS":
        response = {
            "task_id": task_id,
            "status": "completed",
            "result": task_result.result,
        }
    elif task_result.state == "FAILURE":
        response = {
            "task_id": task_id,
            "status": "failed",
            "error": str(task_result.info),
        }
    else:
        response = {
            "task_id": task_id,
            "status": task_result.state.lower(),
        }

    logger.info(f"[TASK STATUS] Response: {response}")
    return response
