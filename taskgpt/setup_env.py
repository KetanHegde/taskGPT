#!/usr/bin/env python3
import subprocess
import os
import sys
from pathlib import Path

SETUP_MARKER = Path(".setup_complete")

try:
    from dotenv import load_dotenv
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "python-dotenv"], check=True)
    from dotenv import load_dotenv


def install_packages():
    """Install required Python packages."""
    print("📦 Installing required packages...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "requests", "python-dotenv"], check=True)
        print("✅ Packages installed successfully.")
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages. Please install them manually.")
        return False
    return True


def get_or_set_api_key(key_name):
    """Check for required API key and prompt to create a .env file if missing."""
    load_dotenv()
    api_key = os.getenv(key_name)

    if api_key:
        print(f"✅ {key_name} found in environment variables.")
        return True

    print(f"⚠️  {key_name} not found.")
    user_input = input(f"Enter your {key_name} (or press Enter to skip): ").strip()
    if not user_input:
        print("❌ API key is required to proceed.")
        return False

    env_path = Path(".env")
    try:
        with env_path.open("a") as f:
            f.write(f"\n{key_name}={user_input}\n")
        print(f"✅ {key_name} saved to {env_path.resolve()}")
    except Exception as e:
        print(f"❌ Failed to write to .env file: {e}")
        return False

    return True


def setup():
    if SETUP_MARKER.exists():
        return True  # Already set up

    print("🚀 Setting up AI Task Agent...\n")

    if not install_packages():
        return False

    # Prompt for both keys, but not mandatory to have both
    get_or_set_api_key("GEMINI_API_KEY")
    get_or_set_api_key("OPENAI_API_KEY")

    SETUP_MARKER.write_text("setup done")
    print("\n✅ Setup complete!")
    return True


def run_setup_if_needed():
    setup()
