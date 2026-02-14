from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import text

from .config import settings
from .database import Base, engine, SessionLocal
from .routers import auth, users, market, trading, learning, economy
from .seed import seed_if_needed


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_if_needed(db)
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    openapi_url="/openapi.json" if settings.enable_docs else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Idempotency-Key"],
)
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)
if settings.force_https:
    app.add_middleware(HTTPSRedirectMiddleware)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid4().hex
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(market.router)
app.include_router(trading.router)
app.include_router(learning.router)
app.include_router(economy.router)


@app.get("/health")
def health():
    return {"ok": True, "service": settings.app_name, "environment": settings.environment}


@app.get("/ready")
def ready():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"ok": True}
