# Operations Assistant

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org)
[![Dependency Manager](https://img.shields.io/badge/dependency--manager-uv-purple.svg)](https://github.com/astral-sh/uv)
[![Framework](https://img.shields.io/badge/framework-CrewAI-red.svg)](https://github.com/crewAIInc/crewAI)
[![Protocol](https://img.shields.io/badge/protocol-MCP-orange.svg)](https://modelcontextprotocol.io)

## What It Does
This is a multi-agent AI system (CrewAI) integrated with multiple Model Context Protocol (MCP) servers. The Assistant helps operations teams answer business questions automatically by querying local text documents, inventory data, and fetching external web resources.

## Architecture & MCP Servers
The project runs **two separate MCP servers** using the Model Context Protocol stdio transport:
1. **Core Operations Server (`server/mcp_server.py`)**:
   - `search_documents`: Search local text documentation.
   - `read_record`: Query product inventory records.
   - `save_report`: Save structured Markdown reports to the `outputs/` folder.
2. **Fetch Server (`server/mcp_fetch_server.py`)**:
   - `fetch_url`: Retrieve and parse HTML content from external URLs (e.g. for operations research).

Agents in the crew are specialized:
- **Operations Researcher**: Equipped with the `fetch_url` tool to gather external web context, plus `search_documents` and `read_record` for internal details.
- **Report Writer**: Equipped with the `save_report` tool to compile the findings.

## Quick Start
1. Clone the repository

2. Install uv: `pip install uv`

3. Install dependencies: `uv sync`

4. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and add your `GROQ_API_KEY`

5. Ask the Assistant a question:
   ```bash
   uv run python -m crew.crew "What is the return policy?"
   ```

6. View generated traces in the `traces/` folder and generated reports in the `outputs/` folder.

## Test the MCP Servers Alone
You can inspect and test the MCP tools visually using the MCP Inspector:

**Operations Server:**
```bash
npx @modelcontextprotocol/inspector uv run python server/mcp_server.py
```

**Fetch Server:**
```bash
npx @modelcontextprotocol/inspector uv run python server/mcp_fetch_server.py
```

## Run Tests
Run the automated test suite:
```bash
uv run pytest tests/ -v
```

## Observability & Custom Tracing
This project integrates OpenTelemetry to monitor agent workflows and track LLM calls, latency, and token usage. Since `litellm[proxy]` has conflicting dependencies with CrewAI, we use a custom LiteLLM telemetry exporter directly in `crew/crew.py` to capture `gen_ai.prompt` and `gen_ai.completion` spans.

1. **Start the Aspire Dashboard:**
   Make sure you have Docker installed and running, then spin up the dashboard container:
   ```bash
   docker compose up -d
   ```
2. **Open the Dashboard UI:**
   Navigate to [http://localhost:18888](http://localhost:18888) to access the dashboard.
3. **Capture Traces:**
   Run the assistant workflow normally:
   ```bash
   uv run python -m crew.crew "What is the return policy?"
   ```
   Traces will automatically export to the dashboard's OTLP endpoint (`http://localhost:4317`) for visual inspection under the **Traces** tab.

## Project Documentation
Additional design documentation and reflections are available in the [docs/](./docs/) folder:
- [Decision Log](./docs/decision_log.md): Outlines architectural decisions, framework selections, and alternatives considered or rejected.
- [Reflection](./docs/reflection.md): Post-build reflection covering agent roles, connection debugging, security mitigations, and production readiness guidelines.
