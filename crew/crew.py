import sys
from datetime import datetime

from crewai import Crew, Process
from crewai_tools import MCPServerAdapter
from dotenv import load_dotenv

from utils.logging_utils import Tee
from utils.patches import apply_patches
from utils.injection_guard import assert_clean
from utils.trace_writer import write_trace
from utils.reporting import write_run_report

from .agents import FETCH_SERVER_PARAMS, SERVER_PARAMS, build_agents
from .tasks import build_tasks

load_dotenv()
apply_patches()


def run_crew(question: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

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
                    verbose=True,
                )

                result = crew.kickoff()

                assert_clean(str(result), label="crew final output")
                write_run_report(timestamp, question, result, crew, tasks)
    finally:
        sys.stdout = original_stdout

    write_trace(timestamp, question, tee.getvalue(), result)
    return str(result)


if __name__ == "__main__":
    from utils.telemetry import setup_telemetry, shutdown_telemetry

    setup_telemetry()
    question = sys.argv[1] if len(sys.argv) > 1 else "What is the return policy?"
    try:
        answer = run_crew(question)
        print("\n FINAL ANSWER :")
        print(answer)
    finally:
        shutdown_telemetry()
