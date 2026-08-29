import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .core.config import settings
from .core.database import SessionLocal, get_db
from .core.exceptions import AppException, app_exception_handler
from .routers.v1.api import api_v1_router
from .routers.v1.health import check_health
from .seed.seed_data import seed_initial_categories

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} ({settings.APP_ENV})...")
    if settings.SEED_ON_STARTUP:
        logger.info("Executing startup category seeding...")
        db = SessionLocal()
        try:
            seed_initial_categories(db)
        except Exception as e:
            logger.error(f"Failed to seed initial categories on startup: {e}")
        finally:
            db.close()
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS Middleware
origins = settings.CORS_ORIGINS
if isinstance(origins, str):
    origins = [origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if "*" not in origins else ["*"],
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.onrender\.com|http://localhost:\d+",
    allow_credentials=True if "*" not in origins else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Global Exception Handler
app.add_exception_handler(AppException, app_exception_handler)

# Include v1 Router
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)


# Thin unversioned /health endpoint alias for platform health checks (Render / Uptime monitors)
@app.get("/health", tags=["Health"], include_in_schema=False)
def unversioned_health(response: Response, db: Session = Depends(get_db)):
    return check_health(response, db)
