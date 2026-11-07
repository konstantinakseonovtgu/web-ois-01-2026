from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Table,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

club_organizers = Table(
    "club_organizers",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("club_id", ForeignKey("clubs.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('student', 'organizer', 'admin')", name="role_check"),
        Index("users_email_key", func.lower(text("email")), unique=True),
    )

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    email: Mapped[str]
    full_name: Mapped[str]
    password_hash: Mapped[str]
    role: Mapped[str] = mapped_column(server_default="student")
    is_active: Mapped[bool] = mapped_column(server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    clubs: Mapped[list["Club"]] = relationship(
        secondary=club_organizers, back_populates="organizers"
    )


class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(server_default="")

    organizers: Mapped[list[User]] = relationship(
        secondary=club_organizers, back_populates="clubs"
    )


class Room(Base):
    __tablename__ = "rooms"
    __table_args__ = (CheckConstraint("capacity > 0", name="capacity_check"),)

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    building: Mapped[str]
    capacity: Mapped[int] = mapped_column(Integer)  # integer, а не bigint: число мест


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint("length(title) BETWEEN 3 AND 200", name="title_check"),
        CheckConstraint("capacity > 0", name="capacity_check"),
        CheckConstraint(
            "status IN ('pending', 'published', 'rejected', 'cancelled')", name="status_check"
        ),
        CheckConstraint("ends_at > starts_at", name="time_order"),
        ExcludeConstraint(
            ("room_id", "="),
            (func.tstzrange(text("starts_at"), text("ends_at")), "&&"),
            name="events_room_no_overlap",
            using="gist",
            where=text("status IN ('pending', 'published')"),
        ),
    )

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"), index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str]
    description: Mapped[str] = mapped_column(server_default="")
    starts_at: Mapped[datetime] = mapped_column(index=True)
    ends_at: Mapped[datetime]
    capacity: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(server_default="pending")
    reject_reason: Mapped[str | None]
    cover_url: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    club: Mapped[Club] = relationship()
    room: Mapped[Room] = relationship()
    author: Mapped[User] = relationship()


class Registration(Base):
    __tablename__ = "registrations"
    __table_args__ = (
        CheckConstraint("status IN ('active', 'cancelled')", name="status_check"),
        Index(
            "registrations_one_active",
            "event_id",
            "user_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
    )

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(server_default="active")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    event: Mapped[Event] = relationship()
    user: Mapped[User] = relationship()
