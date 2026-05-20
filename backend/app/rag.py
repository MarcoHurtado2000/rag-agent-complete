import math
import os
from typing import List, Tuple

from dotenv import load_dotenv
from google import genai

from app.database import rag_chunks_collection, ensure_db_configured


load_dotenv()

_genai_client = None


def _get_genai_client() -> genai.Client:
    global _genai_client
    if _genai_client is not None:
        return _genai_client

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY no esta configurada")

    _genai_client = genai.Client(api_key=api_key)
    return _genai_client


def _embed_texts(texts: List[str]) -> List[List[float]]:
    # Gemini embeddings: avoid heavy local ML deps (torch/transformers).
    client = _get_genai_client()

    # Vercel/serverless: keep requests bounded. Large PDFs can create many chunks
    # and a single embed call can time out or exceed request limits.
    batch_size = int(os.getenv("EMBED_BATCH_SIZE", "32"))
    batch_size = max(1, min(batch_size, 128))

    out: List[List[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.models.embed_content(
            model=os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004"),
            contents=batch,
        )
        embeddings = resp.embeddings or []
        out.extend([e.values or [] for e in embeddings])

    return out


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return -1.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for i in range(len(a)):
        av = float(a[i])
        bv = float(b[i])
        dot += av * bv
        na += av * av
        nb += bv * bv
    if na <= 0.0 or nb <= 0.0:
        return -1.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


async def add_to_index(chunks: List[str]) -> int:
    ensure_db_configured()
    chunks = [c.strip() for c in chunks if c and c.strip()]
    if not chunks:
        return 0

    vectors = _embed_texts(chunks)
    docs = []
    for chunk, vec in zip(chunks, vectors):
        if not vec:
            continue
        docs.append({"text": chunk, "embedding": vec})

    if not docs:
        return 0

    await rag_chunks_collection.insert_many(docs)
    return len(docs)


async def search(question: str, k: int = 3) -> List[str]:
    ensure_db_configured()
    # Simple brute-force cosine search in MongoDB documents.
    # This is acceptable for small datasets and keeps serverless lightweight.
    question = (question or "").strip()
    if not question:
        return ["Pregunta vacia"]

    qvecs = _embed_texts([question])
    qvec = qvecs[0] if qvecs else []
    if not qvec:
        return ["No se pudo generar embedding para la pregunta"]

    cursor = rag_chunks_collection.find({}, {"text": 1, "embedding": 1})
    scored: List[Tuple[float, str]] = []
    async for doc in cursor:
        score = _cosine(qvec, doc.get("embedding") or [])
        scored.append((score, doc.get("text") or ""))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [t for s, t in scored[: max(1, k)] if t]
    return results or ["No hay documentos indexados aun. Sube un PDF primero."]


def ask_gemini(question: str, context: str) -> str:
    prompt = f"""
Responde usando SOLO el contexto.

CONTEXTO:
{context}

PREGUNTA:
{question}
"""

    response = _get_genai_client().models.generate_content(
        model=os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash"),
        contents=prompt,
    )
    return response.text
