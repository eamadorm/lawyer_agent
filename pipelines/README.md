# Data Pipelines

This directory contains the independent data ingestion microservices for the Lawyer Agent system.

Each pipeline is designed to be deployed as a Google Cloud Function (or Cloud Run service) and is responsible for a specific data source.

## Available Pipelines

| Pipeline | Directory | Description | Trigger |
| :--- | :--- | :--- | :--- |
| **DOF Scraper** | [`dof/`](./dof/) | Scrapes the *Diario Oficial de la Federación* daily for legal updates. | Scheduled (Daily 8:00 AM) |
| **Federal Laws** | [`federal_laws/`](./federal_laws/) | Scrapes and downloads the full catalog of Federal Laws from `diputados.gob.mx`. | Scheduled (Daily 9:00 AM) |

## Usage

Each pipeline has its own `README.md` with specific details. However, they share a common deployment pattern via the project's root `Makefile`.

### Common Commands

-   **Test locally:**
    ```bash
    make test-<pipeline-name>
    # Example: make test-federal-laws-pipeline
    ```

-   **Deploy to GCP:**
    ```bash
    make deploy-<pipeline-name>
    # Example: make deploy-dof-pipeline
    ```
