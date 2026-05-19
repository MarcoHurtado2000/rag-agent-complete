from fastapi import APIRouter, HTTPException
from app.models import UserRegister, UserLogin
from app.database import users_collection, ensure_db_configured
from app.auth import hash_password, verify_password, create_token

router = APIRouter()


@router.post("/register")
async def register(user: UserRegister):

    ensure_db_configured()

    existing = await users_collection.find_one({"username": user.username})

    if existing:
        raise HTTPException(400, "Usuario ya existe")

    await users_collection.insert_one(
        {
            "username": user.username,
            "password": hash_password(user.password),
            "role": user.role,
        }
    )

    return {"message": "Usuario creado"}


@router.post("/login")
async def login(user: UserLogin):

    ensure_db_configured()

    db_user = await users_collection.find_one({"username": user.username})

    if not db_user:
        raise HTTPException(404, "Usuario no encontrado")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(401, "Credenciales inválidas")

    token = create_token({"username": db_user["username"], "role": db_user["role"]})

    return {"token": token, "role": db_user["role"]}
