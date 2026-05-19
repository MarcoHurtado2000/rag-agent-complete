from fastapi import APIRouter, Depends, HTTPException
from app.database import memory_collection
from app.auth import require_auth

router = APIRouter()

@router.get("/history")
async def history(user: dict = Depends(require_auth)):

    if user.get("role") != "supervisor":
        raise HTTPException(403, "Acceso denegado")

    data = []

    async for item in memory_collection.find():
        item["_id"] = str(item["_id"])
        data.append(item)

    return data