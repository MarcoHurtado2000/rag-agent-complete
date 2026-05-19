from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.routes.upload import router as upload_router
from app.routes.ask import router as ask_router
from app.routes.auth_routes import router as auth_router
from app.routes.supervisor import router as supervisor_router
from app.routes.health import router as health_router
from app.database import cache_collection

app = FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Vercel routes send requests under /api/* (same as Next/Vercel convention).
api_router = APIRouter(prefix="/api")


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
api_router.include_router(upload_router)
api_router.include_router(ask_router)
api_router.include_router(auth_router)
api_router.include_router(supervisor_router)
api_router.include_router(health_router)
app.include_router(api_router)
