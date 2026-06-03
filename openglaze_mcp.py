#!/usr/bin/env python3
"""OpenGlaze stdio MCP server."""

from __future__ import annotations

import json
import sys
from typing import Any

from core.chemistry.batch import calculate_batch
from core.chemistry.substitutions import suggest_substitutions
from core.chemistry.umf import calculate_umf
from openglaze_cli import _parse_cone, _project_brief

PROTOCOL_VERSION = "2024-11-05"


def analyze_glaze_recipe(args: dict[str, Any]) -> dict[str, Any]:
    recipe = str(args.get("recipe") or "").strip()
    if not recipe:
        raise ValueError("Provide recipe.")
    cone = _parse_cone(args.get("cone") or 10)
    return calculate_umf(recipe, cone=cone).to_dict()


def scale_glaze_batch(args: dict[str, Any]) -> dict[str, Any]:
    recipe = str(args.get("recipe") or "").strip()
    if not recipe:
        raise ValueError("Provide recipe.")
    size = float(args.get("size") or 0)
    if size <= 0:
        raise ValueError("Provide a positive size.")
    return calculate_batch(recipe, size, str(args.get("unit") or "grams"))


def suggest_material_substitutions(args: dict[str, Any]) -> dict[str, Any]:
    recipe = str(args.get("recipe") or "").strip()
    if not recipe:
        raise ValueError("Provide recipe.")
    return suggest_substitutions(recipe).to_dict()


TOOLS = {
    "openglaze_project_brief": {
        "description": "Return OpenGlaze project identity, surfaces, and safety guardrail.",
        "handler": lambda _args: _project_brief(),
        "inputSchema": {"type": "object", "properties": {}},
    },
    "analyze_glaze_recipe": {
        "description": "Calculate UMF, ratios, surface prediction, warnings, and CTE for a glaze recipe.",
        "handler": analyze_glaze_recipe,
        "inputSchema": {
            "type": "object",
            "properties": {
                "recipe": {"type": "string"},
                "cone": {
                    "type": ["integer", "string"],
                    "default": 10,
                    "description": "Firing cone. Use strings like '04' to preserve low-fire cone identity.",
                },
            },
            "required": ["recipe"],
        },
    },
    "scale_glaze_batch": {
        "description": "Scale a glaze recipe to a target batch size.",
        "handler": scale_glaze_batch,
        "inputSchema": {
            "type": "object",
            "properties": {
                "recipe": {"type": "string"},
                "size": {"type": "number"},
                "unit": {"type": "string", "default": "grams"},
            },
            "required": ["recipe", "size"],
        },
    },
    "suggest_material_substitutions": {
        "description": "Suggest substitutes for unknown or unavailable recipe materials.",
        "handler": suggest_material_substitutions,
        "inputSchema": {
            "type": "object",
            "properties": {"recipe": {"type": "string"}},
            "required": ["recipe"],
        },
    },
}


def handle_tool_call(
    name: str, arguments: dict[str, Any] | None = None
) -> dict[str, Any]:
    if name not in TOOLS:
        raise ValueError(f"Unknown tool: {name}")
    return TOOLS[name]["handler"](arguments or {})


def _tool_list() -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "description": spec["description"],
            "inputSchema": spec["inputSchema"],
        }
        for name, spec in TOOLS.items()
    ]


def _response(message_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": message_id, "result": result}


def _error(message_id: Any, code: int, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": message_id,
        "error": {"code": code, "message": message},
    }


def handle_message(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    message_id = message.get("id")
    params = message.get("params") or {}

    if message_id is None:
        return None
    if method == "initialize":
        return _response(
            message_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "openglaze", "version": "0.1.0"},
            },
        )
    if method == "tools/list":
        return _response(message_id, {"tools": _tool_list()})
    if method == "tools/call":
        try:
            result = handle_tool_call(
                params.get("name", ""), params.get("arguments") or {}
            )
            return _response(
                message_id,
                {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]},
            )
        except ValueError as exc:
            return _error(message_id, -32602, str(exc))
    return _error(message_id, -32601, f"Unsupported method: {method}")


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            reply = handle_message(json.loads(line))
        except json.JSONDecodeError as exc:
            reply = _error(None, -32700, f"Invalid JSON: {exc}")
        if reply is not None:
            sys.stdout.write(json.dumps(reply) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
