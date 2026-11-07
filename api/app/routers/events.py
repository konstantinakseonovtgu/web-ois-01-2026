from datetime import date, datetime, time, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import CurrentUser, ensure_can_manage
from app.db import SessionDep, violated_constraint
from app.models import Club, Event, Room
from app.schemas import ErrorResponse, EventCreate, EventPage, EventRead, EventUpdate

router = APIRouter(prefix="/api/events", tags=["Мероприятия"])

NOT_FOUND = {404: {"model": ErrorResponse, "description": "Мероприятие не найдено"}}
CONFLICT = {409: {"model": ErrorResponse, "description": "Нарушено бизнес-правило (BR-1, BR-6)"}}

FORBIDDEN = {
    401: {"model": ErrorResponse, "description": "Не выполнен вход"},
    403: {"model": ErrorResponse, "description": "Нет прав на мероприятия этого клуба (BR-8)"},
}

TOMSK = timezone(timedelta(hours=7))  # часовой пояс вуза: границы дат в фильтрах
ACTIVE = ("pending", "published")     # статусы, при которых мероприятие держит аудиторию


def get_event_or_404(session: Session, event_id: int) -> Event:
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Мероприятие не найдено")
    return event


def check_business_rules(session: Session, data: dict, event_id: int | None = None) -> Club:
    club = session.get(Club, data["club_id"])
    if club is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, f"Клуба {data['club_id']} нет")
    room = session.get(Room, data["room_id"])
    if room is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, f"Аудитории {data['room_id']} нет")

    if data["capacity"] > room.capacity:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Аудитория «{room.name}» вмещает {room.capacity} человек, а указано {data['capacity']}",
        )

    query = select(Event).where(
        Event.room_id == data["room_id"],
        Event.status.in_(ACTIVE),
        Event.starts_at < data["ends_at"],
        Event.ends_at > data["starts_at"],
        )
    if event_id is not None:
        query = query.where(Event.id != event_id)
    other = session.scalars(query.limit(1)).first()
    if other is not None:
        start = other.starts_at.astimezone(TOMSK)
        end = other.ends_at.astimezone(TOMSK)
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Аудитория «{room.name}» занята: {other.title}, {start:%d.%m %H:%M}–{end:%H:%M}",
        )
    return club


def commit_or_409(session: Session) -> None:
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        if violated_constraint(exc) == "events_room_no_overlap":
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Аудиторию только что заняли на это время"
            ) from exc
        raise


@router.get("", response_model=EventPage, summary="Афиша")
def list_events(
        session: SessionDep,
        club_id: Annotated[int | None, Query(description="Только мероприятия этого клуба")] = None,
        date_from: Annotated[date | None, Query(description="Начиная с даты, включительно")] = None,
        date_to: Annotated[date | None, Query(description="По дату, включительно")] = None,
        page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
        size: Annotated[int, Query(ge=1, le=100, description="Мероприятий на странице")] = 20,
):
    query = select(Event).where(Event.status == "published")
    if club_id is not None:
        query = query.where(Event.club_id == club_id)
    if date_from is not None:
        query = query.where(Event.starts_at >= datetime.combine(date_from, time.min, TOMSK))
    if date_to is not None:
        next_day = date_to + timedelta(days=1)
        query = query.where(Event.starts_at < datetime.combine(next_day, time.min, TOMSK))

    total = session.scalar(select(func.count()).select_from(query.subquery()))
    items = session.scalars(
        query.order_by(Event.starts_at, Event.id).offset((page - 1) * size).limit(size)
    ).all()
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/{event_id}", response_model=EventRead, responses=NOT_FOUND, summary="Одно мероприятие")
def get_event(event_id: int, session: SessionDep):
    return get_event_or_404(session, event_id)


@router.post(
    "",
    response_model=EventRead,
    status_code=status.HTTP_201_CREATED,
    responses=CONFLICT,
    summary="Создать мероприятие",
)
def create_event(payload: EventCreate, user: CurrentUser, session: SessionDep):
    data = payload.model_dump()
    club = check_business_rules(session, data)
    ensure_can_manage(user, club)
    event = Event(**data, author=user)
    session.add(event)
    commit_or_409(session)
    return event


@router.patch(
    "/{event_id}",
    response_model=EventRead,
    responses={**NOT_FOUND, **CONFLICT},
    summary="Изменить мероприятие",
)
def update_event(event_id: int, payload: EventUpdate, user: CurrentUser, session: SessionDep):
    event = get_event_or_404(session, event_id)
    ensure_can_manage(user, event.club)
    current = {name: getattr(event, name) for name in EventCreate.model_fields}
    merged = {**current, **payload.model_dump(exclude_unset=True)}
    try:
        checked = EventCreate.model_validate(merged).model_dump()
    except ValidationError as exc:
        errors = exc.errors(include_url=False, include_context=False, include_input=False)
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, errors) from exc
    check_business_rules(session, checked, event_id=event_id)
    for name, value in checked.items():
        setattr(event, name, value)
    commit_or_409(session)
    return event


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=NOT_FOUND,
    summary="Удалить мероприятие",
)
def delete_event(event_id: int, user: CurrentUser, session: SessionDep):
    event = get_event_or_404(session, event_id)
    ensure_can_manage(user, event.club)
    session.delete(event)
    session.commit()
