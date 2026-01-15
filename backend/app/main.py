"""FastAPI application main module."""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .config import get_settings
from .routers import chat_router, models_router
from .telemetry import setup_telemetry, init_metrics, get_metrics, track_request
from .telemetry.setup import shutdown_telemetry


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to track request metrics."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start_time
        
        # Track metrics for non-health endpoints
        if request.url.path not in ['/health', '/metrics']:
            track_request(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code,
                duration=duration
            )
        
        # Add timing header
        response.headers['X-Response-Time'] = f'{duration:.3f}s'
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    settings = get_settings()
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down application...")
    shutdown_telemetry()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="""
        AI Chat Application API
        
        A web-based chat application that allows interaction with multiple AI language models
        through OpenRouter as a gateway.
        
        ## Features
        
        * **Chat**: Send messages and receive AI responses
        * **Models**: Browse available free AI models
        * **History**: View current session chat history
        * **Telemetry**: Full OpenTelemetry tracing with Jaeger
        
        ## OpenTelemetry
        
        All API requests are traced and exported to Jaeger for monitoring and debugging.
        Access Jaeger UI at http://localhost:16686
        """,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    # Setup OpenTelemetry BEFORE adding middleware
    setup_telemetry(app)
    
    # Initialize metrics
    init_metrics(settings.app_name, settings.app_version)
    
    # Add metrics middleware
    app.add_middleware(MetricsMiddleware)
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routers
    app.include_router(chat_router, prefix="/api")
    app.include_router(models_router, prefix="/api")
    
    # Health check endpoint with detailed status
    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint for container orchestration."""
        from .services import chat_history_service
        
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "active_sessions": len(chat_history_service._sessions),
            "current_session_id": chat_history_service.current_session_id,
        }
    
    # Prometheus metrics endpoint
    @app.get("/metrics", tags=["monitoring"], include_in_schema=False)
    async def metrics():
        """Prometheus metrics endpoint."""
        return get_metrics()
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health",
            "metrics": "/metrics",
            "jaeger": "http://localhost:16686",
        }
    
    return app


# Create application instance
app = create_app()
