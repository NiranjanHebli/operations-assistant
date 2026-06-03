from pathlib import Path

TRACES_DIR = Path(__file__).parent.parent / "traces"
TRACES_DIR.mkdir(exist_ok=True)


def write_run_report(timestamp: str, question: str, result, crew, tasks) -> None:
    report_path = TRACES_DIR / f"run_report_{timestamp}.md"

    metrics = getattr(crew, "usage_metrics", None)
    total_tokens = getattr(metrics, "total_tokens", "N/A")
    prompt_tokens = getattr(metrics, "prompt_tokens", "N/A")
    completion_tokens = getattr(metrics, "completion_tokens", "N/A")
    successful_requests = getattr(metrics, "successful_requests", "N/A")

    lines = [
        "# Run Report",
        "",
        f"**Timestamp:** {timestamp}",
        f"**Question:** {question}",
        "",
        "## Token Usage",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Tokens | {total_tokens} |",
        f"| Prompt Tokens | {prompt_tokens} |",
        f"| Completion Tokens | {completion_tokens} |",
        f"| Successful LLM Requests | {successful_requests} |",
        "",
        "## Task Summary",
        "",
    ]

    for i, task in enumerate(tasks, 1):
        agent_name = getattr(task.agent, "role", "Unknown") if task.agent else "Unknown"
        desc_preview = (task.description or "")[:120].replace("\n", " ")
        lines += [
            f"### Task {i}: {agent_name}",
            f"- **Description:** {desc_preview}...",
            "",
        ]

    result_preview = str(result)[:500].replace("\n", " ")
    lines += [
        "## Result Preview",
        "",
        f"> {result_preview}...",
        "",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n Run report saved to: {report_path}")
