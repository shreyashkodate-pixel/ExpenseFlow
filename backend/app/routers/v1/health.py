from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from ...core.database import get_db

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", status_code=status.HTTP_200_OK)
def check_health(response: Response, db: Session = Depends(get_db)):
    """Health check endpoint. Verifies PostgreSQL DB connectivity via SELECT 1 ping."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "db": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "error",
            "db": "disconnected",
            "version": "1.0.0",
            "detail": str(e)
        }
