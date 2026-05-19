from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "rag_db")

client = AsyncIOMotorClient(MONGO_URI)

db = client[DB_NAME]

users_collection = db["users"]
memory_collection = db["memory"]
cache_collection = db["response_cache"]