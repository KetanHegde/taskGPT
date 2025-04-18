
# CodeGPT

CodeGPT is a command-line tool that allows you to interact with OpenAI's GPT models locally, powered by Python. It provides an easy-to-use interface to manage and run GPT-based agents, and it automatically handles environment setup, including dependencies and API keys.

## Features

- Run GPT-based agents using a simple command-line interface (CLI).
- Automatically installs required Python packages.
- Automatically sets up the environment with an OpenAI API key (optional).
- Can be easily distributed and used via Docker or `pip`.

---

## Installation

### **Option 1: Install via `pip`**

You can install CodeGPT directly from PyPI or GitHub:

1. **Install via PyPI** (if published on PyPI):
   ```bash
   pip install codegpt
   ```

2. **Install via GitHub** (if hosted on GitHub):
   ```bash
   pip install git+https://github.com/your-username/codegpt.git
   ```

### **Option 2: Run using Docker**

If you prefer not to set up Python manually, you can use Docker to run CodeGPT in an isolated environment. 

#### Prerequisites:
- Docker must be installed on your machine. If you don’t have Docker, you can download it from [docker.com](https://www.docker.com/).

#### Steps to use Docker:

1. **Build the Docker Image**:
   In the project root directory, run:
   ```bash
   docker build -t codegpt .
   ```

2. **Run the Docker Container**:
   After the image is built, you can run the tool as follows:
   ```bash
   docker run -it --rm codegpt
   ```

This will start the tool in the Docker container, automatically installing dependencies and running the application.

---

## Usage

### Running CodeGPT

Once installed, you can use the `codegpt` command in the terminal.

1. **Start the agent**:
   ```bash
   codegpt
   ```

2. **Provide a task description** when prompted:
   ```bash
   Enter your task description:
   ```

---

## Development

To contribute to this project, follow the steps below to set up a local development environment.

### Clone the repository:

```bash
git clone https://github.com/your-username/codegpt.git
```

### Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
```

### Install dependencies:

```bash
pip install -e .
```

### Running tests:

```bash
python -m unittest discover
```
