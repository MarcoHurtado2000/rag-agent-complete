import os
import sys


# Vercel runs Python functions from the repository root. Our FastAPI app lives in
# backend/app, so we add backend/ to sys.path to make `import app.*` work.
_BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(_BACKEND_DIR))

from app.main import app  # noqa: E402
