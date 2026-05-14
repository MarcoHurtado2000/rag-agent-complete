from fastapi import APIRouter, UploadFile, File
import os

from app.utils.pdf_loader import extract_text
from app.utils.chunker import chunk_text
from app.rag import add_to_index

router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text(file_path)

    chunks = chunk_text(text)

    add_to_index(chunks)

    return {
        "message": "PDF procesado correctamente",
        "chunks": len(chunks)
    }