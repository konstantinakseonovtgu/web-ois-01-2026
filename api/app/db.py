import os
from collections.abc import Iterator
from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import BigInteger, DateTime, MetaData, Text, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://webois:webois@localhost:5433/webois"
)

engine = create_engine(DATABASE_URL, echo=os.environ.get("SQL_ECHO") == "1")

SessionLocal = sessionmaker(engine, expire_on_commit=False)

NAMING = {
    "pk": "%(table_name)s_pkey",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ix": "%(table_name)s_%(column_0_name)s_idx",
    "ck": "%(table_name)s_%(constraint_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING)
    type_annotation_map = {
        int: BigInteger,
        str: Text,
        datetime: DateTime(timezone=True)
    }

def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def violated_constraint(exc: IntegrityError) -> str | None:
    return getattr(getattr(exc.orig, "diag", None), "constraint_name", None)