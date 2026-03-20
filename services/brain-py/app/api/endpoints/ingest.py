from fastapi import APIRouter, Query
from ...schemas.document import DocumentCreate
from ...core.services.embedding import embedding_service
from ...core.services.qdrant import qdrant_service
from config.settings import settings

router = APIRouter()


@router.post("")
async def ingest_document(
    doc: DocumentCreate,
    collection: str = Query(None, description="Collection name (default: config collection)")
):
    """
    Process document: Generate embedding and store in Qdrant
    """
    try:
        # Generate vector embedding from content
        vector = embedding_service.encode(doc.content)

        # Upsert into Qdrant
        point_id = qdrant_service.upsert_document(
            url=doc.url,
            title=doc.title,
            content=doc.content,
            vector=vector,
            collection_name=collection
        )

        print(f"Successfully indexed: {doc.title}")
        return {"status": "success", "point_id": point_id}
    except Exception as e:
        print(f"Error during ingestion: {e}")
        return {"status": "error", "message": str(e)}
