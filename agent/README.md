# Lawyer Agent Service

This directory contains the core logic for the Lawyer Agent, including Pydantic AI integration and tool definitions.

## Overview

The Lawyer Agent is designed to assist with legal tasks, utilizing Google's Gemini models and various custom tools. It interacts with the DOF pipeline data via BigQuery, accesses live laws, and leverages other sources to provide comprehensive and up-to-date legal information.

## Features

-   **Gemini Integration**: Powered by Gemini 2.5 (configurable).
-   **Toolkit**: Includes tools for:
    -   Data retrieval from BigQuery.
    -   Web search (if enabled).

## Configuration

The agent is configured via environment variables. You should create a `.env` file in the root of the project (or within this directory if running standalone).

### Example `.env`

```env
# Google Cloud Platform
PROJECT_ID=<your-project-id>
REGION=<your-region>

# Model Configuration (Optional)
MODEL_NAME=gemini-2.5-pro
MODEL_TEMPERATURE=0.5
TOP_P=0.95
TOP_K=40
MAX_OUTPUT_TOKENS=10000

# Model Armor (Optional)
TEMPLATE_ID=your-model-armor-template-id
ARMOR_REGION=us-central1
```

## Running the Agent

### Using `uv` (Recommended)

To run the agent from the project root:

```bash
uv run --group agent -m agent.main
```

### Using Make

```bash
make run-agent
```
