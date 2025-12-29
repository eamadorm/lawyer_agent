# Lawyer Agent

An AI-powered legal assistant designed to analyze and answer questions based on the Diario Oficial de la Federación (DOF), live laws, and multiple other legal data sources.

## Project Structure

-   **`agent/`**: Contains the AI Agent application, tools, and logic.
-   **`pipelines/`**: Contains data ingestion pipelines (e.g., DOF scraper Cloud Function).
-   **`Makefile`**: Automation for running, deploying, and testing.

## Technology Stack

-   **Language**: Python 3.12+
-   **Frameworks**: Pydantic AI, FastAPI / Google Cloud Functions Framework.
-   **Cloud Provider**: Google Cloud Platform (Cloud Run, BigQuery, Cloud Scheduler).
-   **Package Manager**: `uv`

## Prerequisites

-   Python 3.12 or higher
-   [uv](https://github.com/astral-sh/uv) (for dependency management)
-   Google Cloud SDK (`gcloud`) configured with your project.

## Getting Started

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd lawyer_agent
    ```

2.  **Environment Setup**:
    Create a `.env` file in the root directory. Refer to internal documentation or `agent/README.md` for specific variables. as basic configuration:
    ```env
    PROJECT_ID=<your-project-id>
    REGION=<your-region>
    ```

3.  **Install Dependencies**:
    ```bash
    uv sync --all-groups
    ```

4.  **Run the Agent**:
    ```bash
    make run-agent
    ```

## Deploying DOF Pipeline

The DOF pipeline scrapes data daily. See `pipelines/dof/README.md` for detailed deployment instructions.

```bash
make deploy-dof-pipeline
```