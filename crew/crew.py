import sys
import io
from pathlib import Path
from datetime import datetime
from contextlib import redirect_stdout
from crewai import Crew, Process
from crewai_tools import MCPServerAdapter
from .agents import build_agents, SERVER_PARAMS
from .tasks import build_tasks
from dotenv import load_dotenv

import crewai.llms.cache as _crewai_cache
# Monkey-patch to prevent 'cache_breakpoint' from being added to messages (Groq unsupported property bug)
_crewai_cache.mark_cache_breakpoint = lambda msg: msg

load_dotenv()

TRACES_DIR = Path(__file__).parent.parent / "traces"
TRACES_DIR.mkdir(exist_ok=True)

def run_crew(question: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    trace_path = TRACES_DIR / f"trace_{timestamp}.txt"
    buffer = io.StringIO()

    with redirect_stdout(buffer):
        with MCPServerAdapter(SERVER_PARAMS) as mcp_tools:
            researcher, writer = build_agents(mcp_tools)
            tasks = build_tasks(researcher, writer, question)

            crew = Crew(
                agents=[researcher, writer],
                tasks=tasks,
                process=Process.sequential,
                verbose=True,          # prints every agent step
            )

            result = crew.kickoff()

    trace_content = buffer.getvalue()
    trace_path.write_text(
        f"Question: {question}\n\nTrace:\n{trace_content}\n\nResult:\n{result}",
        encoding="utf-8"
    )
    print(f"\n Trace saved to: {trace_path}")
    return str(result)

if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "What is the return policy?"
    answer = run_crew(question)
    print("\n FINAL ANSWER :")
    print(answer)
