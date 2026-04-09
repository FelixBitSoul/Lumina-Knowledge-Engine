from minio import Minio

# Initialize MinIO client
client = Minio(
    'minio:9000',
    access_key='minioadmin',
    secret_key='minioadmin',
    secure=False
)

# List objects in the bucket
bucket_name = 'lumina-documents'
prefix = 'raw/collections/knowledge_base/'

print(f'Files in MinIO bucket "{bucket_name}" with prefix "{prefix}":')
try:
    objects = client.list_objects(bucket_name, prefix=prefix, recursive=True)
    found = False
    for obj in objects:
        print(f'  - {obj.object_name}')
        found = True
    if not found:
        print('  No files found')
except Exception as e:
    print(f'Error: {e}')
