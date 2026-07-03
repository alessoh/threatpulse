"""Vercel serverless entrypoint.

Every request to the backend project is rewritten to this function (see
backend/vercel.json), and the ASGI scope preserves the original path, so the
FastAPI app routes exactly as it does under uvicorn.
"""

from app.main import app  # noqa: F401
