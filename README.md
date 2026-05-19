# Agente RAG PDF

Sistema RAG (Retrieval-Augmented Generation) desarrollado con:

- FastAPI
- Astro
- MongoDB
- FAISS
- Sentence Transformers
- Gemini AI

Permite:
- Subir documentos PDF
- Generar embeddings
- Consultar información mediante IA
- Guardar conversaciones en MongoDB
- Autenticación de usuarios

---

# Tecnologías

## Backend
- FastAPI
- Motor
- MongoDB
- FAISS
- Sentence Transformers
- Gemini API

## Frontend
- Astro
- TailwindCSS

## Base de datos
- MongoDB

## Contenedores
- Docker
- Docker Compose

---

# Estructura del proyecto

```bash
rag-agent-system/
│
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── Dockerfile
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

# Instalación local

## 1. Clonar repositorio

```bash
git clone URL_DEL_REPOSITORIO
```

---

## 2. Backend

Entrar al backend:

```bash
cd backend
```

Crear entorno virtual:

```bash
python -m venv venv
```

Activar entorno:

### Windows

```bash
venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar servidor:

```bash
uvicorn app.main:app --reload
```

Backend:

```txt
http://localhost:8000
```

Swagger:

```txt
http://localhost:8000/docs
```

---

## 3. Frontend

Entrar al frontend:

```bash
cd frontend
```

Instalar dependencias:

```bash
npm install
```

Ejecutar Astro:

```bash
npm run dev
```

Frontend:

```txt
http://localhost:4321
```

---

# Variables de entorno

Crear archivo `.env` dentro de `backend/`

```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=rag_db
JWT_SECRET=tu_clave_secreta_aqui
GEMINI_API_KEY=TU_API_KEY
```

---

# Docker

## Construir contenedores

```bash
docker compose up --build
```

---

## Detener contenedores

```bash
docker compose down
```

---

# Endpoints principales

## Auth

### Registro

```http
POST /register
```

Body:
```json
{
  "username": "miusuario",
  "password": "miPassword123",
  "role": "user"
}
```

### Login

```http
POST /login
```

Response:
```json
{
  "token": "eyJ...",
  "role": "user"
}
```

---

## PDFs

### Subir PDF

```http
POST /upload
Authorization: Bearer <token>
```

---

## Chat

### Preguntar al agente

```http
POST /ask
Authorization: Bearer <token>
```

---

## Supervisor

### Ver historial

```http
GET /history
Authorization: Bearer <token>
```

Solo accesible para usuarios con rol `supervisor`.

---

# Funcionalidades

- Autenticación JWT
- RAG con FAISS
- Subida de PDFs
- Embeddings automáticos
- Chat IA
- Persistencia en MongoDB
- Frontend moderno
- Dockerizado

---

# Autor

Proyecto académico desarrollado para Ingeniería en Sistemas y Telecomunicaciones.