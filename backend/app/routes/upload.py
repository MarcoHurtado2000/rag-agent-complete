from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import os
import tempfile
import uuid

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

    if not file.filename:
        raise HTTPException(status_code=400, detail="Archivo invalido")

    # Basic validation before doing any heavy work.
    filename = (file.filename or "").strip()
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    # Avoid path traversal and collisions; keep writes inside /tmp.
    safe_name = os.path.basename(filename)
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}-{safe_name}")

    max_upload_mb = int(os.getenv("MAX_UPLOAD_MB", "20"))
    max_upload_bytes = max(1, max_upload_mb) * 1024 * 1024
    written = 0

    # Stream to disk to avoid loading the whole file in memory (important in serverless).
    try:
        with open(file_path, "wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB
                if not chunk:
                    break
                written += len(chunk)
                if written > max_upload_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Archivo demasiado grande (max {max_upload_mb}MB)",
                    )
                f.write(chunk)
    finally:
        try:
            await file.close()
        except Exception:
            pass

    try:
        # Useful for Vercel logs when debugging unexpected 500s.
        print(
            f"upload_pdf user={user.get('username')} filename={filename} bytes={written}"
        )

        # Debug knob for isolating Vercel issues (payload limits, timeouts, Gemini errors).
        # If enabled, we only store the file to /tmp and return immediately.
        if os.getenv("UPLOAD_STORE_ONLY", "0") == "1":
            return {
                "message": "Archivo recibido (store-only)",
                "bytes": written,
                "tmp_path": file_path,
            }

        print("upload_pdf stage=extract")
        text = extract_text(file_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error leyendo PDF: {str(e)[:200]}"
        )

    if not text.strip():
        raise HTTPException(status_code=400, detail="No se pudo extraer texto del PDF")

    chunks = chunk_text(text)
    print(f"upload_pdf stage=chunk chunks={len(chunks)}")

    try:
        if os.getenv("UPLOAD_SKIP_INDEX", "0") == "1":
            return {
                "message": "PDF procesado (sin indexar)",
                "chunks": len(chunks),
                "indexed": 0,
            }

        print(f"upload_pdf stage=index chunks={len(chunks)}")
        inserted = await add_to_index(chunks)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error indexando contenido: {str(e)[:200]}"
        )

    return {
        "message": "PDF procesado correctamente",
        "chunks": len(chunks),
        "indexed": inserted,
    }
