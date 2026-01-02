
from google.cloud import storage
import sys

def set_cors(bucket_name):
    """Set the CORS configuration for the bucket."""
    print(f"Configuring CORS for bucket: {bucket_name}")
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        bucket.cors = [
            {
                "origin": ["*"],
                "responseHeader": [
                    "Content-Type",
                    "x-goog-resumable",
                    "Access-Control-Allow-Origin"
                ],
                "method": ["GET", "PUT", "POST", "OPTIONS"],
                "maxAgeSeconds": 3600
            }
        ]
        bucket.patch()
        print(f"SUCCESS: CORS configured for bucket {bucket_name}")
        print("Settings: Origin=*, Methods=GET,PUT,POST,OPTIONS")
    except Exception as e:
        print(f"ERROR: Failed to configure CORS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Defaulting to lawyer_agent as confirmed in code
    set_cors("lawyer_agent")
