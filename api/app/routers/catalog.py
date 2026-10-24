from fastapi import APIRouter, HTTPException, status

from app import storage
from app.schemas import Club, ErrorResponse, Room

router = APIRouter(prefix="/api", tags=["Справочники"])


@router.get("/clubs", response_model=list[Club], summary="Клубы")
def list_clubs():
    return list(storage.CLUBS.values())


@router.get(
    "/clubs/{club_id}",
    response_model=Club,
    responses={404: {"model": ErrorResponse, "description": "Клуб не найден"}},
    summary="Один клуб",
)
def get_club(club_id: int):
    club = storage.CLUBS.get(club_id)
    if club is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Клуб не найден")
    return club


@router.get("/rooms", response_model=list[Room], summary="Аудитории")
def list_rooms():
    return list(storage.ROOMS.values())
