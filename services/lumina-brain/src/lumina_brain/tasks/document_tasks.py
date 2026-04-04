import logging
from lumina_brain.celery_app import celery_app
from lumina_brain.core.services.minio import minio_service
from lumina_brain.core.services.document import document_service
from lumina_brain.core.services.embedding import embedding_service
from lumina_brain.core.services.qdrant import qdrant_service
from lumina_brain.config.settings import settings
import hashlib
import json
import redis
from datetime import datetime

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="lumina_brain.tasks.process_document")
def process_document(self, file_id: str, filename: str, category: str, collection: str = "knowledge_base"):
    """
    Asynchronous document processing task

    Process:
    1. Download original file from MinIO
    2. Extract text content
    3. Split text into chunks
    4. Generate vector embeddings
    5. Store in Qdrant
    6. Update task status
    7. Send Redis Pub/Sub notification

    Args:
        file_id: Document ID (based on content hash)
        filename: Original filename
        category: Document category
        collection: Qdrant collection name
    """
    logger.info(f"[TASK] Starting document processing task for file_id: {file_id}, filename: {filename}, collection: {collection}")
    
    try:
        logger.info(f"[TASK] Step 1/7: Downloading file from MinIO...")
        self.update_state(state="PROGRESS", meta={"status": "downloading", "file_id": file_id})

        # Download file from MinIO
        file_content = download_file_from_minio(file_id, filename)
        file_extension = filename.split(".")[-1]
        logger.info(f"[TASK] File downloaded successfully, size: {len(file_content)} bytes, extension: {file_extension}")

        logger.info(f"[TASK] Step 2/7: Extracting text...")
        self.update_state(state="PROGRESS", meta={"status": "extracting", "file_id": file_id})

        # Extract text
        text = document_service.extract_text(file_content, file_extension)
        content_hash = document_service.generate_content_hash(text)
        logger.info(f"[TASK] Text extracted successfully, length: {len(text)} characters")

        logger.info(f"[TASK] Step 3/7: Splitting text into chunks...")
        self.update_state(state="PROGRESS", meta={"status": "chunking", "file_id": file_id})

        # Split text into chunks
        chunks = document_service.split_text(text)
        logger.info(f"[TASK] Text split into {len(chunks)} chunks")

        logger.info(f"[TASK] Step 4/7: Generating embeddings...")
        self.update_state(state="PROGRESS", meta={
            "status": "embedding",
            "file_id": file_id,
            "progress": 0,
            "total": len(chunks)
        })

        # Generate embeddings and store in Qdrant
        points = []
        for i, chunk in enumerate(chunks):
            if i % 10 == 0:
                logger.info(f"[TASK] Processing chunk {i}/{len(chunks)}...")
                self.update_state(state="PROGRESS", meta={
                    "status": "embedding",
                    "file_id": file_id,
                    "progress": i,
                    "total": len(chunks)
                })
                # Send progress notification
                send_document_progress_notification(file_id, {
                    "progress": i,
                    "total": len(chunks),
                    "step": f"Generating embeddings ({i}/{len(chunks)})"
                })

            # Generate embedding
            vector = embedding_service.encode(chunk)

            # Generate chunk ID
            chunk_content = f"{file_id}_{i}_{chunk[:100]}"
            chunk_id = int(hashlib.sha256(chunk_content.encode()).hexdigest(), 16) % 10**18

            # Create point
            points.append({
                "id": chunk_id,
                "vector": vector,
                "payload": {
                    "file_id": file_id,  # Keyword field for fast filtering
                    "file_name": filename,
                    "content_hash": content_hash,
                    "category": category,
                    "content": chunk,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "document_id": file_id,
                    "minio_path": f"{file_id}/raw/{filename}",
                },
            })

        logger.info(f"[TASK] Step 5/7: Storing {len(points)} points in Qdrant...")
        self.update_state(state="PROGRESS", meta={"status": "storing", "file_id": file_id})

        # Store in Qdrant
        qdrant_service.upsert_points(points, collection)
        logger.info(f"[TASK] Points stored in Qdrant successfully")

        logger.info(f"[TASK] Step 6/7: Sending completion notification...")
        # Send Redis Pub/Sub notification
        send_document_completion_notification(file_id, {
            "filename": filename,
            "chunks_created": len(chunks),
            "collection": collection
        })
        logger.info(f"[TASK] Completion notification sent")

        logger.info(f"[TASK] Step 7/7: Updating task status to SUCCESS...")
        self.update_state(state="SUCCESS", meta={
            "status": "completed",
            "file_id": file_id,
            "chunks_created": len(chunks),
        })

        logger.info(f"[TASK] Document processing completed successfully! file_id: {file_id}, chunks: {len(chunks)}")
        return {
            "file_id": file_id,
            "filename": filename,
            "chunks_created": len(chunks),
            "status": "success",
        }

    except Exception as e:
        logger.error(f"[TASK] Document processing failed for file_id: {file_id}, error: {str(e)}", exc_info=True)
        # Send failure notification
        send_document_failure_notification(file_id, str(e))
        self.update_state(state="FAILURE", meta={
            "status": "failed",
            "file_id": file_id,
            "error": str(e),
        })
        raise


def download_file_from_minio(file_id: str, filename: str) -> bytes:
    """Download file from MinIO

    Args:
        file_id: Document ID
        filename: Original filename

    Returns:
        bytes: File content
    """
    logger.info(f"[MINIO] Downloading file from MinIO: {file_id}/raw/{filename}")
    from minio import Minio

    client = Minio(
        endpoint=settings.minio.endpoint,
        access_key=settings.minio.access_key,
        secret_key=settings.minio.secret_key,
        secure=settings.minio.secure,
    )

    try:
        response = client.get_object(
            bucket_name=settings.minio.bucket,
            object_name=f"{file_id}/raw/{filename}",
        )
        content = response.read()
        logger.info(f"[MINIO] File downloaded successfully, size: {len(content)} bytes")
        return content
    except Exception as e:
        logger.error(f"[MINIO] Failed to download file from MinIO: {str(e)}", exc_info=True)
        raise


def send_document_completion_notification(file_id: str, metadata: dict = None):
    """Send document processing completion notification

    Args:
        file_id: Document ID
        metadata: Additional metadata
    """
    logger.info(f"[NOTIFICATION] Sending completion notification for file_id: {file_id}")
    try:
        r = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db
        )

        message = {
            "file_id": file_id,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }

        r.publish("document_updates", json.dumps(message))
        logger.info(f"[NOTIFICATION] Completion notification sent successfully")
    except Exception as e:
        logger.error(f"[NOTIFICATION] Failed to send completion notification: {str(e)}", exc_info=True)


def send_document_failure_notification(file_id: str, error: str):
    """Send document processing failure notification

    Args:
        file_id: Document ID
        error:
 Error message
    """
    logger.info(f"[NOTIFICATION] Sending failure notification for file_id: {file_id}")
    try:
        r = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db
        )

        message = {
            "file_id": file_id,
            "status": "failed",
            "error": error,
            "timestamp": datetime.now().isoformat()
        }

        r.publish("document_updates", json.dumps(message))
        logger.info(f"[NOTIFICATION] Failure notification sent successfully")
    except Exception as e:
        logger.error(f"[NOTIFICATION] Failed to send failure notification: {str(e)}", exc_info=True)


def send_document_progress_notification(file_id: str, progress_data: dict):
    """Send document processing progress notification

    Args:
        file_id: Document ID
        progress_data: Progress information
    """
    logger.debug(f"[NOTIFICATION] Sending progress notification for file_id: {file_id}, data: {progress_data}")
    try:
        r = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db
        )

        message = {
            "file_id": file_id,
            "status": "processing",
            "timestamp": datetime.now().isoformat(),
            **progress_data
        }

        r.publish("document_updates", json.dumps(message))
    except Exception as e:
        logger.error(f"[NOTIFICATION] Failed to send progress notification: {str(e)}", exc_info=True)
