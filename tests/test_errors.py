"""Tests for the agent-facing retry pattern (core/errors.py + surfaces).

kinocut-equivalent contract: every error an agent can hit — MCP tool call,
CLI invocation, or HTTP request — carries a concrete re-invocation, not a
dead-end message.
"""

import json

import pytest

from core.errors import (
    _RETRY_INVOCATIONS,
    error_payload,
    retry_invocation,
    retry_message,
)
from openglaze_cli import main as cli_main
from openglaze_mcp import analyze_glaze_recipe, handle_message

# --- core/errors.py ---------------------------------------------------------


def test_every_error_code_maps_to_a_concrete_invocation():
    for code, invocation in _RETRY_INVOCATIONS.items():
        assert "retry" not in code
        assert any(marker in invocation for marker in ("MCP", "CLI", "HTTP")), code


def test_retry_message_appends_invocation():
    msg = retry_message("Provide recipe.", "missing_recipe")
    assert msg.startswith("Provide recipe.")
    assert "; retry with " in msg
    assert "analyze_glaze_recipe" in msg


def test_retry_invocation_falls_back_to_generic_hint():
    assert "corrected parameters" in retry_invocation("never_defined_code")


def test_error_payload_shape():
    payload = error_payload("Glaze not found", "glaze_not_found")
    assert set(payload) == {"error", "code", "retry"}
    assert payload["code"] == "glaze_not_found"
    assert payload["retry"] == retry_invocation("glaze_not_found")
    assert payload["retry"] in payload["error"]


# --- MCP surface ------------------------------------------------------------


def test_mcp_validation_error_carries_retry_hint():
    with pytest.raises(ValueError) as exc:
        analyze_glaze_recipe({})
    assert "retry with" in str(exc.value)


def test_mcp_invalid_params_lane_returns_retry_hint():
    resp = handle_message(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "analyze_glaze_recipe", "arguments": {"recipe": ""}},
        }
    )
    assert resp["error"]["code"] == -32602
    assert "retry with" in resp["error"]["message"]


def test_mcp_chemistry_error_result_carries_retry_key():
    result = analyze_glaze_recipe({"recipe": "Custer Feldspar"})
    assert result["error"]
    assert "analyze_glaze_recipe" in result["retry"]


# --- CLI surface ------------------------------------------------------------


def _run_cli(capsys, *argv):
    with pytest.raises(SystemExit) as exc:
        cli_main(list(argv))
    captured = capsys.readouterr()
    return exc.value.code, captured.out, captured.err


def test_cli_invalid_cone_exits_with_retry_hint(capsys):
    code, out, err = _run_cli(capsys, "umf", "--recipe", "Silica 100", "--cone", "1a")
    assert code == 2
    assert "retry with" in err
    assert "openglaze_cli umf" in err


def test_cli_unparseable_recipe_exits_with_retry_hint(capsys):
    code, out, err = _run_cli(capsys, "umf", "--recipe", "Custer Feldspar")
    assert code == 2
    assert json.loads(out)["error"]  # payload still printed as JSON
    assert "retry with" in err


def test_cli_valid_recipe_exits_zero(capsys):
    cli_main(["umf", "--recipe", "Custer Feldspar 45, Silica 25, Whiting 18, EPK 12"])
    captured = capsys.readouterr()
    assert json.loads(captured.out)["ratios"]
    assert captured.err == ""


# --- HTTP surface -----------------------------------------------------------


def test_http_404_body_carries_retry_fields(test_db_path):
    from server import create_app

    app = create_app(
        {
            "mode": type("M", (), {"security": None, "AUTH_ENABLED": False})(),
            "database": {"path": str(test_db_path)},
        }
    )
    client = app.test_client()
    resp = client.get("/api/glazes/does-not-exist/umf")
    body = resp.get_json()
    assert resp.status_code == 404
    assert body["code"] == "glaze_not_found"
    assert "GET /api/glazes" in body["retry"]

    resp = client.get("/api/no-such-route")
    body = resp.get_json()
    assert resp.status_code == 404
    assert body["code"] == "not_found"
    assert "retry" in body
