from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "rag_db")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI no esta configurada")

client = AsyncIOMotorClient(MONGO_URI)

db = client[DB_NAME]

users_collection = db["users"]
memory_collection = db["memory"]
cache_collection = db["response_cache"]

# RAG storage (chunks + embeddings)
rag_chunks_collection = db["rag_chunks"]
