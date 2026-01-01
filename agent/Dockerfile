FROM python:3.12-slim
ARG UV_VERSION=0.5.4

# Upgrade pip and install the required uv version
RUN pip install --upgrade pip &&\
    pip install uv==${UV_VERSION}

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Export dependencies from the 'agent' group to requirements.txt
RUN uv export --group agent --no-hashes --format requirements-txt > requirements.txt

# Install dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the agent code
COPY agent ./agent

# Expose the API port
EXPOSE 8080

# Command to run the API
CMD ["uvicorn", "agent.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
