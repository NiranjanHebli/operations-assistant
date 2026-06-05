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

## Demo & Pitch Videos

### Pitch Presentation (Idea, Pain Points & Solution)
This video walks through the business pain points of manual operations research, the core concept behind the Operations Assistant, our multi-agent solution, and target use cases.

[![Watch the video](https://cdn.loom.com/sessions/thumbnails/36be91ddba8e41c184f246e3d31eb264-2e248f0756f81a36.gif)](https://www.loom.com/share/36be91ddba8e41c184f246e3d31eb264)

### Live System Demo (Technical Walkthrough)
This video demonstrates the working system end-to-end, showing the multi-agent execution, tools usage via MCP, human-in-the-loop validation, and generated outputs.

[![Watch the video](https://cdn.loom.com/sessions/thumbnails/e008d887287b4cb5a7595cfb49b5570f-3506973381462012.gif)](https://www.loom.com/share/e008d887287b4cb5a7595cfb49b5570f)

## Use Cases
The Operations Assistant is designed to address key operational challenges across various business workflows:
- **Internal Knowledge Retrieval & Support**: Automatically querying local standard operating procedures (SOPs), return policies, compliance documents, and support tickets in `data/documents/` to instantly answer team queries.
- **Inventory Check & Verification**: Reading and analyzing structured data records (e.g., querying product lines in `data/inventory.csv` using the `read_record` tool) to verify stock levels, product specifications, and pricing.
- **Outbound Web Research & Market Intelligence**: Utilizing the Stdio Fetch Server to parse external HTML pages, allowing operations teams to pull current competitor pricing, shipping options, or external vendor terms.
- **Fact-Checked Operations Reports**: Generating structured reports (saved to the `outputs/` folder) with automated fact-checking and Human-in-the-Loop approval to prevent hallucinations in operational decisions.

### Use Case Diagram
![Standard Use Case Diagram](./assets/standard_use_case.png)

## Quick Start

### Automated Setup
The easiest way to initialize the project is by running the `setup.sh` shell script:
```bash
./setup.sh
```
This script automates the environment setup by performing the following tasks:
- **Verifies python environment**: Checks if `pip` is installed on your machine.
- **Installs package manager**: Installs the `uv` dependency manager (`pip install uv`) if not already present.
- **Installs dependencies**: Runs `uv sync` to set up a virtual environment and install all project dependencies.
- **Configures environment variables**: Safely checks if a `.env` file exists; if not, it copies `.env.example` to `.env` (or creates a blank one).

After running, open the newly created `.env` file and add your `GROQ_API_KEY`.

### Manual Setup
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
        Fetch["Fetch Server (Stdio)"]
        Core["Core Operations Server (SSE: localhost:8000)"]
        class Core,Fetch yellowL3;
    end
    class MCPServers mainSubgraph;

    subgraph FetchTools["Fetch Tools (Stdio)"]
        fetch_url["fetch_url - Reads Web HTML"]
        class fetch_url greenL4;
    end
    class FetchTools mainSubgraph;

    subgraph CoreTools["Core Tools (SSE)"]
        search_documents["search_documents - Reads data/documents/"]
        read_record["read_record - Reads inventory.csv"]
        save_report["save_report - Writes to outputs/"]
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

### Agent Workflow Sequence

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'background': 'transparent',
    'primaryColor': '#06B6D4',
    'primaryTextColor': '#000000',
    'primaryBorderColor': '#0891B2',
    'lineColor': '#94A3B8',
    'signalColor': '#38BDF8',
    'signalTextColor': '#FFFFFF',
    'noteBkgColor': '#8B5CF6',
    'noteTextColor': '#FFFFFF',
    'noteBorderColor': '#7C3AED',
    'actorBkg': '#F59E0B',
    'actorTextColor': '#000000',
    'actorBorder': '#D97706',
    'activationBkgColor': '#1E293B',
    'activationBorderColor': '#06B6D4'
  }
}}%%
sequenceDiagram
    autonumber
    actor User
    participant Crew as CrewAI Core
    participant OR as Operations Researcher
    participant RW as Report Writer
    participant FC as Fact Checker
    participant MCP as MCP Tools (Fetch/SSE)

    User->>Crew: Submits business question

    Note over Crew,OR: Step 1: Research Phase
    Crew->>OR: Assigns Research Task
    activate OR
    OR->>MCP: fetch_url (External Data)
    OR->>MCP: search_documents (Local SOPs)
    OR->>MCP: read_record (Inventory CSV)
    MCP-->>OR: Returns retrieved context & data
    OR-->>Crew: Returns Raw Research Findings
    deactivate OR

    Note over Crew,RW: Step 2: Synthesis Phase
    Crew->>RW: Assigns Report Writing Task (with Research)
    activate RW
    RW->>RW: Synthesizes findings into Markdown
    RW-->>Crew: Returns Draft Operations Report
    deactivate RW

    Note over Crew,FC: Step 3: Verification & Output
    Crew->>FC: Assigns Fact Checking Task (with Draft & Research)
    activate FC
    FC->>FC: Cross-references claims against evidence
    FC-->>User: Prompts for Human Approval (HITL)

    alt User Approves
        User-->>FC: Approves Draft ("y" or Enter)
        FC->>MCP: save_report (Writes to outputs/)
        MCP-->>FC: Confirms Save
        FC-->>Crew: Returns Final Result
    else User Rejects / Edits
        User-->>FC: Provides feedback/corrections
        FC->>FC: Adjusts report based on feedback
        FC->>MCP: save_report (Writes to outputs/)
        FC-->>Crew: Returns Corrected Result
    end
    deactivate FC

    Crew-->>User: Returns Final System Output
```

## Sample Data
The repository includes a set of sample data used by the MCP servers to answer operations questions:
- `data/documents/`: A folder containing small text files (e.g., policies, tickets). The `search_documents` tool searches through these files.
- `data/inventory.csv`: A CSV file containing mock product inventory records. The `read_record` tool queries specific records from this file by their ID.

## Test the MCP Servers Alone
You can inspect and test the MCP tools visually using the MCP Inspector.

**Operations Server (SSE mode):**
Start the server first, then connect the inspector to it:
```bash
# Terminal 1 — start SSE server
uv run python server/mcp_server.py

# Terminal 2 — connect inspector
npx @modelcontextprotocol/inspector --transport sse --server-url http://127.0.0.1:8000/sse
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

### Langfuse Tracing Dashboard
![Langfuse Dashboard](./assets/langfuse_dashboard.png)

### Aspire Structured Logs
![Aspire Dashboard](./assets/aspire_dashboard.png)

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

## Future Scope
The following features are planned for future releases to enhance scalability, usability, and integration:
- **Interactive User Dashboard**: Building a sleek web UI (using React/Vite) to move away from terminal commands, allowing operations teams to interact with agents, edit drafts, and view logs dynamically.
- **Enterprise Chat Integration**: Packaging the assistant as a Slack or Microsoft Teams bot to enable team-wide collaboration directly from existing chat channels.
- **Production Database Connections**: Migrating MCP server data tools to query production relational databases (PostgreSQL, MySQL) and enterprise ERP systems (SAP, Salesforce).
- **Multi-Modal Document Parsing**: Upgrading reasoning agents to handle invoices, charts, and scanned PDFs using multi-modal LLMs.

## Project Documentation
Additional design documentation and reflections are available in the [docs/](./docs/) folder:

- [Business Case Study](./docs/business_case_study.md): Details the losses teams previously faced, how the Operations Assistant mitigates them, and calculations projecting annual savings in Lakh rupees.
- [Decision Log](./docs/decision_log.md): Outlines architectural decisions, framework selections, and alternatives considered or rejected.
- [Reflection](./docs/reflection.md): Post-build reflection covering agent roles, connection debugging, security mitigations, and production readiness guidelines.
- [AI Usage Log](./docs/ai_usage_log.md): Documentation of AI interactions applied during development.
- [Data & Examples](./docs/data_and_examples.md): Sample data and example questions with saved outputs.
