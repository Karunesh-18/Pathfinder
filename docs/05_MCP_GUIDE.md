# MCP Guide — Model Context Protocol (optional layer)

Mainly relevant to the AI dev; useful background for backend too if you decide to use it.

## Do you actually need this for the hackathon?

Probably not for the MVP. MCP (Model Context Protocol) is a standard way to expose tools/data sources to an LLM so it can call them consistently across different apps — it matters most when you want your agent's tools to be reusable outside your own codebase, or when you're plugging into external MCP servers someone else built (e.g. a connector for a calendar, a docs source).

For this project, your AI service's functions (`recommend`, `generate_path`, `analyze_feedback`, etc.) are called directly by your own backend — a plain Python function call or internal REST call is simpler and has less surface area to debug than standing up an MCP server for it. **Don't add MCP just because it's a buzzword for the judges** — "Innovation & Creativity" is better served by the active-questioning/replanning logic than by a protocol choice.

## Where MCP is genuinely worth it here

1. **If you want the mentor chat to call live tools during conversation** — e.g. "search my resource catalog," "check my current skill gaps" — as callable tools *during* an LLM conversation turn, rather than your backend pre-fetching everything. MCP (or plain LLM tool-calling, which doesn't require MCP at all) is the right shape for that.
2. **If you want to plug into an external MCP server** someone else already built — e.g. a web-search or docs connector — instead of writing your own integration.
3. **If a judge/evaluator explicitly rewards "agentic tool use"** in the criteria — worth checking the judging rubric again before investing time here.

If none of these apply, skip this doc entirely and keep the AI service as plain internal functions per `03_AI.md`.

## Minimal MCP server skeleton (if you do use it)

Expose one or two of your AI service's read-only functions as MCP tools — `search_resources` and `get_skill_gaps` are good candidates since they're safe to call mid-conversation without side effects.

```python
# mcp_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("learning-agent-tools")

@mcp.tool()
def search_resources(query: str, skill: str | None = None) -> list[dict]:
    """Search the curated resource catalog by free-text query and optional skill filter."""
    # call into the same resource-lookup logic ai_service.py already has
    ...

@mcp.tool()
def get_skill_gaps(user_id: str) -> list[dict]:
    """Return the learner's current prioritized skill gaps."""
    # call skill_gap_engine.compute_gaps(profile)
    ...

if __name__ == "__main__":
    mcp.run()
```

Check the current MCP Python SDK docs before building against this skeleton — the SDK's exact API surface changes between versions, and this is meant as a shape reference, not a copy-paste-ready file.

## Keep side-effecting actions (write progress, regenerate path) out of MCP tools for now

Tools an LLM can call mid-conversation should be read-only for safety and predictability during a live demo — a bug that causes the model to call `generate_path()` unexpectedly mid-chat is exactly the kind of thing that goes wrong on stage. Keep mutations (`/api/progress`, `/api/path` POST) behind explicit backend endpoints the frontend calls after user confirmation, not behind agent tool-calls.

## If you skip MCP entirely

That's a completely reasonable call for a 5-day build. Note in the solution doc that the AI service's tool interface (§ "Internal interface" in `03_AI.md`) is structured so it *could* be exposed via MCP later without a rewrite — that's a legitimate "designed for extensibility" line without having built it.
