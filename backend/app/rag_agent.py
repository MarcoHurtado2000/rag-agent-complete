import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf import PdfReader
import os
from typing import List, Tuple
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

class RAGAgent:
    def __init__(self):
        # Configurar Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Configurar ChromaDB para embeddings
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.embedding_fn = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
            api_key=os.getenv("GEMINI_API_KEY")
        )
        
        # Colección actual (se creará por usuario/documento)
        self.current_collection = None
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extrae texto de un PDF"""
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    
    def split_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Divide el texto en chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        return text_splitter.split_text(text)
    
    def create_collection(self, user_id: str, filename: str):
        """Crea una colección única para cada usuario y documento"""
        collection_name = f"{user_id}_{filename.replace('.', '_')}"
        try:
            self.chroma_client.delete_collection(collection_name)
        except:
            pass
        self.current_collection = self.chroma_client.create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )
        return collection_name
    
    def add_document_chunks(self, chunks: List[str], metadata: List[dict] = None):
        """Añade chunks a la colección actual"""
        if not self.current_collection:
            raise Exception("No collection created. Call create_collection first.")
        
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        metadatas = metadata if metadata else [{"index": i} for i in range(len(chunks))]
        
        self.current_collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        return ids
    
    def search_similar_chunks(self, query: str, n_results: int = 3) -> Tuple[List[str], List[float]]:
        """Busca chunks similares a la pregunta"""
        if not self.current_collection:
            raise Exception("No collection found. Load document first.")
        
        results = self.current_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0], results['distances'][0]
    
    def generate_answer(self, question: str, context_chunks: List[str]) -> str:
        """Genera respuesta usando Gemini con contexto RAG"""
        context = "\n\n".join(context_chunks)
        
        prompt = f"""
        Eres un asistente experto que responde preguntas basadas ÚNICAMENTE en el contexto proporcionado.
        
        CONTEXTO:
        {context}
        
        PREGUNTA:
        {question}
        
        INSTRUCCIONES:
        1. Responde basándote EXCLUSIVAMENTE en el contexto dado
        2. Si la respuesta no está en el contexto, di: "No tengo suficiente información en el documento para responder esta pregunta"
        3. Sé conciso pero completo
        4. Si es relevante, cita partes específicas del contexto
        
        RESPUESTA:
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def load_document_collection(self, user_id: str, filename: str):
        """Carga una colección existente"""
        collection_name = f"{user_id}_{filename.replace('.', '_')}"
        try:
            self.current_collection = self.chroma_client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_fn
            )
            return True
        except:
            return False

rag_agent = RAGAgent()