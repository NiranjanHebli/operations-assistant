# Decision Log

## 1. Why FastMCP over raw MCP SDK?
FastMCP offers a significantly more concise API, allowing tools to be written as standard Python functions with Pydantic typing handling the schema generation automatically. It removes boilerplate routing and serialization logic needed by the raw SDK.

## 2. Why Llama 3.1 8B for Researcher, Llama 3.3 70B for Writer (via Groq)?
Llama 3.1 8B on Groq is highly optimized for ultra-low latency inference and tool calling, making it ideal for the iterative loop the Researcher agent goes through. Llama 3.3 70B is more capable at complex reasoning and high-quality prose generation, which perfectly fits the Writer agent's role of synthesizing the gathered data into a clean report. The Groq API provides a fast, free-tier alternative that avoids OAuth/Vertex key restriction errors.

## 3. Why stdio transport over SSE?
Stdio transport is much simpler for a locally run tool where the MCP client (CrewAI in this case) and server reside on the same machine. It doesn't require allocating a network port or handling network related failures.

## 4. What did you try first that didn't work?
Initial testing with the raw strings in `search_documents` and `save_report` didn't have robust validation. Pydantic models were added to enforce min/max length and path traversal sanitization, preventing potential runtime issues and ensuring secure file writing.

## 5. What did you reject?
I rejected building custom Python scripts for reading the files in favor of using CrewAI. CrewAI provides out of the box MCP integration via `MCPServerAdapter` which handles standardizing tool execution and agent behavior much more natively than a bespoke pipeline.

## 6. Why externalize agent and task configurations to YAML?
Moving the prompt instructions, roles, backstories, and task descriptions out of the Python execution scripts (`crew/agents.py` and `crew/tasks.py`) into separate configuration files (`config/agents.yaml` and `config/tasks.yaml`) ensures a clean separation of concerns. This allows developers or prompt engineers to edit agent personas and task descriptions declaratively without touching executable Python code, making the system modular and scaling friendly.
