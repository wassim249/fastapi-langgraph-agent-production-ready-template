"""Convenience entrypoint for running the LiveKit phone agent.

Important: This file is named `phone_agent.py` (not `app.py`) to avoid shadowing
the `app/` Python package in this repository.
"""

from app.agents.phone_agent.executor import run

if __name__ == "__main__":
    run()
