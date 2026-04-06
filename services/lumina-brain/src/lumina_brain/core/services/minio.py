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

    def list_files(self, collection_name: str, limit: int = 20, start_after: str = None) -> tuple[list[dict], str]:
        """List files in a collection with pagination

        Args:
            collection_name: Collection name
            limit: Maximum number of files to return
            start_after: Object name to start after (for pagination)

        Returns:
            tuple[list[dict], str]: List of files with metadata and the next marker
        """
        files = []
        next_marker = None
        try:
            # List document files
            docs_prefix = f"raw/collections/{collection_name}/docs/"
            logger.info(f"[MINIO] Listing files in collection: {collection_name}, prefix: {docs_prefix}, limit: {limit}, start_after: {start_after}")

            # List objects in MinIO
            objects = self.client.list_objects(
                bucket_name=self.bucket,
                prefix=docs_prefix,
                recursive=True
            )

            # Collect objects up to the limit, skipping until start_after
            collected_objects = []
            skip_until_start_after = start_after is not None

            for obj in objects:
                # Skip objects until we reach start_after
                if skip_until_start_after:
                    if obj.object_name == start_after:
                        skip_until_start_after = False
                    continue

                # Collect objects up to the limit
                if len(collected_objects) < limit:
                    collected_objects.append(obj)
                else:
                    break

            # Check if there are more objects
            if len(collected_objects) == limit:
                # Set next marker to the last object's name
                next_marker = collected_objects[-1].object_name

            # Process collected objects
            for obj in collected_objects:
                # Extract file_id and filename from object name
                import os
                obj_name = obj.object_name
                # Get file_id from the path: raw/collections/{collection}/docs/{file_id}.{ext}
                file_id = os.path.basename(obj_name).split('.')[0]

                # Get metadata
                try:
                    stat = self.client.stat_object(self.bucket, obj_name)
                    original_name = stat.metadata.get('x-amz-meta-original-name', os.path.basename(obj_name))
                    file_size = int(stat.metadata.get('x-amz-meta-file-size', obj.size))
                    uploaded_at = stat.metadata.get('x-amz-meta-uploaded-at', obj.last_modified.isoformat())

                    files.append({
                        "file_id": file_id,
                        "filename": original_name,
                        "size": file_size,
                        "uploaded_at": uploaded_at,
                        "type": "document",
                        "object_name": obj_name
                    })
                except Exception as e:
                    logger.error(f"[MINIO] Failed to get metadata for {obj_name}: {str(e)}")
                    # Continue with basic info
                    files.append({
                        "file_id": file_id,
                        "filename": os.path.basename(obj_name),
                        "size": obj.size,
                        "uploaded_at": obj.last_modified.isoformat(),
                        "type": "document",
                        "object_name": obj_name
                    })

            # If we haven't reached the limit, list web snapshot files
            remaining_limit = limit - len(files)
            if remaining_limit > 0:
                web_prefix = f"raw/collections/{collection_name}/web/"
                logger.info(f"[MINIO] Listing web snapshots in collection: {collection_name}, prefix: {web_prefix}, limit: {remaining_limit}")

                # List web objects
                web_objects = self.client.list_objects(
                    bucket_name=self.bucket,
                    prefix=web_prefix,
                    recursive=True
                )

                # Collect web objects up to the remaining limit
                web_collected_objects = []
                for obj in web_objects:
                    if len(web_collected_objects) < remaining_limit:
                        web_collected_objects.append(obj)
                    else:
                        break

                # Check if there are more web objects
                if len(web_collected_objects) == remaining_limit:
                    # Set next marker to the last web object's name
                    next_marker = web_collected_objects[-1].object_name

                # Process web objects
                for obj in web_collected_objects:
                    # Extract file_id from object name
                    import os
                    obj_name = obj.object_name
                    file_id = os.path.basename(obj_name).split('.')[0]

                    # Get metadata
                    try:
                        stat = self.client.stat_object(self.bucket, obj_name)

                        # Read the JSON content to get title and URL
                        try:
                            response = self.client.get_object(self.bucket, obj_name)
                            snapshot_data = json.loads(response.read().decode('utf-8'))
                            response.close()
                            response.release_conn()

                            files.append({
                                "file_id": file_id,
                                "filename": snapshot_data.get('title', f"Web: {snapshot_data.get('url', 'Unknown')}"),
                                "size": obj.size,
                                "uploaded_at": snapshot_data.get('metadata', {}).get('crawled_at', obj.last_modified.isoformat()),
                                "type": "web",
                                "url": snapshot_data.get('url'),
                                "object_name": obj_name
                            })
                        except Exception as e:
                            logger.error(f"[MINIO] Failed to read web snapshot content: {str(e)}")
                            # Continue with basic info
                            files.append({
                                "file_id": file_id,
                                "filename": os.path.basename(obj_name),
                                "size": obj.size,
                                "uploaded_at": obj.last_modified.isoformat(),
                                "type": "web",
                                "object_name": obj_name
                            })
                    except Exception as e:
                        logger.error(f"[MINIO] Failed to get metadata for {obj_name}: {str(e)}")
                        # Continue with basic info
                        files.append({
                            "file_id": file_id,
                            "filename": os.path.basename(obj_name),
                            "size": obj.size,
                            "uploaded_at": obj.last_modified.isoformat(),
                            "type": "web",
                            "object_name": obj_name
                        })

            logger.info(f"[MINIO] Listed {len(files)} files in collection: {collection_name}, next_marker: {next_marker}")
            return files, next_marker
        except Exception as e:
            logger.error(f"[MINIO] Failed to list files: {str(e)}", exc_info=True)
            return [], None


# Create global MinIO service instance
logger.info("[MINIO] Creating global MinIO service instance...")
minio_service = MinIOService()
logger.info("[MINIO] Global MinIO service instance created")
