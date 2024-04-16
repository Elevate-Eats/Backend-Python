from fastapi import APIRouter
from app.api.endpoints import reportEndpoints

router = APIRouter()
router.include_router(reportEndpoints.router, tags = ["Reports"], prefix="/reports")