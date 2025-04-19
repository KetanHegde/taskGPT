# taskGPT

**taskGPT** is a Python-based command-line tool for running AI agents powered by OpenAI and Gemini models. It offers a guided setup experience, installs dependencies automatically, and configures API keys globally for seamless future use.

---

## ✨ Features

- 🤖 Run GPT-based agents from your terminal with a simple command
- 🔄 One-time setup for dependencies and API keys
- 🔐 Supports both OpenAI and Gemini API keys
- 💾 Persists API keys to system environment (Windows Registry / shell config)
- ⚙️ Automatically detects setup and avoids redundant installations
- 🐳 Docker support for isolated environments
- 📦 Installable via PyPI or GitHub

---

## 🚀 Installation

### Option 1: Install via `pip`

You can install taskGPT from either PyPI or GitHub:

#### 🔸 From PyPI

```bash
pip install taskgpt
```

#### 🔹 From GitHub

```bash
pip install git+https://github.com/KetanHegde/taskGPT.git
```

---

### Option 2: Run using Docker

If you prefer using containers, taskGPT works great inside Docker.

#### 📦 Build the Docker image

```bash
docker build -t taskgpt .
```

#### 🏃 Run the container

```bash
docker run -it --rm taskgpt
```

---

## 💡 Usage

Once installed, run the tool using:

```bash
taskgpt
```

### First Run

On the first launch, `taskgpt` will:

1. Install missing Python dependencies
2. Prompt you to enter `GEMINI_API_KEY` and/or `OPENAI_API_KEY` if not already set
3. Save them permanently in your system environment
4. Ask you to restart your terminal (only on first setup)

Subsequent runs will skip setup and launch the agent directly.

---

## 🛠 Development

To contribute to this project:

### 🧪 Clone the repository

```bash
git clone https://github.com/KetanHegde/taskGPT.git
cd taskGPT
```

### 📥 Install dependencies

```bash
pip install -e .
```

---