from fastapi import APIRouter, UploadFile, File, Depends
import os
import tempfile

from app.utils.pdf_loader import extract_text
from app.utils.chunker import chunk_text
from app.rag import add_to_index
from app.database import ensure_db_configured
from app.auth import require_auth

router = APIRouter()

UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), user: dict = Depends(require_auth)):

    ensure_db_configured()

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text(file_path)

    chunks = chunk_text(text)

    inserted = await add_to_index(chunks)

    return {
        "message": "PDF procesado correctamente",
        "chunks": len(chunks),
        "indexed": inserted,
    }
