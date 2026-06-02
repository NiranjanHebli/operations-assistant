# Operations Assistant

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org)
[![Dependency Manager](https://img.shields.io/badge/dependency--manager-uv-purple.svg)](https://github.com/astral-sh/uv)
[![Framework](https://img.shields.io/badge/framework-CrewAI-red.svg)](https://github.com/crewAIInc/crewAI)
[![Protocol](https://img.shields.io/badge/protocol-MCP-orange.svg)](https://modelcontextprotocol.io)
[![FastMCP](https://img.shields.io/badge/library-FastMCP-yellow.svg)](https://github.com/jlowin/fastmcp)
[![Inference](https://img.shields.io/badge/inference-Groq-black.svg)](https://groq.com)
[![Observability](https://img.shields.io/badge/observability-OpenTelemetry-blueviolet.svg)](https://opentelemetry.io)
[![Tracing](https://img.shields.io/badge/tracing-Langfuse-green.svg)](https://langfuse.com)
[![LLM Router](https://img.shields.io/badge/router-LiteLLM-lightgrey.svg)](https://github.com/BerriAI/litellm)

## What It Does
This is a multi-agent AI system (CrewAI) integrated with multiple Model Context Protocol (MCP) servers. The Assistant helps operations teams answer business questions automatically by querying local text documents, inventory data, and fetching external web resources.

## Architecture & MCP Servers

```mermaid
%%{init: {'themeVariables': {'edgeLabelBackground':'transparent'}}}%%
graph TD
    classDef mainSubgraph fill:none,stroke:#888,stroke-width:1px,rx:5,ry:5,color:#fff;
    classDef redL1 fill:#990000,stroke:#ff4d4d,stroke-width:2px,color:#fff;
    classDef blueL2 fill:#003399,stroke:#4d79ff,stroke-width:2px,color:#fff;
    classDef yellowL3 fill:#997a00,stroke:#ffcc00,stroke-width:2px,color:#fff;
    classDef greenL4 fill:#006600,stroke:#33cc33,stroke-width:2px,color:#fff;
    classDef orangeL5 fill:#cc5200,stroke:#ff9933,stroke-width:2px,color:#fff;

    User(["User"])
    Crew["CrewAI Workflow"]
    class User,Crew redL1;

    User --> Crew

    subgraph CrewAIAgents["CrewAI Agents"]
        OR["Operations Researcher"]
        FC["Fact Checker"]
        RW["Report Writer"]
        class OR,RW,FC blueL2;
    end
    class CrewAIAgents mainSubgraph;

    Crew --> OR
    Crew --> FC
    Crew --> RW

    subgraph MCPServers["MCP Servers"]
        Fetch["Fetch Server<br/>(Stdio)"]
        Core["Core Operations Server<br/>(SSE: localhost:8000)"]
        class Core,Fetch yellowL3;
    end
    class MCPServers mainSubgraph;

    subgraph FetchTools["Fetch Tools (Stdio)"]
        fetch_url["fetch_url<br/>Reads Web HTML"]
        class fetch_url greenL4;
    end
    class FetchTools mainSubgraph;

    subgraph CoreTools["Core Tools (SSE)"]
        search_documents["search_documents<br/>Reads data/documents/"]
        read_record["read_record<br/>Reads inventory.csv"]
        save_report["save_report<br/>Writes to outputs/"]
        class search_documents,read_record,save_report greenL4;
    end
    class CoreTools mainSubgraph;

    %% Independent output node with new orange styling
    Draft(("Draft Report"))
    class Draft orangeL5;

    Fetch --- fetch_url
    Core --- search_documents
    Core --- read_record
    Core --- save_report

    OR -->|"Uses"| fetch_url
    OR -->|"Uses"| search_documents
    OR -->|"Uses"| read_record

    FC -->|"Uses"| search_documents
    FC -->|"Uses"| read_record
    FC -->|"Uses"| save_report

    RW -->|"Synthesises"| Draft
```

The project runs **two separate MCP servers** using different transports:
1. **Core Operations Server (`server/mcp_server.py`)** — runs over **SSE (Server-Sent Events)** on `http://localhost:8000/sse`:
   - `search_documents`: Search local text documentation.
   - `read_record`: Query product inventory records.
   - `save_report`: Save structured Markdown reports to the `outputs/` folder.
2. **Fetch Server (`server/mcp_fetch_server.py`)** — runs over **Stdio** (spawned inline by the crew):
   - `fetch_url`: Retrieve and parse HTML content from external URLs (e.g. for operations research).

Agents in the crew are specialized:
- **Operations Researcher**: Equipped with the `fetch_url` tool to gather external web context, plus `search_documents` and `read_record` for internal details.
- **Report Writer**: Synthesises the Researcher's findings into a clean, structured Markdown report.
- **Fact Checker**: Cross-references the draft report against retrieved evidence, corrects unsupported claims, and gates saving behind human approval (HITL).

## Sample Data
The repository includes a set of sample data used by the MCP servers to answer operations questions:
- `data/documents/`: A folder containing small text files (e.g., policies, tickets). The `search_documents` tool searches through these files.
- `data/inventory.csv`: A CSV file containing mock product inventory records. The `read_record` tool queries specific records from this file by their ID.

## Quick Start
1. Clone the repository

2. Install uv: `pip install uv`

3. Install dependencies: `uv sync`

4. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and add your `GROQ_API_KEY`. (Optionally, also add your Langfuse keys to enable cloud tracing).

5. **Start the Core MCP server** (SSE mode) in a dedicated terminal:
   ```bash
   uv run python server/mcp_server.py
   ```
   You should see Uvicorn start up on `http://0.0.0.0:8000`. Keep this terminal open.

6. In a **second terminal**, ask the Assistant a question:
   ```bash
     uv run python -m crew.crew "What is the return policy?"
   ```

7. View generated traces in the `traces/` folder and generated reports in the `outputs/` folder.

## Test the MCP Servers Alone
You can inspect and test the MCP tools visually using the MCP Inspector.

**Operations Server (SSE mode):**
Start the server first, then connect the inspector to it:
```bash
# Terminal 1 — start SSE server
uv run python server/mcp_server.py

# Terminal 2 — connect inspector
npx @modelcontextprotocol/inspector --cli http://localhost:8000/sse --transport sse
```

**Fetch Server (Stdio mode):**
```bash
npx @modelcontextprotocol/inspector uv run python server/mcp_fetch_server.py
```

## Run Tests
Run the automated test suite:
```bash
uv run pytest tests/ -v
```

## Observability & Custom Tracing
This project integrates OpenTelemetry to monitor agent workflows and track LLM calls, latency, and token usage, utilizing both local Aspire Dashboard and cloud Langfuse tracking.

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
   Traces will automatically export to the dashboard's OTLP endpoint (`http://localhost:4317`) for visual inspection under the **Traces** tab. They will also be sent to Langfuse if configured in your `.env`.

## Project Documentation
Additional design documentation and reflections are available in the [docs/](./docs/) folder:
- [Decision Log](./docs/decision_log.md): Outlines architectural decisions, framework selections, and alternatives considered or rejected.
- [Reflection](./docs/reflection.md): Post-build reflection covering agent roles, connection debugging, security mitigations, and production readiness guidelines.
- [AI Usage Log](./docs/ai_usage_log.md): Documentation of AI interactions applied during development.
