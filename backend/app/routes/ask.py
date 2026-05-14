from fastapi import APIRouter
from app.models import Question
from app.rag import search, ask_gemini
from app.database import memory_collection

router = APIRouter()

@router.post("/ask")
async def ask_question(data: Question):

    context = search(data.question)

    response = ask_gemini(
        data.question,
        "\n".join(context)
    )

    await memory_collection.insert_one({
        "question": data.question,
        "response": response
    })

    return {
        "answer": response,
        "context": context
    }