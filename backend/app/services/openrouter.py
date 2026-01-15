"""OpenRouter API service for AI model interactions."""

import time
import httpx
from typing import Optional
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..config import get_settings
from ..schemas import ModelInfo, ImageData
from ..telemetry import track_openrouter_request

tracer = trace.get_tracer(__name__)


class OpenRouterService:
    """Service for interacting with the OpenRouter API."""
    
    # List of known free models on OpenRouter (updated January 2026)
    FREE_MODELS = [
        "xiaomi/mimo-v2-flash:free",           # 262K context - Best open-source, reasoning/coding
        "mistralai/devstral-2512:free",        # 262K context - Agentic coding specialist
        "deepseek/deepseek-r1-0528:free",      # 164K context - O1-level reasoning, 671B params
        "qwen/qwen3-coder:free",               # 262K context - Code generation, tool use
        "z-ai/glm-4.5-air:free",               # 131K context - Agent apps, thinking mode
        "tngtech/tng-r1t-chimera:free",        # 164K context - Creative storytelling
        "tngtech/deepseek-r1t-chimera:free",   # 164K context - Reasoning + efficiency
        "tngtech/deepseek-r1t2-chimera:free",  # 164K context - Roleplay, long context
        "google/gemma-3-27b-it:free",          # Gemma 3 - Multimodal
        "meta-llama/llama-3.3-70b-instruct:free",  # Llama 3.3 70B
    ]
    
    # Models that support image input (multimodal) - fallback list
    MULTIMODAL_MODELS = [
        "allenai/molmo-2-8b:free",
        "nvidia/nemotron-nano-12b-v2-vl:free",
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
                            # Check modality for image support - format is "text+image->text"
                            modality = model.get("architecture", {}).get("modality", "")
                            supports_images = (
                                model_id in self.MULTIMODAL_MODELS or
                                "vision" in model_id.lower() or
                                "image" in modality.lower()
                            )
                            
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
        start_time = time.perf_counter()
        
        with tracer.start_as_current_span("openrouter.send_message") as span:
            # Rich span attributes
            span.set_attribute("model.id", model)
            span.set_attribute("model.provider", model.split("/")[0] if "/" in model else "unknown")
            span.set_attribute("context.message_count", len(messages))
            span.set_attribute("has_image", image is not None)
            span.set_attribute("api.endpoint", f"{self.base_url}/chat/completions")
            
            if image:
                span.set_attribute("image.media_type", image.media_type)
                # Estimate image size from base64 (base64 is ~33% larger than binary)
                image_size = len(image.base64_data) * 3 // 4
                span.set_attribute("image.size_bytes", image_size)
            
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
                
                span.add_event("Sending request to OpenRouter", {
                    "model": model,
                    "message_count": len(messages),
                })
                
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=self._get_headers(),
                        json=payload
                    )
                    
                    duration = time.perf_counter() - start_time
                    span.set_attribute("http.status_code", response.status_code)
                    span.set_attribute("duration_seconds", duration)
                    
                    if response.status_code != 200:
                        error_data = response.json()
                        error_message = error_data.get("error", {}).get("message", "Unknown error")
                        span.set_status(Status(StatusCode.ERROR, error_message))
                        span.set_attribute("error.message", error_message)
                        track_openrouter_request(model, "error", duration)
                        raise Exception(f"OpenRouter API error: {error_message}")
                    
                    data = response.json()
                    
                    # Extract usage data if available
                    usage = data.get("usage", {})
                    if usage:
                        span.set_attribute("tokens.prompt", usage.get("prompt_tokens", 0))
                        span.set_attribute("tokens.completion", usage.get("completion_tokens", 0))
                        span.set_attribute("tokens.total", usage.get("total_tokens", 0))
                    
                    # Extract the response content
                    choices = data.get("choices", [])
                    if not choices:
                        raise Exception("No response choices returned from OpenRouter")
                    
                    content = choices[0].get("message", {}).get("content", "")
                    finish_reason = choices[0].get("finish_reason", "unknown")
                    
                    span.set_attribute("response.length", len(content))
                    span.set_attribute("response.word_count", len(content.split()))
                    span.set_attribute("response.finish_reason", finish_reason)
                    span.set_status(Status(StatusCode.OK))
                    span.add_event("Response received successfully", {
                        "response_length": len(content),
                        "finish_reason": finish_reason,
                    })
                    
                    # Track metrics
                    track_openrouter_request(model, "success", duration)
                    
                    return content
                    
            except httpx.TimeoutException as e:
                duration = time.perf_counter() - start_time
                span.set_status(Status(StatusCode.ERROR, "Request timeout"))
                span.set_attribute("error.type", "timeout")
                span.record_exception(e)
                track_openrouter_request(model, "timeout", duration)
                raise Exception("Request to OpenRouter timed out. Please try again.")
                
            except httpx.HTTPError as e:
                duration = time.perf_counter() - start_time
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.set_attribute("error.type", "http_error")
                span.record_exception(e)
                track_openrouter_request(model, "http_error", duration)
                raise Exception(f"HTTP error communicating with OpenRouter: {str(e)}")
                
            except Exception as e:
                duration = time.perf_counter() - start_time
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.set_attribute("error.type", type(e).__name__)
                span.record_exception(e)
                track_openrouter_request(model, "error", duration)
                raise


# Singleton instance
openrouter_service = OpenRouterService()
