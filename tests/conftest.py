"""Shared pytest setup."""

import os

# Settings are read at import time; the test environment skips the
# production-only secret checks so the app modules can be imported.
os.environ.setdefault("APP_ENV", "test")
