# Base image with Python
FROM python

# Set working directory
WORKDIR /taskgpt

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
RUN python taskgpt/setup_env.py

# Set the CLI entry point
ENTRYPOINT ["taskgpt"]
