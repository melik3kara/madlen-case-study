"""Prometheus metrics for the chat application."""

import time
from functools import wraps
from typing import Callable, Any
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# Application info
APP_INFO = Info('app', 'Application information')

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Chat-specific metrics
CHAT_REQUESTS = Counter(
    'chat_requests_total',
    'Total chat requests',
    ['model', 'status']
)

CHAT_LATENCY = Histogram(
    'chat_request_duration_seconds',
    'Chat request latency in seconds',
    ['model'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

CHAT_MESSAGE_LENGTH = Histogram(
    'chat_message_length_chars',
    'Chat message length in characters',
    ['role'],
    buckets=[10, 50, 100, 250, 500, 1000, 2500, 5000]
)

# Model usage
MODEL_USAGE = Counter(
    'model_usage_total',
    'Model usage count',
    ['model_id', 'model_name']
)

# Session metrics
ACTIVE_SESSIONS = Gauge(
    'active_sessions_count',
    'Number of active chat sessions'
)

TOTAL_MESSAGES = Counter(
    'total_messages_count',
    'Total messages sent',
    ['role']
)

# Error metrics
ERROR_COUNT = Counter(
    'errors_total',
    'Total errors',
    ['type', 'endpoint']
)

# OpenRouter API metrics
OPENROUTER_REQUESTS = Counter(
    'openrouter_requests_total',
    'Total OpenRouter API requests',
    ['model', 'status']
)

OPENROUTER_LATENCY = Histogram(
    'openrouter_request_duration_seconds',
    'OpenRouter API request latency',
    ['model'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# Image processing metrics
IMAGE_UPLOADS = Counter(
    'image_uploads_total',
    'Total image uploads',
    ['media_type', 'status']
)


def init_metrics(app_name: str, app_version: str) -> None:
    """Initialize application metrics."""
    APP_INFO.info({
        'name': app_name,
        'version': app_version,
        'environment': 'development'
    })


def get_metrics() -> Response:
    """Generate Prometheus metrics response."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


def track_request(method: str, endpoint: str, status: int, duration: float) -> None:
    """Track an HTTP request."""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=str(status)).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)


def track_chat_request(model: str, status: str, duration: float, message_length: int) -> None:
    """Track a chat request."""
    CHAT_REQUESTS.labels(model=model, status=status).inc()
    CHAT_LATENCY.labels(model=model).observe(duration)
    CHAT_MESSAGE_LENGTH.labels(role='user').observe(message_length)


def track_chat_response(model: str, response_length: int) -> None:
    """Track a chat response."""
    CHAT_MESSAGE_LENGTH.labels(role='assistant').observe(response_length)
    TOTAL_MESSAGES.labels(role='assistant').inc()


def track_model_usage(model_id: str, model_name: str) -> None:
    """Track model usage."""
    MODEL_USAGE.labels(model_id=model_id, model_name=model_name).inc()


def track_error(error_type: str, endpoint: str) -> None:
    """Track an error."""
    ERROR_COUNT.labels(type=error_type, endpoint=endpoint).inc()


def track_openrouter_request(model: str, status: str, duration: float) -> None:
    """Track OpenRouter API request."""
    OPENROUTER_REQUESTS.labels(model=model, status=status).inc()
    OPENROUTER_LATENCY.labels(model=model).observe(duration)


def update_session_count(count: int) -> None:
    """Update active session count."""
    ACTIVE_SESSIONS.set(count)


def track_image_upload(media_type: str, status: str) -> None:
    """Track image upload."""
    IMAGE_UPLOADS.labels(media_type=media_type, status=status).inc()


def timed_operation(metric_name: str = None):
    """Decorator to time an operation."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.perf_counter() - start
                if metric_name:
                    REQUEST_LATENCY.labels(method='internal', endpoint=metric_name).observe(duration)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.perf_counter() - start
                if metric_name:
                    REQUEST_LATENCY.labels(method='internal', endpoint=metric_name).observe(duration)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator
