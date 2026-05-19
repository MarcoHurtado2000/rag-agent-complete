from fastapi import APIRouter
import os

from app.database import client


router = APIRouter()


@router.get("/health")
async def health():
    mongo_uri_set = bool(os.getenv("MONGO_URI"))
    gemini_key_set = bool(os.getenv("GEMINI_API_KEY"))

    db_ok = False
    db_error = None
    try:
        await client.admin.command("ping")
        db_ok = True
    except Exception as e:
        db_error = str(e)[:300]

    return {
        "ok": True,
        "env": {
            "mongo_uri_set": mongo_uri_set,
            "gemini_api_key_set": gemini_key_set,
        },
        "db": {
            "ok": db_ok,
            "error": db_error,
        },
    }
