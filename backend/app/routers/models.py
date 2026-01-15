"""Models router for handling model-related endpoints."""

from fastapi import APIRouter
from opentelemetry import trace

from ..schemas import ModelsResponse
from ..services import openrouter_service

router = APIRouter(prefix="/models", tags=["models"])
tracer = trace.get_tracer(__name__)


@router.get(
    "",
    response_model=ModelsResponse,
    summary="List available models",
    description="Get a list of all available free AI models from OpenRouter"
)
async def get_available_models() -> ModelsResponse:
    """
    Get the list of available free AI models.
    
    Returns models that can be used with the /chat endpoint.
    """
    with tracer.start_as_current_span("api.models.get_available") as span:
        models = await openrouter_service.get_available_models()
        
        span.set_attribute("models_count", len(models))
        
        return ModelsResponse(
            models=models,
            count=len(models)
        )
