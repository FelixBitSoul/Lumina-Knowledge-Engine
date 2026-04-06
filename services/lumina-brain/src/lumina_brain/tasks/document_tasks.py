import logging
from lumina_brain.celery_app import celery_app
from lumina_brain.core.services.document import document_service
from lumina_brain.core.services.embedding import embedding_service
from lumina_brain.core.services.qdrant import qdrant_service
from lumina_brain.core.services.notification_service import notification_service
from lumina_brain.config.settings import settings
import hashlib

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="lumina_brain.tasks.process_document")
def process_document(self, file_id: str, collection: str = "knowledge_base", source_type: str = "document", filename: str = None, category: str = "general"):
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
        collection: Qdrant collection name
        source_type: Source type ("document" or "web")
        filename: Original filename (required for document type)
        category: Document category
    """
    logger.info(f"[TASK] Starting document processing task for file_id: {file_id}, source_type: {source_type}, collection: {collection}")

    try:
        logger.info(f"[TASK] Step 1/7: Downloading file from MinIO...")
        self.update_state(state="PROGRESS", meta={"status": "downloading", "file_id": file_id})

        # Download file from MinIO
        file_content = download_file_from_minio(file_id, collection, source_type, filename)
        logger.info(f"[TASK] File downloaded successfully, size: {len(file_content)} bytes")

        logger.info(f"[TASK] Step 2/7: Extracting text...")
        self.update_state(state="PROGRESS", meta={"status": "extracting", "file_id": file_id})

        # Extract text based on source type
        snapshot = None
        title = ""
        if source_type == "web":
            # Parse JSON for web snapshots
            import json
            snapshot = json.loads(file_content.decode('utf-8'))
            text = snapshot.get("content", "")
            title = snapshot.get("title", "")
            content_hash = document_service.generate_content_hash(text)
            logger.info(f"[TASK] Web snapshot content extracted successfully, length: {len(text)} characters")
        else:
            # Extract text for regular documents
            if not filename:
                raise ValueError("Filename is required for document type")
            file_extension = filename.split(".")[-1]
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
                notification_service.publish_document_progress(file_id, {
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
            payload = {
                "file_id": file_id,  # Keyword field for fast filtering
                "content_hash": content_hash,
                "category": category,
                "content": chunk,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "document_id": file_id,
                "source_type": source_type,
            }

            # Add source-specific payload
            if source_type == "web":
                payload["url"] = snapshot.get("url", "")
                payload["title"] = title
                payload["minio_path"] = f"raw/collections/{collection}/web/{file_id}.json"
            else:
                payload["file_name"] = filename
                import os
                _, extension = os.path.splitext(filename)
                if extension:
                    extension = extension[1:]  # Remove leading dot
                else:
                    extension = "bin"
                payload["minio_path"] = f"raw/collections/{collection}/docs/{file_id}.{extension}"

            points.append({
                "id": chunk_id,
                "vector": vector,
                "payload": payload,
            })

        logger.info(f"[TASK] Step 5/7: Storing {len(points)} points in Qdrant...")
        self.update_state(state="PROGRESS", meta={"status": "storing", "file_id": file_id})

        # Store in Qdrant
        qdrant_service.upsert_points(points, collection)
        logger.info(f"[TASK] Points stored in Qdrant successfully")

        logger.info(f"[TASK] Step 6/7: Sending completion notification...")
        # Send Redis Pub/Sub notification
        notification_service.publish_document_completion(file_id, {
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
        notification_service.publish_document_failure(file_id, str(e))
        self.update_state(state="FAILURE", meta={
            "status": "failed",
            "file_id": file_id,
            "error": str(e),
        })
        raise


def download_file_from_minio(file_id: str, collection: str, source_type: str, filename: str = None) -> bytes:
    """Download file from MinIO

    Args:
        file_id: Document ID
        collection: Collection name
        source_type: Source type ("document" or "web")
        filename: Original filename (required for document type)

    Returns:
        bytes: File content
    """
    from minio import Minio

    client = Minio(
        endpoint=settings.minio.endpoint,
        access_key=settings.minio.access_key,
        secret_key=settings.minio.secret_key,
        secure=settings.minio.secure,
    )

    try:
        if source_type == "web":
            # Web snapshot path: raw/collections/{collection}/web/{file_id}.json
            object_name = f"raw/collections/{collection}/web/{file_id}.json"
            logger.info(f"[MINIO] Downloading web snapshot from MinIO: {object_name}")
        else:
            # Document path: raw/collections/{collection}/docs/{file_id}.{extension}
            if not filename:
                raise ValueError("Filename is required for document type")
            import os
            _, extension = os.path.splitext(filename)
            if extension:
                extension = extension[1:]  # Remove leading dot
            else:
                extension = "bin"
            object_name = f"raw/collections/{collection}/docs/{file_id}.{extension}"
            logger.info(f"[MINIO] Downloading document from MinIO: {object_name}")

        response = client.get_object(
            bucket_name=settings.minio.bucket,
            object_name=object_name,
        )
        content = response.read()
        logger.info(f"[MINIO] File downloaded successfully, size: {len(content)} bytes")
        return content
    except Exception as e:
        logger.error(f"[MINIO] Failed to download file from MinIO: {str(e)}", exc_info=True)
        raise



