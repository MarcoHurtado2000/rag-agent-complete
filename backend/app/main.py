from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback
import uuid

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


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    error_id = uuid.uuid4().hex
    # Logged in Vercel function logs for debugging.
    print(f"Unhandled exception error_id={error_id}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error_id": error_id},
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
