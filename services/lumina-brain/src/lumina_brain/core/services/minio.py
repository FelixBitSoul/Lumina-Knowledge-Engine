import logging
from minio import Minio
from minio.error import S3Error
from datetime import timedelta
import io
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

    def upload_bytes(self, data: bytes, file_id: str, filename: str) -> str:
        """Upload bytes data to MinIO

        Args:
            data: File content as bytes
            file_id: Document ID (based on content hash)
            filename: Original filename

        Returns:
            str: Object name in MinIO
        """
        object_name = f"{file_id}/raw/{filename}"
        logger.info(f"[MINIO] Uploading file to MinIO: {object_name}, size: {len(data)} bytes")
        try:
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=io.BytesIO(data),
                length=len(data),
            )
            logger.info(f"[MINIO] File uploaded successfully: {object_name}")
            return object_name
        except Exception as e:
            logger.error(f"[MINIO] Failed to upload file: {str(e)}", exc_info=True)
            raise

    def generate_presigned_url(self, file_id: str, filename: str, expiry: int = None) -> str:
        """Generate presigned URL for file download

        Args:
            file_id: Document ID (based on content hash)
            filename: Original filename
            expiry: Expiry time in seconds (default: settings.minio.presigned_expiry)

        Returns:
            str: Presigned URL
        """
        object_name = f"{file_id}/raw/{filename}"
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

    def delete_file(self, file_id: str, filename: str):
        """Delete file from MinIO

        Args:
            file_id: Document ID (based on content hash)
            filename: Original filename
        """
        object_name = f"{file_id}/raw/{filename}"
        logger.info(f"[MINIO] Deleting file from MinIO: {object_name}")
        try:
            self.client.remove_object(self.bucket, object_name)
            logger.info(f"[MINIO] File deleted successfully: {object_name}")
        except Exception as e:
            logger.error(f"[MINIO] Failed to delete file: {str(e)}", exc_info=True)
            raise

    def file_exists(self, file_id: str, filename: str) -> bool:
        """Check if file exists in MinIO

        Args:
            file_id: Document ID (based on content hash)
            filename: Original filename

        Returns:
            bool: True if file exists, False otherwise
        """
        object_name = f"{file_id}/raw/{filename}"
        logger.debug(f"[MINIO] Checking if file exists: {object_name}")
        try:
            self.client.stat_object(self.bucket, object_name)
            logger.debug(f"[MINIO] File exists: {object_name}")
            return True
        except S3Error as e:
            logger.debug(f"[MINIO] File does not exist: {object_name}, error: {str(e)}")
            return False


# Create global MinIO service instance
logger.info("[MINIO] Creating global MinIO service instance...")
minio_service = MinIOService()
logger.info("[MINIO] Global MinIO service instance created")
