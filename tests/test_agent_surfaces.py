"""Tests for OpenGlaze CLI, MCP, and public skill surfaces."""

from pathlib import Path

from core.chemistry.umf import get_limit_formulas
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


def test_agent_surfaces_preserve_low_fire_cone_values():
    result = handle_tool_call(
        "analyze_glaze_recipe",
        {"recipe": "Ferro Frit 3124 40, Silica 20, EPK 20, Whiting 20", "cone": "04"},
    )

    assert result["cone"] == "04"
    assert get_limit_formulas("04") != get_limit_formulas(4)
