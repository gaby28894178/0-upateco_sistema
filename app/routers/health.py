from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Chequeo de salud")
def healthcheck():
    return {"status": "ok"}