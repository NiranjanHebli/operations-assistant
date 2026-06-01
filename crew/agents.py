from crewai import Agent
from .llm_config import llama_instant, llama_versatile
from mcp import StdioServerParameters
import yaml
from pathlib import Path
import sys
import os

SERVER_PARAMS = StdioServerParameters(
    command=sys.executable,
    args=["server/mcp_server.py"],
)

FETCH_SERVER_PARAMS = StdioServerParameters(
    command=sys.executable,
    args=["server/mcp_fetch_server.py"],
)


def get_agents_config():
    config_path = Path(__file__).parent.parent / "config" / "agents.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_agents(mcp_tools: list, fetch_tools: list) -> tuple[Agent, Agent]:
    config = get_agents_config()

    # Operations Researcher gets search & read tools from the main server PLUS the fetch tool
    researcher_tools = [t for t in mcp_tools if t.name != "save_report"] + fetch_tools

    # Report Writer ONLY gets the save_report tool
    writer_tools = [t for t in mcp_tools if t.name == "save_report"]

    researcher = Agent(
        config=config["researcher"],
        tools=researcher_tools,
        llm=llama_instant,
        max_iter=5,  # prevent infinite loops
        verbose=True,
    )

    writer = Agent(
        config=config["writer"],
        tools=writer_tools,
        llm=llama_versatile,
        max_iter=3,
        verbose=True,
    )

    return researcher, writer
