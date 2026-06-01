# Operations Assistant

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org)
[![Dependency Manager](https://img.shields.io/badge/dependency--manager-uv-purple.svg)](https://github.com/astral-sh/uv)
[![Framework](https://img.shields.io/badge/framework-CrewAI-red.svg)](https://github.com/crewAIInc/crewAI)
[![Protocol](https://img.shields.io/badge/protocol-MCP-orange.svg)](https://modelcontextprotocol.io)

## What It Does
This is a multi-agent AI system (CrewAI) integrated with a Model Context Protocol (MCP) server. The Assistant helps operations teams answer business questions automatically by querying local text documents and an inventory CSV without needing to manually look up files.

## Quick Start
1. Clone the repository

2. Install uv: `pip install uv`

3. Install dependencies: `uv sync`

4. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```
   Open .env and add your GROQ_API_KEY

5. Ask the Assistant a question:
   ```bash
   uv run python -m crew.crew "What is the return policy?"
   ```
   
6. View generated traces in the `traces/` folder and generated reports in the `outputs/` folder.


## Test the MCP Server Alone
You can inspect and test the MCP tools visually using the MCP Inspector:
```bash
npx @modelcontextprotocol/inspector uv run python server/mcp_server.py
```

## Run Tests
Run the automated test suite:
```bash
uv run pytest tests/ -v
```

## Project Documentation
Additional design documentation and reflections are available in the [docs/](./docs/) folder:
- [Decision Log](./docs/decision_log.md): Outlines architectural decisions, framework selections, and alternatives considered or rejected.
- [Reflection](./docs/reflection.md): Post-build reflection covering agent roles, connection debugging, security mitigations, and production readiness guidelines.