from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Служебное"])


@router.get("/health", summary="Проверка работоспособности")
def health():
    return {"status": "ok"}
