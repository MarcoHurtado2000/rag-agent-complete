from fastapi import APIRouter, Depends, HTTPException
from app.models import Question
from app.rag import search, ask_gemini
from app.database import memory_collection, cache_collection, ensure_db_configured
from app.auth import require_auth
import hashlib

router = APIRouter()


@router.post("/ask")
async def ask_question(data: Question, user: dict = Depends(require_auth)):

    ensure_db_configured()

    if not data.question or not data.question.strip():
        raise HTTPException(status_code=400, detail="Pregunta vacia")

    question_hash = hashlib.md5(data.question.lower().strip().encode()).hexdigest()
    cached = await cache_collection.find_one({"hash": question_hash})
    if cached:
        return {
            "answer": cached["answer"],
            "context": cached["context"],
            "cached": True,
        }

    try:
        context = await search(data.question)
        response = ask_gemini(data.question, "\n".join(context))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error procesando pregunta: {str(e)[:200]}"
        )

    await memory_collection.insert_one(
        {
            "question": data.question,
            "response": response,
            "username": user.get("username", "anonymous"),
        }
    )

    await cache_collection.insert_one(
        {"hash": question_hash, "answer": response, "context": context}
    )

    return {"answer": response, "context": context, "cached": False}
