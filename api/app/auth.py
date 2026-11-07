from datetime import datetime, timezone
from typing import Annotated

from fastapi import Request, HTTPException, status, Depends
from sqlalchemy import select

from app.db import SessionDep
from app.models import User, AuthSession, Club
from app.security import SESSION_COOKIE, token_digest

def get_current_user(request: Request, session: SessionDep) -> User:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        auth = session.scalars(select(AuthSession).where(
            AuthSession.token_hash == token_digest(token),
            AuthSession.expires_at > datetime.now(timezone.utc)
        )).first()
        if auth is not None and auth.user.is_active:
            return auth.user
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Нужно войти в систему")

CurrentUser = Annotated[User, Depends(get_current_user)]

def ensure_can_manage(user: User, club: Club) -> None:
    if user.role == "admin":
        return
    if user.role == "organizer" and club in user.clubs:
        return
    raise HTTPException(status.HTTP_403_FORBIDDEN, f"Вы не организатор клуба «{club.name}»")