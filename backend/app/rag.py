import faiss
import numpy as np
from google import genai
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import pickle

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

dimension = 384

INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "faiss_index.index")
CHUNKS_PATH = os.path.join(os.path.dirname(__file__), "..", "document_chunks.pkl")

if os.path.exists(INDEX_PATH):
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
    embeddings = embedding_model.encode(chunks)
    index.add(np.array(embeddings).astype("float32"))
    document_chunks.extend(chunks)
    save_index()

def search(question):
    if index.ntotal == 0:
        return ["No hay documentos indexados aún. Sube un PDF primero."]

    question_embedding = embedding_model.encode([question])
    k = min(3, index.ntotal)
    D, I = index.search(
        np.array(question_embedding).astype("float32"),
        k=k
    )
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

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text