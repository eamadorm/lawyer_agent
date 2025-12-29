# DOF Scraper Pipeline

This directory contains the DOF (Diario Oficial de la Federación) scraping pipeline, which retrieves daily legal data and stores it in BigQuery.

## Overview

The pipeline is implemented as a Google Cloud Run Function (2nd Gen) that:
1.  Scrapes the DOF website for the current date.
2.  Parses the content.
3.  Loads the data into BigQuery.

## Architecture

-   **Cloud Function**: Python 3.12 function triggered via HTTP.
-   **BigQuery**: Destination for scraped data.
-   **Cloud Scheduler**: Triggers the function daily at 8:00 AM CST.

## Permissions

For the Cloud Scheduler job to successfully trigger the Cloud Function, the service account used by the scheduler must have the appropriate permissions.

**Service Account**: `dof-pipeline@learned-stone-454021-c8.iam.gserviceaccount.com`

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

## Setup & Deployment

The project includes a `Makefile` at the root to simplify deployment.

### Deploy Function

To deploy the Cloud Run Function:

```bash
make deploy-dof-pipeline
```

This command will:
1.  Export dependencies from the `dof_pipeline` group in `pyproject.toml`.
2.  Deploy the function `dof-scraper-function` to `us-central1`.
3.  Configure it with the necessary service account and environment variables.

### Schedule Job

To set up the daily schedule:

```bash
make schedule-dof-pipeline
```

### Local Testing

You can run the pipeline locally using `uv`:

```bash
uv run --group dof_pipeline -m pipelines.dof.main --start_date 01/01/2024 --end_date 31/12/2024
```
