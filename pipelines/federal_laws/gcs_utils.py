from google.cloud import storage
from loguru import logger
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


def upload_bytes(
    blob_name: str,
    bucket_name: str,
    content_type: str,
    bytes_data: bytes,
    make_public: bool = False,
) -> None | str:
    """
    Upload bytes data to a GCS bucket.

    Args:
        blob_name: str -> Path + name of the file to be stored. ex: "my_folder/my_file.bin"
        bucket_name: str -> Name of the GCS bucket. ex: "my_bucket"
        bytes_data: bytes -> Raw binary data to be stored in GCS.
        make_public: bool -> Make a blob public. Default to False

    Return:
        None | str -> Public URL if make_public = True, otherwise None
    """
    if not bucket_exists(bucket_name):
        raise ValueError(f"The bucket {bucket_name} does not exists")
    if not isinstance(bytes_data, bytes):
        raise TypeError("The bytes_data parameter must be of type 'bytes'")
    if not all(
        isinstance(param, str) and param.strip() != ""
        for param in [blob_name, content_type]
    ):
        raise ValueError(
            "blob_name and content_type parameters must be non-empty strings"
        )

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_file(BytesIO(bytes_data), content_type=content_type)

    if make_public:
        blob.make_public()
        return blob.public_url

    logger.info("Bytes data successfully stored in GCS bucket")