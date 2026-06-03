from pathlib import Path

TRACES_DIR = Path(__file__).parent.parent / "traces"
TRACES_DIR.mkdir(exist_ok=True)


def write_trace(timestamp: str, question: str, trace_content: str, result) -> None:
    trace_path = TRACES_DIR / f"trace_{timestamp}.txt"
    trace_path.write_text(
        f"Question: {question}\n\nTrace:\n{trace_content}\n\nResult:\n{result}",
        encoding="utf-8",
    )
    print(f"\n Trace saved to: {trace_path}")
