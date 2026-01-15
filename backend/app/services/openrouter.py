"""OpenRouter API service for AI model interactions."""

import httpx
from typing import Optional
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..config import get_settings
from ..schemas import ModelInfo, ImageData

tracer = trace.get_tracer(__name__)


class OpenRouterService:
    """Service for interacting with the OpenRouter API."""
    
    # List of known free models on OpenRouter
    FREE_MODELS = [
        "meta-llama/llama-3.2-3b-instruct:free",
        "meta-llama/llama-3.2-1b-instruct:free",
        "google/gemma-2-9b-it:free",
        "microsoft/phi-3-mini-128k-instruct:free",
        "microsoft/phi-3-medium-128k-instruct:free",
        "huggingfaceh4/zephyr-7b-beta:free",
        "openchat/openchat-7b:free",
        "qwen/qwen-2-7b-instruct:free",
    ]
    
    # Models that support image input
    MULTIMODAL_MODELS = [
        "google/gemma-2-9b-it:free",
    ]
    
    def __init__(self):
        """Initialize the OpenRouter service."""
        self.settings = get_settings()
        self.base_url = self.settings.openrouter_base_url
        self.api_key = self.settings.openrouter_api_key
    
    def _get_headers(self) -> dict:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": self.settings.app_name,
        }
    
    async def get_available_models(self) -> list[ModelInfo]:
        """Fetch available free models from OpenRouter."""
        with tracer.start_as_current_span("openrouter.get_available_models") as span:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    span.add_event("Fetching models from OpenRouter")
                    
                    response = await client.get(
                        f"{self.base_url}/models",
                        headers=self._get_headers()
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    all_models = data.get("data", [])
                    
                    # Filter to only free models
                    free_models = []
                    for model in all_models:
                        model_id = model.get("id", "")
                        # Check if model is free (pricing is 0 or in our free list)
                        pricing = model.get("pricing", {})
                        prompt_price = float(pricing.get("prompt", "1") or "1")
                        completion_price = float(pricing.get("completion", "1") or "1")
                        
                        is_free = (
                            prompt_price == 0 and completion_price == 0
                        ) or any(
                            free_id in model_id for free_id in [":free", "/free"]
                        )
                        
                        if is_free:
                            supports_images = model_id in self.MULTIMODAL_MODELS or \
                                "vision" in model_id.lower() or \
                                model.get("architecture", {}).get("modality", "") == "multimodal"
                            
                            free_models.append(ModelInfo(
                                id=model_id,
                                name=model.get("name", model_id),
                                description=model.get("description"),
                                context_length=model.get("context_length"),
                                supports_images=supports_images,
                                pricing=pricing
                            ))
                    
                    span.set_attribute("models_count", len(free_models))
                    span.set_status(Status(StatusCode.OK))
                    
                    # If API doesn't return free models, use our fallback list
                    if not free_models:
                        span.add_event("Using fallback model list")
                        free_models = [
                            ModelInfo(
                                id=model_id,
                                name=model_id.split("/")[-1].replace(":free", "").replace("-", " ").title(),
                                supports_images=model_id in self.MULTIMODAL_MODELS
                            )
                            for model_id in self.FREE_MODELS
                        ]
                    
                    return free_models
                    
            except httpx.HTTPError as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                # Return fallback list on error
                return [
                    ModelInfo(
                        id=model_id,
                        name=model_id.split("/")[-1].replace(":free", "").replace("-", " ").title(),
                        supports_images=model_id in self.MULTIMODAL_MODELS
                    )
                    for model_id in self.FREE_MODELS
                ]
    
    async def send_message(
        self,
        messages: list[dict],
        model: str,
        image: Optional[ImageData] = None
    ) -> str:
        """Send a message to the OpenRouter API and get a response."""
        with tracer.start_as_current_span("openrouter.send_message") as span:
            span.set_attribute("model", model)
            span.set_attribute("message_count", len(messages))
            span.set_attribute("has_image", image is not None)
            
            try:
                # Prepare the request payload
                payload = {
                    "model": model,
                    "messages": messages,
                }
                
                # Handle multimodal input if image is provided
                if image and messages:
                    last_message = messages[-1]
                    if last_message.get("role") == "user":
                        # Convert last message to multimodal format
                        messages[-1] = {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": last_message.get("content", "")
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{image.media_type};base64,{image.base64_data}"
                                    }
                                }
                            ]
                        }
                        payload["messages"] = messages
                
                span.add_event("Sending request to OpenRouter")
                
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=self._get_headers(),
                        json=payload
                    )
                    
                    span.set_attribute("response_status", response.status_code)
                    
                    if response.status_code != 200:
                        error_data = response.json()
                        error_message = error_data.get("error", {}).get("message", "Unknown error")
                        span.set_status(Status(StatusCode.ERROR, error_message))
                        raise Exception(f"OpenRouter API error: {error_message}")
                    
                    data = response.json()
                    
                    # Extract the response content
                    choices = data.get("choices", [])
                    if not choices:
                        raise Exception("No response choices returned from OpenRouter")
                    
                    content = choices[0].get("message", {}).get("content", "")
                    
                    span.set_attribute("response_length", len(content))
                    span.set_status(Status(StatusCode.OK))
                    span.add_event("Response received successfully")
                    
                    return content
                    
            except httpx.TimeoutException as e:
                span.set_status(Status(StatusCode.ERROR, "Request timeout"))
                span.record_exception(e)
                raise Exception("Request to OpenRouter timed out. Please try again.")
                
            except httpx.HTTPError as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise Exception(f"HTTP error communicating with OpenRouter: {str(e)}")
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise


# Singleton instance
openrouter_service = OpenRouterService()
