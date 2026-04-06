from fastapi import APIRouter, Query
from lumina_brain.schemas.document import DocumentCreate
from lumina_brain.core.services.minio import minio_service
from lumina_brain.tasks.document_tasks import process_document

router = APIRouter()


@router.post("")
async def ingest_document(
    doc: DocumentCreate,
    collection: str = Query("knowledge_base", description="Collection name (default: knowledge_base)")
):
    """
    Process document: Upload to MinIO and trigger processing task
    """
    try:
        # Upload web snapshot to MinIO
        minio_path, file_id = minio_service.upload_web_snapshot(
            url=doc.url,
            title=doc.title,
            content=doc.content,
            collection_name=collection
        )

        # Trigger Celery task for processing
        task = process_document.delay(
            file_id=file_id,
            collection=collection,
            source_type="web"
        )

        print(f"Successfully started processing: {doc.title}")
        return {"status": "success", "task_id": task.id, "minio_path": minio_path}
    except Exception as e:
        print(f"Error during ingestion: {e}")
        return {"status": "error", "message": str(e)}
