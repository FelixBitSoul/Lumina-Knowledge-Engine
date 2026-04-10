import logging
from datetime import datetime
from lumina_brain.celery_app import celery_app
from lumina_brain.core.services.document import document_service
from lumina_brain.core.services.embedding import embedding_service
from lumina_brain.core.services.qdrant import qdrant_service
from lumina_brain.core.services.notification_service import notification_service
from lumina_brain.core.services.cache import cache_service
from lumina_brain.core.services.database import SessionLocal
from lumina_brain.core.models import DocumentProcessing, DocumentStatus, SourceType
from lumina_brain.core.utils.path_utils import get_minio_object_path
from lumina_brain.config.settings import settings
import hashlib

logger = logging.getLogger(__name__)


def _update_processing_status(processing, status, step=None, progress=None, total=None):
    """Update processing status in database"""
    if processing:
        if status:
            processing.status = status
        if step:
            processing.current_step = step
        if progress is not None:
            processing.progress = progress
        if total is not None:
            processing.total = total
        processing.db.commit()


def _extract_text_from_content(file_content, source_type, filename):
    """Extract text from file content based on source type"""
    # Guard clause: Check for filename if not web source
    if source_type != SourceType.WEB.value and not filename:
        raise ValueError("Filename is required for document type")
    
    snapshot = None
    title = ""
    if source_type == SourceType.WEB.value:
        # Parse JSON for web snapshots
        import json
        snapshot = json.loads(file_content.decode('utf-8'))
        text = snapshot.get("content", "")
        title = snapshot.get("title", "")
        content_hash = document_service.generate_content_hash(text)
        logger.info(f"[TASK] Web snapshot content extracted successfully, length: {len(text)} characters")
    else:
        # Extract text for regular documents
        file_extension = filename.split(".")[-1]
        text = document_service.extract_text(file_content, file_extension)
        content_hash = document_service.generate_content_hash(text)
        logger.info(f"[TASK] Text extracted successfully, length: {len(text)} characters")
    return text, content_hash, snapshot, title

def _generate_embedding_points(chunks, file_id, collection, source_type, filename, category, content_hash, processing, snapshot, title, task):
    """Generate embedding points for chunks"""
    points = []
    for i, chunk in enumerate(chunks):
        if i % 10 == 0:
            logger.info(f"[TASK] Processing chunk {i}/{len(chunks)}...")
            task.update_state(state="PROGRESS", meta={
                "status": "embedding",
                "file_id": file_id,
                "progress": i,
                "total": len(chunks)
            })
            # Update database progress
            _update_processing_status(processing, None, None, i, len(chunks))
            # Send progress notification
            notification_service.publish_document_progress(file_id, {
                "progress": i,
                "total": len(chunks),
                "step": f"Generating embeddings ({i}/{len(chunks)})"
            }, collection)

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
        if source_type == SourceType.WEB.value:
            payload["url"] = snapshot.get("url", "")
            payload["title"] = title
        else:
            payload["file_name"] = filename
        
        # Generate MinIO path using utility function
        payload["minio_path"] = get_minio_object_path(file_id, collection, source_type, filename)

        points.append({
            "id": chunk_id,
            "vector": vector,
            "payload": payload,
        })
    return points

def _update_collection_statistics(collection):
    """Update collection statistics cache"""
    try:
        from lumina_brain.core.services.qdrant import qdrant_service
        from lumina_brain.core.services.minio import minio_service

        # Generate cache key
        cache_key = f"lumina:stats:{collection}"

        # Initialize statistics
        stats = {
            "collection": collection,
            "files_count": 0,
            "total_vectors": 0,
            "total_chunks": 0,  # Each vector represents a chunk
            "vector_size": 384,  # Fixed for all-MiniLM-L6-v2 model
            "distance_function": "cosine"
        }

        # Count files in MinIO
        try:
            # Build MinIO path prefix
            prefix = f"raw/collections/{collection}/"

            # List all objects with the specified prefix
            objects = minio_service.client.list_objects(
                bucket_name=minio_service.bucket,
                prefix=prefix,
                recursive=True
            )

            # Count files
            file_count = 0
            for _ in objects:
                file_count += 1

            stats["files_count"] = file_count
        except Exception as e:
            print(f"Error counting files in MinIO: {e}")
            # Continue execution, not affecting other statistics

        # Get vector count from Qdrant
        try:
            # Get collection information
            collection_info = qdrant_service.client.get_collection(collection_name=collection)

            # Get total vectors (points) in the collection
            total_vectors = collection_info.points_count

            stats["total_vectors"] = total_vectors
            stats["total_chunks"] = total_vectors  # Each vector represents a chunk
        except Exception as e:
            print(f"Error getting collection info from Qdrant: {e}")
            # Continue execution, return default values

        # Cache statistics with 60-second expiration
        cache_service.set(cache_key, stats, ttl=60)
        logger.info(f"[TASK] Collection stats cache updated")
    except Exception as e:
        logger.error(f"[TASK] Failed to update collection stats cache: {e}")

def _complete_processing(processing, chunks, file_id, filename, task):
    """Complete processing and update status"""
    # Update status to completed
    logger.info(f"[TASK] Step 7/7: Updating task status to SUCCESS...")
    if processing:
        processing.status = DocumentStatus.COMPLETED
        processing.progress = len(chunks)
        processing.chunks_created = len(chunks)
        processing.completed_at = datetime.utcnow()
        processing.db.commit()
        logger.info(f"[TASK] Status updated to completed in PostgreSQL")

    task.update_state(state="SUCCESS", meta={
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

def _update_task_status(task, processing, step_name, status_message, progress=None, total=None):
    """Update task status in Celery and database"""
    logger.info(f"[TASK] Step {step_name}: {status_message}")
    
    # Update Celery task state
    meta = {"status": status_message.lower().replace(" ", "_"), "file_id": task.request.id}
    if progress is not None:
        meta["progress"] = progress
    if total is not None:
        meta["total"] = total
    task.update_state(state="PROGRESS", meta=meta)
    
    # Update database status
    _update_processing_status(processing, None, status_message.lower().replace(" ", "_"), progress, total)


def _handle_processing_error(processing, file_id, error, task, collection=None):
    """Handle processing error and update status"""
    logger.error(f"[TASK] Document processing failed for file_id: {file_id}, error: {str(error)}", exc_info=True)
    # Update status to failed in database
    if processing:
        processing.status = DocumentStatus.FAILED
        processing.error_message = str(error)
        processing.db.commit()
        logger.info(f"[TASK] Status updated to failed in PostgreSQL")
    # Send failure notification
    notification_service.publish_document_failure(file_id, str(error), collection)
    task.update_state(state="FAILURE", meta={
        "status": "failed",
        "file_id": file_id,
        "error": str(error),
    })
    raise


def _initialize_processing(db, file_id):
    """Initialize processing record and update status"""
    # Get processing record
    processing = db.query(DocumentProcessing).filter(DocumentProcessing.document_id == file_id).first()
    processing.db = db  # Attach db to processing object

    # Update status to processing
    logger.info(f"[TASK] Updating status to processing in PostgreSQL...")
    _update_processing_status(processing, DocumentStatus.PROCESSING, "downloading")
    return processing


def _process_document_content(self, processing, file_id, collection, source_type, filename, category):
    """Process document content and generate embeddings"""
    # Step 1: Download file from MinIO
    _update_task_status(self, processing, "1/7", "Downloading file from MinIO")
    file_content = _download_file_from_minio(file_id, collection, source_type, filename)
    logger.info(f"[TASK] File downloaded successfully, size: {len(file_content)} bytes")

    # Step 2: Extract text
    _update_task_status(self, processing, "2/7", "Extracting text")
    text, content_hash, snapshot, title = _extract_text_from_content(file_content, source_type, filename)

    # Step 3: Split text into chunks
    _update_task_status(self, processing, "3/7", "Splitting text into chunks")
    chunks = document_service.split_text(text)
    logger.info(f"[TASK] Text split into {len(chunks)} chunks")

    # Step 4: Generate embeddings
    _update_task_status(self, processing, "4/7", "Generating embeddings", 0, len(chunks))

    # Generate embeddings and store in Qdrant
    points = _generate_embedding_points(chunks, file_id, collection, source_type, filename, category, content_hash, processing, snapshot, title, self)

    # Step 5: Store points in Qdrant
    _update_task_status(self, processing, "5/7", f"Storing {len(points)} points in Qdrant")
    qdrant_service.upsert_points(points, collection)
    logger.info(f"[TASK] Points stored in Qdrant successfully")

    return chunks, content_hash


def _finalize_processing(self, processing, file_id, filename, collection, chunks):
    """Finalize processing and update collection stats"""
    # Step 6: Send completion notification
    _update_task_status(self, processing, "6/7", "Sending completion notification")
    notification_service.publish_document_completion(file_id, {
        "filename": filename,
        "chunks_created": len(chunks),
        "collection": collection
    })
    logger.info(f"[TASK] Completion notification sent")

    # Step 6.5: Clear collection cache
    logger.info(f"[TASK] Step 6.5/7: Clearing collection cache for {collection}...")
    cache_service.clear_collection_cache(collection)
    logger.info(f"[TASK] Collection cache cleared")

    # Step 6.6: Update collection stats cache
    logger.info(f"[TASK] Step 6.6/7: Updating collection stats cache for {collection}...")
    _update_collection_statistics(collection)

    # Complete processing
    return _complete_processing(processing, chunks, file_id, filename, self)


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

    # Get database session
    db = SessionLocal()
    processing = None
    
    try:
        # Initialize processing
        processing = _initialize_processing(db, file_id)

        # Process document content
        chunks, content_hash = _process_document_content(self, processing, file_id, collection, source_type, filename, category)

        # Finalize processing
        return _finalize_processing(self, processing, file_id, filename, collection, chunks)

    except Exception as e:
        _handle_processing_error(processing, file_id, e, self, collection)
    finally:
        db.close()


def _download_file_from_minio(file_id: str, collection: str, source_type: str, filename: str = None) -> bytes:
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
        # Generate MinIO object path using utility function
        object_name = get_minio_object_path(file_id, collection, source_type, filename)
        logger.info(f"[MINIO] Downloading from MinIO: {object_name}")

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



