
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi_events.middleware import EventHandlerASGIMiddleware
import traceback
import sys
from app.api.routes.user_routes import router as user_router
from app.api.routes.tenant_routes import router as tenant_router
from app.ioc.container import Container, register_event_handlers
from app.infrastructure.database.connection import (
    create_db_and_tables,
    close_db_connections,
)
from fastapi_events.handlers.local import local_handler
from app.shared.config import get_settings
import uvicorn

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = Container()
    try:
        rabbitmq_service = container.rabbitmq_service()
        await rabbitmq_service.connect()
    except Exception as e:
        print(f"Warning: Could not connect to RabbitMQ: {e}")
    
    await create_db_and_tables()
    yield
    
    try:
        rabbitmq_service = container.rabbitmq_service()
        await rabbitmq_service.disconnect()
    except Exception as e:
        print(f"Warning: Error disconnecting from RabbitMQ: {e}")
    
    await close_db_connections()


def create_app() -> FastAPI:
    container = Container()
    register_event_handlers(container)

    app = FastAPI(
        title=settings.app_name,
        description="A FastAPI application with Clean Architecture, Event-Driven design, and Dependency Injection",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        try:
            sys.stdout.flush()
            print(f"\n{'='*60}", flush=True)
            print(f"🌐 REQUEST: {request.method} {request.url.path}", flush=True)
            try:
                response = await call_next(request)
                print(f"✅ RESPONSE: {response.status_code}", flush=True)
                print(f"{'='*60}\n", flush=True)
                return response
            except Exception as inner_e:
                sys.stdout.flush()
                print(f"❌ EXCEPTION in call_next: {type(inner_e).__name__}: {str(inner_e)}", flush=True)
                print(traceback.format_exc(), flush=True)
                print(f"{'='*60}\n", flush=True)
                raise
        except Exception as e:
            sys.stdout.flush()
            print(f"❌ EXCEPTION in middleware: {type(e).__name__}: {str(e)}", flush=True)
            print(traceback.format_exc(), flush=True)
            print(f"{'='*60}\n", flush=True)
            raise

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.events_enabled:
        app.add_middleware(EventHandlerASGIMiddleware, handlers=[local_handler])

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        sys.stdout.flush()
        print(f"\n{'='*60}", flush=True)
        print(f"❌❌❌ GLOBAL EXCEPTION HANDLER ❌❌❌", flush=True)
        print(f"URL: {request.url}", flush=True)
        print(f"Method: {request.method}", flush=True)
        print(f"Exception: {type(exc).__name__}: {str(exc)}", flush=True)
        print(f"Traceback:", flush=True)
        print(traceback.format_exc(), flush=True)
        print(f"{'='*60}\n", flush=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Internal server error: {str(exc)}"}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        sys.stdout.flush()
        print(f"\n{'='*60}", flush=True)
        print(f"⚠️ VALIDATION ERROR ⚠️", flush=True)
        print(f"URL: {request.url}", flush=True)
        print(f"Errors: {exc.errors()}", flush=True)
        print(f"{'='*60}\n", flush=True)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()}
        )

    app.include_router(user_router)
    app.include_router(tenant_router)

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "app": settings.app_name}

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)