"""FastAPI application main module."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import chat_router, models_router
from .telemetry import setup_telemetry
from .telemetry.setup import shutdown_telemetry


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    settings = get_settings()
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    
    # Setup OpenTelemetry
    setup_telemetry(app)
    
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
    
    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint for container orchestration."""
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
        }
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health",
        }
    
    return app


# Create application instance
app = create_app()
