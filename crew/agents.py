from crewai import Agent
from .llm_config import llama_instant, llama_versatile
from mcp import StdioServerParameters
import yaml
from pathlib import Path
import sys
import os

SERVER_PARAMS = StdioServerParameters(
    command="uv",
    args=["run", "python", "server/mcp_server.py"],
)


def get_agents_config():
    config_path = Path(__file__).parent.parent / "config" / "agents.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_agents(mcp_tools: list) -> tuple[Agent, Agent]:
    config = get_agents_config()

    researcher = Agent(
        config=config["researcher"],
        tools=mcp_tools,
        llm=llama_instant,
        max_iter=5,  # prevent infinite loops
        verbose=True,
    )

    writer = Agent(
        config=config["writer"],
        tools=mcp_tools,  # writer can also call save_report
        llm=llama_versatile,
        max_iter=3,
        verbose=True,
    )

    return researcher, writer
