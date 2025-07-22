from google.cloud import storage
from dotenv import load_dotenv
import mimetypes
import uuid
import os

load_dotenv()
GOOGLE_CLOUD_PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT_ID"]

def upload_image_to_gcs(file, bucket_name: str, folder: str = "uploads") -> str:
    """
    Uploads an image to Google Cloud Storage and returns the public URL.

    Args:
        file (UploadFile): FastAPI UploadFile object.
        bucket_name (str): GCS bucket name.
        folder (str): Optional folder in the bucket.

    Returns:
        str: Public URL of the uploaded image.
    """
    # Initialize the GCS client
    client = storage.Client(project=GOOGLE_CLOUD_PROJECT_ID)
    bucket = client.bucket(bucket_name)

    # Get file extension from original filename
    filename_ext = file.filename.split('.')[-1]
    filename = f"{folder}/{uuid.uuid4().hex}.{filename_ext}"

    # Upload blob from file object
    blob = bucket.blob(filename)
    content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

    blob.upload_from_file(file.file, content_type=content_type)

    # Make it public
    # blob.make_public()

    return blob.public_url
