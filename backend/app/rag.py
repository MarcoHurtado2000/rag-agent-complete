import faiss
import numpy as np
from google import genai
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

dimension = 384

index = faiss.IndexFlatL2(dimension)

document_chunks = []

def add_to_index(chunks):
    global document_chunks

    embeddings = embedding_model.encode(chunks)

    index.add(np.array(embeddings).astype("float32"))

    document_chunks.extend(chunks)

def search(question):
    question_embedding = embedding_model.encode([question])

    D, I = index.search(
        np.array(question_embedding).astype("float32"),
        k=3
    )

    results = [document_chunks[i] for i in I[0]]

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