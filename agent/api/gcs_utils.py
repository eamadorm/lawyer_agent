
from google.cloud import storage
from loguru import logger
from datetime import datetime, timedelta
from io import BytesIO


# Create a general storage client
client = storage.Client()


def bucket_exists(bucket_name: str) -> bool:
    """
    Tells if a bucket exists or not.

        Args:
            bucket_name: str -> Name of the bucket

        Return:
            bool -> True if the bucket exists, otherwise False.
    """
    if not isinstance(bucket_name, str) or bucket_name == "":
        raise TypeError("The parameter bucket_name must be a not null string")

    return client.bucket(bucket_name).exists()


def generate_upload_url(
    blob_name: str,
    bucket_name: str,
    content_type: str,
) -> None | str:
    """
    Generate a v4 signed URL for uploading a blob using HTTP PUT.

    Args:
        blob_name: str -> Path + name of the file to be stored. ex: "my_folder/my_file.bin"
        bucket_name: str -> Name of the GCS bucket. ex: "my_bucket"
        content_type: str -> MIME type of the file.

    Return:
        str -> Generated url to upload a file in GCS
    """
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=15), # The url is valid for 15 min only
        method="PUT",
        content_type=content_type
    )
    logger.debug(f"Generated upload URL: {url}")
    return url
