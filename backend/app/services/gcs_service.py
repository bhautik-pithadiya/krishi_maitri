from google.cloud import storage
from dotenv import load_dotenv
import mimetypes
import uuid
import os

load_dotenv()
GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")

def upload_image_to_gcs(file, bucket_name: str, folder: str = "uploads") -> str:
    """
    Uploads an image to Google Cloud Storage and returns the public URL.
    """
    client = storage.Client(project=GOOGLE_CLOUD_PROJECT_ID)
    bucket = client.bucket(bucket_name)

    filename_ext = file.filename.split('.')[-1]
    filename = f"{folder}/{uuid.uuid4().hex}.{filename_ext}"

    blob = bucket.blob(filename)
    content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

    blob.upload_from_file(file.file, content_type=content_type)

    return blob.public_url