from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.db import SessionDep
from app.schemas import Club, ErrorResponse, Room
from app.models import Club as ClubModel
from app.models import Room as RoomModel

router = APIRouter(prefix="/api", tags=["Справочники"])


@router.get("/clubs", response_model=list[Club], summary="Клубы")
def list_clubs(session: SessionDep):
    return session.scalars(select(ClubModel)).order_by(ClubModel.name).all()


@router.get(
    "/clubs/{club_id}",
    response_model=Club,
    responses={404: {"model": ErrorResponse, "description": "Клуб не найден"}},
    summary="Один клуб",
)
def get_club(club_id: int, session: SessionDep):
    club = session.get(ClubModel, club_id)
    if club is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Клуб не найден")
    return club


@router.get("/rooms", response_model=list[Room], summary="Аудитории")
def list_rooms(session: SessionDep):
    return session.scalars(select(RoomModel).order_by(RoomModel.name)).all()
