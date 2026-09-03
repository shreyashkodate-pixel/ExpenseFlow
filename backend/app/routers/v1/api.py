from fastapi import APIRouter
from .auth import router as auth_router
from .categories import router as categories_router
from .expenses import router as expenses_router
from .budgets import router as budgets_router
from .dashboard import router as dashboard_router
from .analytics import router as analytics_router
from .health import router as health_router
from .ai import router as ai_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(categories_router)
api_v1_router.include_router(expenses_router)
api_v1_router.include_router(budgets_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(health_router)
api_v1_router.include_router(ai_router)


