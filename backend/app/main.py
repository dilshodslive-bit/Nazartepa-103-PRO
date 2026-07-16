"""FastAPI ilova fabrikasi (app factory)."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.core.middleware import RequestContextMiddleware
from app.modules.ambulance.router import router as ambulance_router
from app.modules.auth.router import router as auth_router
from app.modules.dispatch.router import router as dispatch_router
from app.modules.emergency.router import router as emergency_router
from app.modules.realtime.router import router as realtime_router
from app.modules.users.router import router as users_router
from app.shared.exceptions import AppError


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info(f"{settings.app_name} ishga tushdi ({settings.environment})")
    yield
    logger.info(f"{settings.app_name} to'xtatildi")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="AI-Powered Emergency Medical Dispatch Platform",
        lifespan=lifespan,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    # --- Middleware ---
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Domen xatoliklarini HTTP javobga aylantirish ---
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    # --- Routerlar ---
    app.include_router(auth_router, prefix=settings.api_v1_prefix)
    app.include_router(users_router, prefix=settings.api_v1_prefix)
    app.include_router(emergency_router, prefix=settings.api_v1_prefix)
    app.include_router(ambulance_router, prefix=settings.api_v1_prefix)
    app.include_router(dispatch_router, prefix=settings.api_v1_prefix)
    # Realtime WebSocket (prefikssiz: /ws/dispatch)
    app.include_router(realtime_router)

    # --- Sog'liq va metrika ---
    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "app": settings.app_name, "env": settings.environment}

    @app.get("/", tags=["system"])
    async def root() -> dict[str, str]:
        return {"message": "Nazartepa 103 API", "docs": "/docs"}

    return app


app = create_app()
