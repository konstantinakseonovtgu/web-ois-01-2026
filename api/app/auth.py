from datetime import datetime, timezone
from typing import Annotated

from fastapi import Request, HTTPException, status, Depends
from sqlalchemy import select

from app.db import SessionDep
from app.models import User, AuthSession, Club
from app.security import SESSION_COOKIE, token_digest

def get_optional_user(request: Request, session: SessionDep) -> User | None:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        auth = session.scalars(
            select(AuthSession).where(
                AuthSession.token_hash == token_digest(token),
                AuthSession.expires_at > datetime.now(timezone.utc),
                )
        ).first()
        if auth is not None and auth.user.is_active:
            return auth.user
    return None


def get_current_user(user: Annotated[User | None, Depends(get_optional_user)]) -> User:
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Нужно войти в систему")
    return user


OptionalUser = Annotated[User | None, Depends(get_optional_user)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def can_manage(user: User | None, club: Club) -> bool:
    if user is None:
        return False
    return user.role == "admin" or (user.role == "organizer" and club in user.clubs)


def ensure_can_manage(user: User, club: Club) -> None:
    if can_manage(user, club):
        return
    raise HTTPException(status.HTTP_403_FORBIDDEN, f"Вы не организатор клуба «{club.name}»")
