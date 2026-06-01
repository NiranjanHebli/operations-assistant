import logging
import os
import litellm
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Global variables to hold providers so we can shut them down later
_tracer_provider = None
_logger_provider = None


def setup_telemetry():
    """Initialize OpenTelemetry providers and Litellm callback."""
    global _tracer_provider, _logger_provider

    otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    resource = Resource(attributes={"service.name": "operations-assistant-crew"})

    # Trace configuration
    _tracer_provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint=otel_endpoint, insecure=True)
    )
    _tracer_provider.add_span_processor(processor)

    # Bypass restriction and set the tracer provider globally
    trace._TRACER_PROVIDER = None
    trace.set_tracer_provider(_tracer_provider)

    # Log configuration
    _logger_provider = LoggerProvider(resource=resource)
    log_exporter = OTLPLogExporter(endpoint=otel_endpoint, insecure=True)
    _logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
    set_logger_provider(_logger_provider)

    # Attach OTLP Logging Handler to standard Python logging root logger
    handler = LoggingHandler(level=logging.INFO, logger_provider=_logger_provider)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)

    # Register the custom Litellm callback
    _register_litellm_callback()


def _register_litellm_callback():
    tracer = trace.get_tracer("litellm-custom-tracer")

    def custom_otel_success_callback(kwargs, completion_response, start_time, end_time):
        model = kwargs.get("model", "unknown_model")
        messages = kwargs.get("messages", [])

        with tracer.start_as_current_span(f"litellm.completion: {model}") as span:
            # Log input prompt
            span.set_attribute("gen_ai.prompt", str(messages))

            # Log output completion
            if (
                completion_response
                and hasattr(completion_response, "choices")
                and len(completion_response.choices) > 0
            ):
                content = completion_response.choices[0].message.content
                span.set_attribute("gen_ai.completion", str(content))

    litellm.success_callback = [custom_otel_success_callback]


def shutdown_telemetry():
    """Flush and shutdown OpenTelemetry providers."""
    if _tracer_provider:
        _tracer_provider.shutdown()
    if _logger_provider:
        _logger_provider.shutdown()
