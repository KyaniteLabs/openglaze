"""Follow-through tests: the retry invocations actually run.

Security round-1 contract: a retry hint is only valid if executing it
succeeds. These tests extract the CLI command / HTTP body / MCP arguments
from the emitted retry strings and execute them for real — no
surface-name substring checks.
"""

import json
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

from core.errors import retry_invocation
from openglaze_mcp import handle_tool_call

REPO_ROOT = Path(__file__).resolve().parents[1]

_CLI_CMD = re.compile(r"python -m openglaze_cli .*?(?= \(CLI\))")
_POST_HINT = re.compile(r"POST (/\S+) with (\{[^}]*\})")
_MCP_RECIPE = re.compile(r'recipe="([^"]+)"')

# Codes whose hint carries a runnable CLI command and a runnable HTTP body.
CLI_CODES = (
    "missing_recipe",
    "invalid_cone",
    "invalid_size",
    "missing_batch_size",
    "unparseable_recipe",
)
HTTP_POST_CODES = (
    "missing_recipe",
    "invalid_size",
    "missing_batch_size",
    "invalid_target",
    "missing_target_value",
)


def _extract_cli(invocation: str) -> list[str]:
    match = _CLI_CMD.search(invocation)
    assert match, f"no CLI command in: {invocation}"
    return shlex.split(match.group(0))[3:]  # drop "python -m openglaze_cli"


def _extract_post(invocation: str) -> tuple[str, dict]:
    match = _POST_HINT.search(invocation)
    assert match, f"no POST hint in: {invocation}"
    path, raw = match.groups()
    return path, json.loads(raw.replace("'", '"'))


def _make_client(test_db_path):
    from server import create_app

    app = create_app(
        {
            "mode": type("M", (), {"security": None, "AUTH_ENABLED": False})(),
            "database": {"path": str(test_db_path)},
        }
    )
    return app.test_client()


# --- CLI: run the hinted command, expect exit 0 -----------------------------


def test_cli_retry_commands_run_end_to_end():
    for code in CLI_CODES:
        argv = _extract_cli(retry_invocation(code))
        proc = subprocess.run(
            [sys.executable, "-m", "openglaze_cli", *argv],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert proc.returncode == 0, (code, proc.stderr)
        assert json.loads(proc.stdout), code  # a real payload came back


# --- HTTP: post the hinted body, expect the route to accept it -------------


def test_http_retry_bodies_are_accepted_by_their_routes(test_db_path):
    client = _make_client(test_db_path)
    for code in HTTP_POST_CODES:
        path, body = _extract_post(retry_invocation(code))
        resp = client.post(path, json=body)
        assert resp.status_code == 200, (code, resp.status_code, resp.get_json())


def test_http_error_retry_preserves_caller_arguments(test_db_path):
    """A 400 must hint this caller's own recipe plus the missing field."""
    client = _make_client(test_db_path)
    recipe = "Silica 40, Whiting 20, EPK 20, Custer Feldspar 20"
    resp = client.post(
        "/api/chemistry/optimize", json={"recipe": recipe, "target": "target_cte"}
    )
    assert resp.status_code == 400
    assert resp.get_json()["code"] == "missing_target_value"
    path, body = _extract_post(resp.get_json()["retry"])
    assert body["recipe"] == recipe  # the caller's recipe survived
    follow = client.post(path, json=body)
    assert follow.status_code == 200, follow.get_json()


# --- MCP: call the hinted tool with the hinted arguments -------------------


def test_mcp_retry_hints_run_end_to_end():
    recipe = _MCP_RECIPE.search(retry_invocation("missing_recipe")).group(1)
    result = handle_tool_call("analyze_glaze_recipe", {"recipe": recipe})
    assert not result.get("error")

    result = handle_tool_call("scale_glaze_batch", {"recipe": recipe, "size": 300})
    assert not result.get("error")


def test_mcp_error_hints_preserve_caller_recipe():
    from openglaze_mcp import scale_glaze_batch

    try:
        scale_glaze_batch({"recipe": "Silica 40, Whiting 20", "size": "abc"})
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "Silica 40, Whiting 20" in str(exc)  # recipe echoed
        assert "size=300" in str(exc)


# --- Rate limit: the denial carries the measured window, and the
#     hinted same-request retry succeeds once the window passes -------------


class _Clock:
    """Controllable stand-in for the time module inside core.security."""

    def __init__(self, real):
        self._real = real
        self.offset = 0.0

    def time(self):
        return self._real.time() + self.offset

    def __getattr__(self, name):
        return getattr(self._real, name)


def test_rate_limit_denial_is_measured_and_retry_follows_through(
    test_db_path, monkeypatch
):
    from core import security
    from server import create_app

    limiter = security.InMemoryRateLimiter(
        requests_per_minute=2, block_duration_minutes=1
    )
    monkeypatch.setattr(security, "_rate_limiter", limiter)
    clock = _Clock(time)
    monkeypatch.setattr(security, "time", clock)

    app = create_app(
        {
            "mode": type("M", (), {"security": None, "AUTH_ENABLED": False})(),
            "database": {"path": str(test_db_path)},
        }
    )
    client = app.test_client()

    assert client.get("/api/glazes").status_code == 200
    assert client.get("/api/glazes").status_code == 200

    denied = client.get("/api/glazes")
    assert denied.status_code == 429
    body = denied.get_json()
    measured = int(denied.headers["Retry-After"])
    assert measured == 60  # 1-minute block, not a substituted constant
    assert body["code"] == "RATE_LIMITED"
    assert body["retry_after"] == measured
    assert "GET /api/glazes" in body["retry"]
    assert str(measured) in body["retry"]
    assert "same arguments" in body["retry"]

    # Follow-through: after the measured window, the same request succeeds.
    clock.offset += measured + 1
    assert client.get("/api/glazes").status_code == 200
