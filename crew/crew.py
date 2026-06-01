import io
import logging
import os
import sys
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

import crewai.llms.cache as _crewai_cache
import litellm
from crewai import Crew, Process
from crewai_tools import MCPServerAdapter
from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .agents import FETCH_SERVER_PARAMS, SERVER_PARAMS, build_agents
from .tasks import build_tasks

# Load environment variables
load_dotenv()

# Setup OpenTelemetry
otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
resource = Resource(attributes={"service.name": "operations-assistant-crew"})

# Trace configuration
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otel_endpoint, insecure=True))
provider.add_span_processor(processor)

# Bypass restriction and set the tracer provider globally
trace._TRACER_PROVIDER = None
trace.set_tracer_provider(provider)

# Log configuration
logger_provider = LoggerProvider(resource=resource)
log_exporter = OTLPLogExporter(endpoint=otel_endpoint, insecure=True)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
set_logger_provider(logger_provider)

# Attach OTLP Logging Handler to standard Python logging root logger
handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

# Custom OpenTelemetry callback for Litellm
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


# Register the custom callback
litellm.success_callback = [custom_otel_success_callback]

# Monkey-patch to prevent 'cache_breakpoint' from being added to messages (Groq unsupported property bug)
_crewai_cache.mark_cache_breakpoint = lambda msg: msg

TRACES_DIR = Path(__file__).parent.parent / "traces"
TRACES_DIR.mkdir(exist_ok=True)


def run_crew(question: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    trace_path = TRACES_DIR / f"trace_{timestamp}.txt"
    buffer = io.StringIO()

    with redirect_stdout(buffer):
        with MCPServerAdapter(SERVER_PARAMS) as mcp_tools:
            with MCPServerAdapter(FETCH_SERVER_PARAMS) as fetch_tools:
                researcher, writer = build_agents(mcp_tools, fetch_tools)
                tasks = build_tasks(researcher, writer, question)

                crew = Crew(
                    agents=[researcher, writer],
                    tasks=tasks,
                    process=Process.sequential,
                    verbose=True,  # prints every agent step
                )

                result = crew.kickoff()

    trace_content = buffer.getvalue()
    trace_path.write_text(
        f"Question: {question}\n\nTrace:\n{trace_content}\n\nResult:\n{result}",
        encoding="utf-8",
    )
    print(f"\n Trace saved to: {trace_path}")
    return str(result)


if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "What is the return policy?"
    try:
        answer = run_crew(question)
        print("\n FINAL ANSWER :")
        print(answer)
    finally:
        # Flush and shutdown OTel providers
        provider.shutdown()
        logger_provider.shutdown()
