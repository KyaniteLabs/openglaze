"""Tests for OpenGlaze CLI, MCP, and public skill surfaces."""

from pathlib import Path

from openglaze_mcp import handle_message, handle_tool_call

ROOT = Path(__file__).resolve().parents[1]


def test_mcp_analyzes_glaze_recipe():
    result = handle_tool_call(
        "analyze_glaze_recipe",
        {"recipe": "Custer Feldspar 45, Silica 25, Whiting 18, EPK 12", "cone": 10},
    )

    assert result["success"] is True
    assert result["thermal_expansion"] is not None


def test_mcp_lists_tools():
    response = handle_message({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})

    assert response is not None
    assert any(
        tool["name"] == "scale_glaze_batch" for tool in response["result"]["tools"]
    )


def test_public_skill_exists():
    skill = ROOT / "skills" / "openglaze" / "SKILL.md"

    assert skill.exists()
    assert "python -m openglaze_mcp" in skill.read_text()
