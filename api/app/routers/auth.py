from datetime import datetime, timezone

from fastapi import APIRouter, status, HTTPException, Response, Request
from sqlalchemy import select, func, delete
from sqlalchemy.exc import IntegrityError

from app.auth import CurrentUser
from app.schemas import ErrorResponse, UserRead, RegisterRequest, LoginRequest
from app.db import SessionDep, violated_constraint
from app.models import User, AuthSession
from app.security import (
    hash_password,
    verify_password,
    new_session_token,
    token_digest,
    SESSION_TTL, SESSION_COOKIE, COOKIE_SECURE
)

router = APIRouter(prefix="/api/auth", tags=["Вход"])

UNAUTHORIZED = {401: {"model": ErrorResponse, "description": "Не выполнен вход"}}

@router.post(
    "/resister",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse, "description": "Email уже зарегистрирован"}},
    summary="Регистрация студента",
)
def register(payload: RegisterRequest, session: SessionDep):
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        if violated_constraint(exc) == "users_email_key":
            raise HTTPException(status.HTTP_409_CONFLICT, "Этот email уже зарегистрирован") from exc
        raise
    return user

@router.post(
    "/login",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    responses={401: {"model": ErrorResponse, "description": "Неверный логин или пароль"}},
    summary="Вход",
)
def login(payload: LoginRequest, response: Response, session: SessionDep):
    user = session.scalars(
        select(User).where(func.lower(User.email) == payload.email.strip().lower())
    ).first()
    if not verify_password(user.password_hash if user else None, payload.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный email или пароль")
    if not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный email или пароль")

    token = new_session_token()
    session.add(
        AuthSession(
            token_hash=token_digest(token),
            user=user,
            expires_at=datetime.now(timezone.utc) + SESSION_TTL,
        )
    )
    session.commit()

    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=int(SESSION_TTL.total_seconds()),
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax"
    )

    return user

@router.post(
    "/loguot",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=UNAUTHORIZED,
    summary="Выход"
)
def logout(request: Request, response: Response, user: CurrentUser, session: SessionDep):
    token = request.cookies.get(SESSION_COOKIE, "")
    session.execute(delete(AuthSession).where(AuthSession.token_hash == token_digest(token)))
    session.commit()
    response.delete_cookie(SESSION_COOKIE, httponly=True, secure=COOKIE_SECURE, samesite="lax")

@router.get("/me", response_model=UserRead, responses=UNAUTHORIZED, summary="Кто я")
def me(user: CurrentUser):
    return user
