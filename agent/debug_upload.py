
import requests
import uuid

API_URL = "http://localhost:8080"
TEST_FILE_CONTENT = b"Test PDF Content"
TEST_FILENAME = "test.pdf"
TEST_CONTENT_TYPE = "application/pdf"
USER_ID = "debug_user"
CONVERSATION_ID = str(uuid.uuid4())

def debug_upload():
    print(f"--- Starting Upload Debugging ---")
    print(f"Target API: {API_URL}")
    
    # 1. Get Signed URL
    print(f"\n1. Requesting Signed URL for {TEST_FILENAME}...")
    try:
        payload = {
            "filename": TEST_FILENAME,
            "content_type": TEST_CONTENT_TYPE,
            "user_id": USER_ID,
            "conversation_id": CONVERSATION_ID
        }
        response = requests.post(f"{API_URL}/get_gcs_upload_url", json=payload)
        response.raise_for_status()
        data = response.json()
        upload_url = data["upload_url"]
        gcs_uri = data["gcs_uri"]
        print(f"   Success! Upload URL: {upload_url[:50]}...")
        print(f"   GCS URI: {gcs_uri}")
    except Exception as e:
        print(f"   FAILED to get url: {e}")
        if 'response' in locals():
            print(f"   Response Body: {response.text}")
        return

    # 2. Upload File
    print(f"\n2. Uploading content to GCS via PUT...")
    try:
        headers = {"Content-Type": TEST_CONTENT_TYPE}
        # Note: requests.put automatically sets content-length
        put_response = requests.put(upload_url, data=TEST_FILE_CONTENT, headers=headers)
        put_response.raise_for_status()
        print(f"   Success! File uploaded.")
    except Exception as e:
        print(f"   FAILED to upload file: {e}")
        if 'put_response' in locals():
            print(f"   Response Status: {put_response.status_code}")
            print(f"   Response Body: {put_response.text}")
        return

    print("\n--- Debugging Complete: flow appears operational from script ---")
    print("If this works but browser fails, it is likely a CORS issue on the bucket.")

if __name__ == "__main__":
    debug_upload()
