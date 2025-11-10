"""
MCP Server to read chat session logs from the user's workflow directory.

Features
- Reads configuration from config.json: port/http_port/mcp_port.
- Exposes an MCP tool over HTTP:
  - get_chat_session_history(session_id): reads ~/.workflow/chat_session_<id>.log and returns its content.

Run
    uv run python history-mcp-server.py
"""

from __future__ import annotations

import json
import os
import re
from typing import Optional

try:
    from fastmcp import FastMCP  # type: ignore
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "fastmcp is required to run this server. Install with `uv add fastmcp`."
    ) from e


# ------------------------- Configuration -------------------------------------

_CFG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def _load_cfg() -> dict:
    try:
        if os.path.isfile(_CFG_PATH):
            with open(_CFG_PATH, "r", encoding="utf-8") as fh:
                return json.load(fh) or {}
    except Exception:
        pass
    return {}


_CFG = _load_cfg()


def _cfg_port(cfg: dict) -> int:
    for key in ("port", "http_port", "mcp_port"):
        if key in cfg:
            try:
                return int(cfg[key])
            except Exception:
                continue
    return 8012


_MCP_PORT = _cfg_port(_CFG)


# --------------------------- Helpers -----------------------------------------

def _workflow_home_dir() -> str:
    home = os.path.expanduser("~")
    return os.path.join(home, ".workflow")


def _normalize_session_id(session_id: str) -> str:
    # Replace any unsafe characters with underscore to avoid path traversal
    # Allow only alphanumerics, dash and underscore
    return re.sub(r"[^A-Za-z0-9_-]", "_", session_id or "")


def _session_log_path(session_id: str) -> str:
    normalized = _normalize_session_id(session_id)
    return os.path.join(_workflow_home_dir(), f"chat_session_{normalized}.log")


# --------------------------- MCP Tools ---------------------------------------

mcp = FastMCP("workflow-history-mcp")


@mcp.tool(
    name="get_chat_session_history",
    description=(
        "Return the chat history for a given session id from "
        "~/.workflow/chat_session_<id>.log."
    ),
)
def get_chat_session_history(session_id: str) -> dict:  # type: ignore[override]
    if not session_id:
        return {"ok": False, "error": "session_id is required"}

    wf_dir = _workflow_home_dir()
    if not os.path.isdir(wf_dir):
        return {"ok": False, "error": f"workflow directory not found: {wf_dir}"}

    path = _session_log_path(session_id)
    if not os.path.isfile(path):
        return {"ok": False, "error": f"session log not found: {path}", "path": path}

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read()
    except Exception as e:
        return {"ok": False, "error": f"failed to read file: {e}", "path": path}

    return {
        "ok": True,
        "path": path,
        "length": len(content),
        "content": content,
    }


if __name__ == "__main__":
    print(f"[MCP] Starting on http://127.0.0.1:{_MCP_PORT}")
    # FastMCP HTTP transport entrypoint
    mcp.run(transport="http", host="127.0.0.1", port=_MCP_PORT)

