# Base image with Python
FROM python:3.11-slim

# Set working directory
WORKDIR /codegpt

# Install OS-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files into the container
COPY . .

# Set environment variable to avoid prompts during installation
ENV PIP_NO_INPUT=1

# Create and activate a virtual environment
RUN python -m venv /venv

# Install project dependencies
RUN /venv/bin/pip install --upgrade pip setuptools wheel \
 && /venv/bin/pip install .

# Ensure the virtual environment is in the PATH
ENV PATH="/venv/bin:$PATH"

# Run the setup script (to initialize environment or install extra deps)
RUN python setup.py

# Set the CLI entry point
ENTRYPOINT ["codegpt"]
