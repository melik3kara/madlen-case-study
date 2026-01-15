"""OpenTelemetry setup and configuration."""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from ..config import get_settings


def setup_telemetry(app) -> None:
    """
    Set up OpenTelemetry tracing with Jaeger exporter.
    
    Args:
        app: FastAPI application instance
    """
    settings = get_settings()
    
    # Create a resource with service name
    resource = Resource.create({
        SERVICE_NAME: settings.otel_service_name,
        "service.version": settings.app_version,
        "deployment.environment": "development" if settings.debug else "production",
    })
    
    # Create tracer provider with resource
    provider = TracerProvider(resource=resource)
    
    # Configure OTLP exporter for Jaeger
    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.otel_exporter_otlp_endpoint,
        insecure=True,  # For local development
    )
    
    # Add span processor with batch processing
    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)
    
    # Set the tracer provider
    trace.set_tracer_provider(provider)
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(
        app,
        excluded_urls="/health,/docs,/openapi.json,/redoc",
    )
    
    # Instrument httpx for outgoing requests
    HTTPXClientInstrumentor().instrument()
    
    print(f"✅ OpenTelemetry configured - exporting to {settings.otel_exporter_otlp_endpoint}")


def shutdown_telemetry() -> None:
    """Shutdown telemetry and flush any pending spans."""
    provider = trace.get_tracer_provider()
    if hasattr(provider, 'shutdown'):
        provider.shutdown()
