# taskgpt/cli.py

from taskgpt.setup_env import run_setup_if_needed
from taskgpt.agent import run

def main():
    needs_restart = run_setup_if_needed()
    if needs_restart:
        return
    run()


