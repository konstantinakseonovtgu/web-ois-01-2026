from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.auth import CurrentUser
from app.db import SessionDep
from app.models import Event, Registration
from app.schemas import ErrorResponse, MyRegistration

router = APIRouter(prefix="/api/me", tags=["Записи"])


@router.get(
    "/registrations",
    response_model=list[MyRegistration],
    responses={401: {"model": ErrorResponse, "description": "Не выполнен вход"}},
    summary="Мои записи",
)
def my_registrations(user: CurrentUser, session: SessionDep):
    rows = session.execute(
        select(Registration.id, Event)
        .join(Event, Event.id == Registration.event_id)
        .where(Registration.user_id == user.id, Registration.status == "active")
        .options(selectinload(Event.club), selectinload(Event.room))
        .order_by(Event.starts_at)
    ).all()
    return [
        {
            "registration_id": registration_id,
            "event_id": event.id,
            "title": event.title,
            "starts_at": event.starts_at,
            "ends_at": event.ends_at,
            "club": event.club,
            "room": event.room,
        }
        for registration_id, event in rows
    ]
