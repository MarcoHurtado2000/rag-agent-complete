from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from fastapi import HTTPException

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "rag_db")


def ensure_db_configured() -> None:
    if not MONGO_URI:
        raise HTTPException(status_code=500, detail="MONGO_URI no esta configurada")


if MONGO_URI:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    users_collection = db["users"]
    memory_collection = db["memory"]
    cache_collection = db["response_cache"]
    rag_chunks_collection = db["rag_chunks"]
else:
    client = None
    db = None
    users_collection = None
    memory_collection = None
    cache_collection = None
    rag_chunks_collection = None
