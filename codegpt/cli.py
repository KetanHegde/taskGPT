# codegpt/cli.py

from codegpt.setup_env import run_setup_if_needed
from codegpt.agent import run
import sys


def main():
    print(f"🧠 Using Python from: {sys.executable}")

    run_setup_if_needed()
    run()

