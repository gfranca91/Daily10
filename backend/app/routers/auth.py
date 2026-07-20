from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.services.auth import create_access_token, create_user, get_user_by_email, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/signup", response_model=AuthResponse)
def signup(payload: SignupRequest):
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="A senha precisa ter pelo menos 8 caracteres")

    if get_user_by_email(payload.email):
        raise HTTPException(status_code=409, detail="Já existe uma conta com este e-mail")

    user_id = create_user(payload.email, payload.password)
    return AuthResponse(access_token=create_access_token(user_id))


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    user = get_user_by_email(payload.email)
    if user is None or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")

    return AuthResponse(access_token=create_access_token(user["id"]))
