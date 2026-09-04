"""Utility for loading and validating LLM tool (function-calling) definitions from JSON.

Usage
-----
    from tool_loader import get_tools, get_tool

    tools = get_tools()                              # dict[name] -> ToolDefinition
    record_user_details_json = get_tool("record_user_details").model_dump()

    # OpenAI-style tools= payload:
    openai_tools = [
        {"type": "function", "function": t.model_dump()} for t in tools.values()
    ]
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

TOOLS_PATH = Path(__file__).parent / "tools.json"


class ToolParameters(BaseModel):
    """JSON-schema-style parameters block for a single tool."""

    model_config = ConfigDict(extra="allow")

    type: str
    properties: dict[str, Any]
    required: list[str] = []
    additionalProperties: bool = False


class ToolDefinition(BaseModel):
    """A single tool/function definition."""

    name: str
    description: str
    parameters: ToolParameters


def _load_raw(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"Tool definitions file not found: {path}") from None

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Malformed JSON in {path} at line {e.lineno}, col {e.colno}: {e.msg}"
        ) from e


@lru_cache(maxsize=1)
def get_tools(path: Path = TOOLS_PATH) -> dict[str, ToolDefinition]:
    """Load, validate, and cache all tool definitions from the JSON file.

    Raises FileNotFoundError, ValueError (bad JSON), or pydantic ValidationError
    (schema doesn't match ToolDefinition) — all with a message pointing at the
    exact tool/field that's broken, instead of failing later inside an API call.
    """
    raw = _load_raw(path)

    tools: dict[str, ToolDefinition] = {}
    for key, value in raw.items():
        try:
            tools[key] = ToolDefinition(**value)
        except ValidationError as e:
            raise ValueError(f"Invalid tool definition for '{key}' in {path}:\n{e}") from e

    return tools


def get_tool(name: str) -> ToolDefinition:
    """Fetch a single tool definition by name."""
    tools = get_tools()
    try:
        return tools[name]
    except KeyError:
        available = ", ".join(sorted(tools)) or "none"
        raise KeyError(f"Unknown tool '{name}'. Available tools: {available}") from None


def as_openai_tools() -> list[dict[str, Any]]:
    """Convenience: return all tools formatted for the OpenAI `tools=` parameter."""
    return [{"type": "function", "function": t.model_dump()} for t in get_tools().values()]
