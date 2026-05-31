# Operations Assistant

## What It Does
This is a multi-agent AI system (CrewAI) integrated with a Model Context Protocol (MCP) server. The Assistant helps operations teams answer business questions automatically by querying local text documents and an inventory CSV without needing to manually look up files.

## Quick Start
1. Clone the repository
2. Install uv: `pip install uv`
3. Install dependencies: `uv sync`
4. Test the MCP Server alone using the MCP Inspector (see instructions below)


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