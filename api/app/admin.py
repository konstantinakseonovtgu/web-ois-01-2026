import logging
import os
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from sqladmin import Admin, ModelView, action
from sqladmin.audit import LoggingAuditBackend
from sqladmin.authentication import AuthenticationBackend, get_current_user_id
from sqlalchemy import func, select
from starlette.requests import Request
from starlette.responses import RedirectResponse
from wtforms import SelectField

from app.db import SessionLocal, engine
from app.models import AuthSession, Club, Event, Registration, Room, User
from app.security import SESSION_TTL, new_session_token, token_digest, verify_password

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-not-a-secret")

TOMSK = timezone(timedelta(hours=7))
STATUSES = [
    ("pending", "на модерации"),
    ("published", "опубликовано"),
    ("rejected", "отклонено"),
    ("cancelled", "отменено"),
]
ROLES = [("student", "студент"), ("organizer", "организатор"), ("admin", "администратор")]

audit_log = logging.getLogger("sqladmin.audit")
audit_log.setLevel(logging.INFO)
audit_log.addHandler(logging.StreamHandler())


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = str(form.get("username", "")).strip().lower()
        password = str(form.get("password", ""))
        with SessionLocal() as session:
            user = session.scalars(select(User).where(func.lower(User.email) == email)).first()
            if not verify_password(user.password_hash if user else None, password):
                return False
            if not user.is_active or user.role != "admin":
                return False
            token = new_session_token()
            session.add(
                AuthSession(
                    token_hash=token_digest(token),
                    user=user,
                    expires_at=datetime.now(timezone.utc) + SESSION_TTL,
                )
            )
            session.commit()
            request.session.update({"token": token, "user_id": user.id})
        return True

    async def logout(self, request: Request) -> bool:
        token = request.session.get("token", "")
        with SessionLocal() as session:
            auth = session.scalars(
                select(AuthSession).where(AuthSession.token_hash == token_digest(token))
            ).first()
            if auth is not None:
                session.delete(auth)
                session.commit()
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False
        with SessionLocal() as session:
            auth = session.scalars(
                select(AuthSession).where(
                    AuthSession.token_hash == token_digest(token),
                    AuthSession.expires_at > datetime.now(timezone.utc),
                    )
            ).first()
            return auth is not None and auth.user.is_active and auth.user.role == "admin"


class EventAdmin(ModelView, model=Event):
    name = "Мероприятие"
    name_plural = "Мероприятия"
    icon = "fa-solid fa-calendar"
    column_list = [Event.id, Event.title, Event.club, Event.room, Event.starts_at, Event.status]
    column_searchable_list = [Event.title]
    column_sortable_list = [Event.id, Event.starts_at, Event.status]
    column_default_sort = [(Event.starts_at, False)]
    form_excluded_columns = [Event.created_at]
    form_overrides = {"status": SelectField}
    form_args = {
        "status": {"choices": STATUSES},
        "starts_at": {"display_timezone": TOMSK},
        "ends_at": {"display_timezone": TOMSK},
    }
    column_formatters = {
        Event.starts_at: lambda event, _: event.starts_at.astimezone(TOMSK).strftime("%d.%m.%Y %H:%M"),
    }
    column_labels = {
        Event.title: "Название",
        Event.club: "Клуб",
        Event.room: "Аудитория",
        Event.starts_at: "Начало",
        Event.ends_at: "Окончание",
        Event.status: "Статус",
        Event.reject_reason: "Причина отклонения",
    }

    async def _set_status(self, request: Request, new_status: str) -> RedirectResponse:
        pks = [pk for pk in request.query_params.get("pks", "").split(",") if pk]
        with SessionLocal() as session:
            for pk in pks:
                event = session.get(Event, int(pk))
                if event is not None and event.status == "pending":
                    event.status = new_status
                    audit_log.info(
                        "audit action=%s identity=event pk=%s user_id=%s",
                        new_status, pk, get_current_user_id(request),
                    )
            session.commit()
        return RedirectResponse(request.url_for("admin:list", identity=self.identity), status_code=302)

    @action(name="publish", label="Опубликовать", confirmation_message="Опубликовать выбранные мероприятия?")
    async def publish(self, request: Request) -> RedirectResponse:
        return await self._set_status(request, "published")

    @action(name="reject", label="Отклонить", confirmation_message="Отклонить выбранные мероприятия?")
    async def reject(self, request: Request) -> RedirectResponse:
        return await self._set_status(request, "rejected")


class ClubAdmin(ModelView, model=Club):
    name = "Клуб"
    name_plural = "Клубы"
    icon = "fa-solid fa-users"
    column_list = [Club.id, Club.name, Club.slug, Club.organizers]
    column_searchable_list = [Club.name]


class RoomAdmin(ModelView, model=Room):
    name = "Аудитория"
    name_plural = "Аудитории"
    icon = "fa-solid fa-door-open"
    column_list = [Room.id, Room.name, Room.building, Room.capacity]


class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"
    can_create = False
    can_delete = False
    column_list = [User.id, User.email, User.full_name, User.role, User.is_active]
    column_searchable_list = [User.email, User.full_name]
    column_details_exclude_list = [User.password_hash]
    form_columns = [User.full_name, User.role, User.is_active, User.clubs]
    form_overrides = {"role": SelectField}
    form_args = {"role": {"choices": ROLES}}


class RegistrationAdmin(ModelView, model=Registration):
    name = "Запись"
    name_plural = "Записи"
    icon = "fa-solid fa-ticket"
    can_create = False
    can_edit = False
    column_list = [Registration.id, Registration.event, Registration.user, Registration.status, Registration.created_at]


def setup_admin(app: FastAPI) -> Admin:
    admin = Admin(
        app,
        engine,
        title="WEB-ОИС: администрирование",
        authentication_backend=AdminAuth(secret_key=SECRET_KEY),
        audit_backend=LoggingAuditBackend(),
    )
    for view in (EventAdmin, ClubAdmin, RoomAdmin, UserAdmin, RegistrationAdmin):
        admin.add_view(view)
    return admin
