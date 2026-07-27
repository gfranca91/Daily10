from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from app.services.auth import (
    create_access_token,
    create_user,
    get_current_user_id,
    get_user_by_email,
    get_user_state,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])

CefrLevel = Literal["A1", "A2", "B1", "B2", "C1", "C2"]


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    declared_level: CefrLevel


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserState(BaseModel):
    declared_level: CefrLevel
    current_level: CefrLevel
    placement_test_done: bool


@router.post("/signup", response_model=AuthResponse)
def signup(payload: SignupRequest):
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="A senha precisa ter pelo menos 8 caracteres")

    if get_user_by_email(payload.email):
        raise HTTPException(status_code=409, detail="Já existe uma conta com este e-mail")

    user_id = create_user(payload.email, payload.password, payload.declared_level)
    return AuthResponse(access_token=create_access_token(user_id))


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    user = get_user_by_email(payload.email)
    if user is None or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")

    return AuthResponse(access_token=create_access_token(user["id"]))


@router.get("/me", response_model=UserState)
def me(user_id: int = Depends(get_current_user_id)):
    state = get_user_state(user_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return UserState(**state)
