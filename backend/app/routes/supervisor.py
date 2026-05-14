from fastapi import APIRouter
from app.database import memory_collection

router = APIRouter()

@router.get("/history")
async def history():

    data = []

    async for item in memory_collection.find():
        item["_id"] = str(item["_id"])
        data.append(item)

    return data