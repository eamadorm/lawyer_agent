# Federal Laws Scraper Pipeline

This pipeline scrapes the official list of Mexican Federal Laws from the Chamber of Deputies website and uploads the PDF documents to Google Cloud Storage (GCS).

## Features

- **Web Scraping:** Extracts law names, publication dates, and last reform dates.
- **Filename Sanitization:** Aggressively cleans filenames (removing accents, special characters, replacing parentheses/quotes) to ensure compatibility with GCS and file systems.
- **Parallel Processing:** Uses multi-threading (`ThreadPoolExecutor`) to download and upload up to 20 PDFs concurrently for high performance.
- **GCS Integration:** Uploads files directly to a specified Bucket and Folder in Google Cloud Storage.
- **Cloud Function Ready:** Structured as a Google Cloud Function (2nd Gen) for on-demand or scheduled execution.

## Configuration

Configuration is managed in `config.py` via `pydantic-settings`. Key settings include:

- `PROJECT_ID`: GCP Project ID.
- `BUCKET_NAME`: Target GCS Bucket (default: `lawyer_agent`).
- `GCS_FOLDER`: Target folder within the bucket (default: `federal_laws`).
- `URL`: Source URL for the laws.
- `MAX_WORKERS`: Number of concurrent threads for ingestion (default: `20`).

## Local Development

Prerequisites:
- `uv` installed.
- `gcloud` CLI authenticated with necessary permissions.

To run the pipeline locally (simulating the trigger):

```bash
make test-federal-laws-pipeline
```


## Permissions

For the Cloud Scheduler job to successfully trigger the Cloud Function, the service account used by the scheduler must have the appropriate permissions.

**Service Account**: `federal-laws-pipeline@<project-id>.iam.gserviceaccount.com`

**Required Roles**:
-   `roles/run.invoker`
-   `roles/cloudfunctions.invoker`

### IAM Policy Binding

You must explicitly grant the `roles/cloudfunctions.invoker` role to the service account on the function:

```bash
gcloud functions add-iam-policy-binding <cloud-function-name> \
  --region=<region> \
  --member="serviceAccount:<service-account>" \
  --role="roles/cloudfunctions.invoker" \
  --project=<project-id>
```

## Deployment

To deploy the pipeline as a Google Cloud Function:

```bash
make deploy-federal-laws-pipeline
```

This command will:
1. Export the dependencies from `pyproject.toml` (group `federal_laws`) to a `requirements.txt`.
2. Deploy the function `federal-laws-scraper-function` to the configured region.
3. Clean up the temporary `requirements.txt`.

## Project Structure

- `scraper.py`: Core logic for scraping, parsing, and uploading.
- `main.py`: Entry point for the Cloud Function (HTTP trigger).
- `config.py`: Configuration settings.
- `gcs_utils.py`: Helper functions for GCS interactions.
