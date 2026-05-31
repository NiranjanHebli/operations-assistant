# Reflection

## Why these tools and agent roles?
I decided to split the work between a Researcher and a Writer because it felt like the most natural way to handle a standard RAG (Retrieval-Augmented Generation) workflow. The Researcher gets to do the messy, iterative work of digging through text files and filtering CSV records. Once that's done, the Writer takes over to focus purely on formatting and presenting that knowledge clearly. 

The tools themselves (`search_documents`, `read_record`, `save_report`) were built to give each agent strict, bounded capabilities so they don't step on each other's toes. I also made sure to pull all the agent instructions, backstories, and task descriptions out into YAML files under `config/`. This keeps the actual Python code a lot cleaner and separates the "prompt engineering" from the hard logic.

## What broke first when you connected the crew to the server?
The very first thing that tripped me up was getting the Pydantic schemas to play nicely with the MCP tools. FastMCP tries to automatically infer inputs, and it took some tweaking to get the types to align perfectly. I also ran into an issue where the crew agent would occasionally hallucinate arguments—like passing an empty query or a completely invalid ID. I had to tighten up the prompt instructions and set strict `max_iter` limits to stop the agents from getting stuck in endless retry loops when they got confused.

## Show one wrong or ungrounded answer. Did your guardrail catch it?
During a live run, the Researcher agent hallucinated two random record IDs to query, calling `read_record(record_id=12345)` and `read_record(record_id=67890)`. 

Our guardrails caught this at two levels:
1. **Pydantic Validation:** The MCP tool's `RecordInput` schema has a strict rule (`le=9999`), so the tool immediately rejected the request with a clear `validation error for RecordInput`. 
2. **System Prompt Guardrail:** Because the prompt explicitly instructed the agent to "state explicitly" if nothing useful is found and "do NOT guess," the agent correctly digested the validation error. In its final output, instead of making up a fake record, it accurately reported: *"No records found matching record IDs 12345 and 67890."*

## Where is the biggest security risk in your server?
Without a doubt, it's the `save_report` tool. Since it actively writes files to the disk, a hallucinating (or malicious) model could easily attempt a path traversal attack—something like passing `title="../../../etc/passwd"`. To lock this down, I added a strict regular expression to sanitize the filename and hardcoded the logic so it can *only* write files into the `./outputs/` directory.

## What would you change before touching real company data?
If I were deploying this to a real production environment, I'd definitely add a few safeguards:
1. **Authentication:** I'd lock down the MCP server so only permitted, authenticated clients could even connect to it.
2. **Read-Only Policies:** I'd enforce strict read-only database permissions for the data-fetching tools.
3. **Human-in-the-loop (HITL):** I would absolutely require a human to approve the final draft before any data is actually written to disk via `save_report`.
4. **Rate Limiting:** I'd add rate limits to make sure a runaway agent loop couldn't accidentally DDOS external APIs or thrash the local file system.
