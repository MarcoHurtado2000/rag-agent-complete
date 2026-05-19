import faiss
import numpy as np
from google import genai
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import pickle

load_dotenv()

_genai_client = None
_embedding_model = None


def _get_genai_client() -> genai.Client:
    global _genai_client
    if _genai_client is not None:
        return _genai_client

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY no esta configurada")

    _genai_client = genai.Client(api_key=api_key)
    return _genai_client


def _get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        # Lazy-load: evita costo en cold start/import.
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


dimension = 384

# Vercel serverless file system is read-only except /tmp.
_TMP_DIR = os.getenv("RAG_TMP_DIR", "/tmp")
INDEX_PATH = os.path.join(_TMP_DIR, "faiss_index.index")
CHUNKS_PATH = os.path.join(_TMP_DIR, "document_chunks.pkl")

if os.path.exists(INDEX_PATH) and os.path.exists(CHUNKS_PATH):
    index = faiss.read_index(INDEX_PATH)
    with open(CHUNKS_PATH, "rb") as f:
        document_chunks = pickle.load(f)
else:
    index = faiss.IndexFlatL2(dimension)
    document_chunks = []


def save_index():
    faiss.write_index(index, INDEX_PATH)
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(document_chunks, f)


def add_to_index(chunks):
    global document_chunks
    embeddings = _get_embedding_model().encode(chunks)
    index.add(np.array(embeddings).astype("float32"))
    document_chunks.extend(chunks)
    save_index()


def search(question):
    if index.ntotal == 0:
        return ["No hay documentos indexados aún. Sube un PDF primero."]

    question_embedding = _get_embedding_model().encode([question])
    k = min(3, index.ntotal)
    D, I = index.search(np.array(question_embedding).astype("float32"), k=k)
    results = [document_chunks[i] for i in I[0] if i != -1]

    if not results:
        return ["No se encontraron resultados relevantes."]

    return results


def ask_gemini(question, context):
    prompt = f"""
    Responde usando SOLO el contexto.

    CONTEXTO:
    {context}

    PREGUNTA:
    {question}
    """

    response = _get_genai_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text
