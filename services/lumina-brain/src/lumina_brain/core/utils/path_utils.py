"""Path utility functions for MinIO object paths"""
import os
from lumina_brain.config.settings import settings


def get_minio_object_path(file_id: str, collection: str, source_type: str, filename: str = None) -> str:
    """Generate MinIO object path based on source type

    Args:
        file_id: Document ID
        collection: Collection name
        source_type: Source type ("document" or "web")
        filename: Original filename (required for document type)

    Returns:
        str: MinIO object path
    """
    if source_type == "web":
        # Web snapshot path: raw/collections/{collection}/web/{file_id}.json
        return f"raw/collections/{collection}/web/{file_id}.json"
    else:
        # Document path: raw/collections/{collection}/docs/{file_id}.{extension}
        if not filename:
            raise ValueError("Filename is required for document type")
        _, extension = os.path.splitext(filename)
        if extension:
            extension = extension[1:]  # Remove leading dot
        else:
            extension = "bin"
        return f"raw/collections/{collection}/docs/{file_id}.{extension}"
