import sys
from datetime import datetime
from pathlib import Path

from crewai import Crew, Process
from crewai_tools import MCPServerAdapter
from dotenv import load_dotenv

from utils.logging_utils import Tee
from utils.patches import apply_patches
from utils.telemetry import setup_telemetry, shutdown_telemetry

from .agents import FETCH_SERVER_PARAMS, SERVER_PARAMS, build_agents
from .tasks import build_tasks

# Load environment variables
load_dotenv()

# Apply patches immediately on import
apply_patches()

TRACES_DIR = Path(__file__).parent.parent / "traces"
TRACES_DIR.mkdir(exist_ok=True)


def run_crew(question: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    trace_path = TRACES_DIR / f"trace_{timestamp}.txt"

    original_stdout = sys.stdout
    tee = Tee(original_stdout)
    sys.stdout = tee

    try:
        with MCPServerAdapter(SERVER_PARAMS) as mcp_tools:
            with MCPServerAdapter(FETCH_SERVER_PARAMS) as fetch_tools:
                researcher, writer, fact_checker = build_agents(mcp_tools, fetch_tools)
                save_tool = [t for t in mcp_tools if t.name == "save_report"]
                tasks = build_tasks(
                    researcher, writer, fact_checker, question, save_tool
                )

                crew = Crew(
                    agents=[researcher, writer, fact_checker],
                    tasks=tasks,
                    process=Process.sequential,
                    verbose=True,  # prints every agent step
                )

                result = crew.kickoff()
    finally:
        sys.stdout = original_stdout

    trace_content = tee.getvalue()
    trace_path.write_text(
        f"Question: {question}\n\nTrace:\n{trace_content}\n\nResult:\n{result}",
        encoding="utf-8",
    )
    print(f"\n Trace saved to: {trace_path}")
    return str(result)


if __name__ == "__main__":
    setup_telemetry()

    question = sys.argv[1] if len(sys.argv) > 1 else "What is the return policy?"
    try:
        answer = run_crew(question)
        print("\n FINAL ANSWER :")
        print(answer)
    finally:
        shutdown_telemetry()
