# Base image with Python
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install OS-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Set environment variable to avoid prompts during installation
ENV PIP_NO_INPUT=1

# Create a virtual environment and activate it
RUN python -m venv /venv

# Install dependencies using the venv's pip
RUN /venv/bin/pip install --upgrade pip setuptools wheel \
 && /venv/bin/pip install .

# Expose the virtual environment in the PATH
ENV PATH="/venv/bin:$PATH"

# Run setup script to initialize env variables and configuration
RUN python setup.py

# Entry point for the CLI tool
ENTRYPOINT ["codegpt"]
