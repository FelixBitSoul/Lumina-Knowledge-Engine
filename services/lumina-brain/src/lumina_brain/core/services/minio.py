import logging
from minio import Minio
from minio.error import S3Error
from datetime import timedelta, datetime, timezone
import io
import json
import hashlib
from urllib.parse import urlparse
from lumina_brain.config.settings import settings

logger = logging.getLogger(__name__)


class MinIOService:
    def __init__(self):
        """Initialize MinIO client"""
        logger.info(f"[MINIO] Initializing MinIO client with endpoint: {settings.minio.endpoint}")
        self.client = Minio(
            endpoint=settings.minio.endpoint,
            access_key=settings.minio.access_key,
            secret_key=settings.minio.secret_key,
            secure=settings.minio.secure,
        )
        self.bucket = settings.minio.bucket
        logger.info(f"[MINIO] MinIO client initialized, bucket: {self.bucket}")
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Create bucket if not exists"""
        try:
            logger.info(f"[MINIO] Checking if bucket exists: {self.bucket}")
            if not self.client.bucket_exists(self.bucket):
                logger.info(f"[MINIO] Bucket does not exist, creating: {self.bucket}")
                self.client.make_bucket(self.bucket)
                logger.info(f"[MINIO] Bucket created successfully: {self.bucket}")
            else:
                logger.info(f"[MINIO] Bucket already exists: {self.bucket}")
        except Exception as e:
            logger.error(f"[MINIO] Failed to ensure bucket: {str(e)}", exc_info=True)
            raise

    def upload_bytes(self, data: bytes, file_id: str, filename: str, collection_name: str) -> str:
        """Upload bytes data to MinIO

        Args:
            data: File content as bytes
            file_id: Document ID (based on content hash)
            filename: Original filename
            collection_name: Collection name

        Returns:
            str: Object name in MinIO
        """
        # Extract file extension
        import os
        _, extension = os.path.splitext(filename)
        if extension:
            extension = extension[1:]  # Remove leading dot
        else:
            extension = "bin"

        # Construct object name following the new path规范
        object_name = f"raw/collections/{collection_name}/docs/{file_id}.{extension}"
        logger.info(f"[MINIO] Uploading file to MinIO: {object_name}, size: {len(data)} bytes")

        # Prepare metadata
        metadata = {
            "original-name": filename,
            "file-size": str(len(data)),
            "uploaded-at": datetime.now(timezone.utc).isoformat()
        }

        try:
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=io.BytesIO(data),
                length=len(data),
                metadata=metadata
            )
            logger.info(f"[MINIO] File uploaded successfully: {object_name}")
            return object_name
        except Exception as e:
            logger.error(f"[MINIO] Failed to upload file: {str(e)}", exc_info=True)
            raise

    def generate_presigned_url(self, file_id: str, filename: str, collection_name: str, expiry: int = None) -> str:
        """Generate presigned URL for file download

        Args:
            file_id: Document ID (based on content hash)
            filename: Original filename
            collection_name: Collection name
            expiry: Expiry time in seconds (default: settings.minio.presigned_expiry)

        Returns:
            str: Presigned URL
        """
        # Extract file extension
        import os
        _, extension = os.path.splitext(filename)
        if extension:
            extension = extension[1:]  # Remove leading dot
        else:
            extension = "bin"

        object_name = f"raw/collections/{collection_name}/docs/{file_id}.{extension}"
        expiry_seconds = expiry or settings.minio.presigned_expiry
        logger.info(f"[MINIO] Generating presigned URL for: {object_name}, expiry: {expiry_seconds}s")
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=timedelta(seconds=expiry_seconds),
            )
            logger.info(f"[MINIO] Presigned URL generated successfully")
            return url
        except Exception as e:
            logger.error(f"[MINIO] Failed to generate presigned URL: {str(e)}", exc_info=True)
            raise

    def delete_file(self, file_id: str, filename: str, collection_name: str):
        """Delete file from MinIO

        Args:
            file_id: Document ID (based on content hash)
            filename: Original filename
            collection_name: Collection name
        """
        # Extract file extension
        import os
        _, extension = os.path.splitext(filename)
        if extension:
            extension = extension[1:]  # Remove leading dot
        else:
            extension = "bin"

        object_name = f"raw/collections/{collection_name}/docs/{file_id}.{extension}"
        logger.info(f"[MINIO] Deleting file from MinIO: {object_name}")
        try:
            self.client.remove_object(self.bucket, object_name)
            logger.info(f"[MINIO] File deleted successfully: {object_name}")
        except Exception as e:
            logger.error(f"[MINIO] Failed to delete file: {str(e)}", exc_info=True)
            raise

    def file_exists(self, file_id: str, filename: str, collection_name: str) -> bool:
        """Check if file exists in MinIO

        Args:
            file_id: Document ID (based on content hash)
            filename: Original filename
            collection_name: Collection name

        Returns:
            bool: True if file exists, False otherwise
        """
        # Extract file extension
        import os
        _, extension = os.path.splitext(filename)
        if extension:
            extension = extension[1:]  # Remove leading dot
        else:
            extension = "bin"

        object_name = f"raw/collections/{collection_name}/docs/{file_id}.{extension}"
        logger.debug(f"[MINIO] Checking if file exists: {object_name}")
        try:
            self.client.stat_object(self.bucket, object_name)
            logger.debug(f"[MINIO] File exists: {object_name}")
            return True
        except S3Error as e:
            logger.debug(f"[MINIO] File does not exist: {object_name}, error: {str(e)}")
            return False

    def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed_url = urlparse(url)
        return parsed_url.netloc

    def upload_web_snapshot(self, url: str, title: str, content: str, collection_name: str) -> tuple[str, str]:
        """Upload web snapshot to MinIO

        Args:
            url: Web page URL
            title: Web page title
            content: Web page content
            collection_name: Collection name

        Returns:
            tuple[str, str]: (minio_path, sha256_id)
        """
        # Generate sha256 hash from URL
        sha256_id = hashlib.sha256(url.encode()).hexdigest()

        # Create snapshot object
        snapshot = {
            "url": url,
            "title": title,
            "content": content,
            "metadata": {
                "domain": self.extract_domain(url),
                "crawled_at": datetime.now(timezone.utc).isoformat(),
                "type": "webpage"
            }
        }

        # Convert snapshot to JSON bytes
        snapshot_json = json.dumps(snapshot, ensure_ascii=False).encode('utf-8')

        # Construct object name following the path规范
        object_name = f"raw/collections/{collection_name}/web/{sha256_id}.json"
        logger.info(f"[MINIO] Uploading web snapshot to MinIO: {object_name}, size: {len(snapshot_json)} bytes")

        # Prepare metadata
        metadata = {
            "source-type": "web",
            "created-at": datetime.now(timezone.utc).isoformat()
        }

        try:
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=io.BytesIO(snapshot_json),
                length=len(snapshot_json),
                metadata=metadata
            )
            logger.info(f"[MINIO] Web snapshot uploaded successfully: {object_name}")
            return object_name, sha256_id
        except Exception as e:
            logger.error(f"[MINIO] Failed to upload web snapshot: {str(e)}", exc_info=True)
            raise


# Create global MinIO service instance
logger.info("[MINIO] Creating global MinIO service instance...")
minio_service = MinIOService()
logger.info("[MINIO] Global MinIO service instance created")
