import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import configure_logging, request_id_context
from app.core.responses import error_response
from app.db.seed import seed_demo_data
from app.db.session import SessionLocal
from app.jobs.scheduler import start_scheduler, stop_scheduler
from app.security.encryption import EncryptionService
from app.storage.file_manager import FileManager

configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    FileManager().ensure_dirs()
    db = SessionLocal()
    try:
        EncryptionService().ensure_pgcrypto_extension(db)
        if settings.seed_demo_data:
            seed_demo_data(db)
        db.commit()
    finally:
        db.close()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
    request_id_context.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content=error_response(exc.message, code=exc.code, field=exc.field))


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0] if exc.errors() else {"msg": "Validation failed"}
    return JSONResponse(status_code=422, content=error_response(first_error.get("msg", "Validation failed"), code="validation_error"))


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(status_code=500, content=error_response("Internal server error", code="internal_error"))


app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
