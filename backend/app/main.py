from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.upload import router as upload_router
from app.routes.ask import router as ask_router
from app.routes.auth_routes import router as auth_router
from app.routes.supervisor import router as supervisor_router
from app.database import cache_collection

app = FastAPI()


@app.on_event("startup")
async def startup():
    try:
        await cache_collection.create_index("created_at", expireAfterSeconds=86400)
    except Exception:
        pass


# CORS
app.add_middleware(
    CORSMiddleware,
    # Same-origin in Vercel (frontend calls /api/*). Keep localhost for dev.
    allow_origins=[
        "http://localhost:4321",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(upload_router)
app.include_router(ask_router)
app.include_router(auth_router)
app.include_router(supervisor_router)
