from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.auth import CurrentUser, ensure_can_manage
from app.db import SessionDep, violated_constraint
from app.models import Event, Registration, User
from app.schemas import ErrorResponse, Participant, RegistrationRead

router = APIRouter(prefix="/api/events/{event_id}/registrations", tags=["Записи"])

UNAUTHORIZED = {401: {"model": ErrorResponse, "description": "Не выполнен вход"}}
NOT_FOUND = {404: {"model": ErrorResponse, "description": "Мероприятие не найдено"}}


@router.post(
    "",
    response_model=RegistrationRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        **UNAUTHORIZED,
        **NOT_FOUND,
        409: {"model": ErrorResponse, "description": "Нет мест, уже записан или запись закрыта (BR-2, BR-3, BR-4)"},
    },
    summary="Записаться на мероприятие",
)
def register(event_id: int, user: CurrentUser, session: SessionDep):
    event = session.get(Event, event_id, with_for_update=True)
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Мероприятие не найдено")

    if event.status != "published":
        raise HTTPException(status.HTTP_409_CONFLICT, "Запись открыта только на опубликованные мероприятия")
    if event.starts_at <= datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_409_CONFLICT, "Мероприятие уже началось")

    active = select(func.count()).select_from(Registration).where(
        Registration.event_id == event_id, Registration.status == "active"
    )
    if session.scalar(active.where(Registration.user_id == user.id)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Вы уже записаны на это мероприятие")
    if session.scalar(active) >= event.capacity:
        raise HTTPException(status.HTTP_409_CONFLICT, "Свободных мест нет")

    registration = Registration(event_id=event_id, user_id=user.id)
    session.add(registration)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        if violated_constraint(exc) == "registrations_one_active":
            raise HTTPException(status.HTTP_409_CONFLICT, "Вы уже записаны на это мероприятие") from exc
        raise
    return registration


@router.get(
    "",
    response_model=list[Participant],
    responses={
        **UNAUTHORIZED,
        **NOT_FOUND,
        403: {"model": ErrorResponse, "description": "Список видят только организаторы клуба и администратор (BR-10)"},
    },
    summary="Участники мероприятия",
)
def list_participants(event_id: int, user: CurrentUser, session: SessionDep):
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Мероприятие не найдено")
    ensure_can_manage(user, event.club)

    rows = session.execute(
        select(Registration, User)
        .join(User, User.id == Registration.user_id)
        .where(Registration.event_id == event_id, Registration.status == "active")
        .order_by(Registration.created_at)
    ).all()
    return [
        {"user_id": u.id, "full_name": u.full_name, "email": u.email, "created_at": r.created_at}
        for r, u in rows
    ]
