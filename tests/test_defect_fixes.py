"""Regression tests for the six tool-surface defects fixed on card t_d98f89bf.

D1 empty-id glaze create, D2 /api/ask 500→503 with AI down, D3 CLI exit codes,
D4 substitutions materials param, D5 personal-mode 401s, D6 JSON 415 errors.
"""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]

RECIPE = "Custer Feldspar 45, Silica 25, Whiting 18, EPK 12"
DEAD_AI = "http://127.0.0.1:9/v1"  # nothing listens on port 9


@pytest.fixture
def app(test_db_path):
    with patch.dict(
        "os.environ",
        {
            "DATABASE_PATH": test_db_path,
            "AI_PROVIDER": "lmstudio",
            "LM_STUDIO_URL": DEAD_AI,
            "LM_STUDIO_MODEL": "test-model",
        },
    ):
        from server import create_app

        return create_app(
            {
                "mode": "personal",
                "database": {"path": test_db_path},
            }
        )


@pytest.fixture
def client(app):
    # The rate limiter is a process-global singleton bucketed by client IP and
    # shared with every other test file; give these tests their own bucket via
    # a trusted-proxy X-Forwarded-For identifier so the suite order stays stable.
    with patch.dict("os.environ", {"TRUSTED_PROXY": "127.0.0.1"}):
        test_client = app.test_client()
        test_client.environ_base["HTTP_X_FORWARDED_FOR"] = "10.42.0.99"
        yield test_client


def _post_json(client, path, payload, **kwargs):
    return client.post(
        path, data=json.dumps(payload), content_type="application/json", **kwargs
    )


class TestD1GlazeCreateId:
    def test_create_without_id_generates_slug(self, client):
        resp = _post_json(client, "/api/glazes", {"name": "Probe Gloss"})
        assert resp.status_code == 201
        glaze_id = json.loads(resp.data)["id"]
        assert isinstance(glaze_id, str) and glaze_id.strip()
        assert glaze_id == "probe-gloss"

    def test_no_empty_id_rows_persisted(self, client):
        _post_json(client, "/api/glazes", {"name": "x"})
        listing = json.loads(client.get("/api/glazes").data)
        assert all(isinstance(g.get("id"), str) and g["id"].strip() for g in listing)

    def test_generated_ids_are_slugged_and_unique(self, client):
        first = json.loads(
            _post_json(client, "/api/glazes", {"name": "Leach 4/3/2"}).data
        )
        second = json.loads(
            _post_json(client, "/api/glazes", {"name": "Leach 4/3/2"}).data
        )
        assert first["id"] == "leach-4-3-2"
        assert second["id"] == "leach-4-3-2-2"

    def test_explicit_id_is_preserved(self, client):
        resp = _post_json(client, "/api/glazes", {"id": "my-custom-id", "name": "Kept"})
        assert resp.status_code == 201
        assert json.loads(resp.data)["id"] == "my-custom-id"

    def test_whitespace_only_id_is_replaced(self, client):
        resp = _post_json(client, "/api/glazes", {"id": "   ", "name": "Blank"})
        assert resp.status_code == 201
        glaze_id = json.loads(resp.data)["id"]
        assert glaze_id.strip()


class TestD2AskUnavailable:
    def test_ask_returns_designed_503_when_ai_down(self, client):
        resp = _post_json(client, "/api/ask", {"question": "hi"})
        assert resp.status_code == 503
        data = json.loads(resp.data)
        assert data["ai_available"] is False

    def test_ask_stream_error_event_marks_ai_unavailable(self, client):
        resp = _post_json(client, "/api/ask/stream", {"question": "hi"})
        assert resp.status_code == 200
        assert resp.content_type.startswith("text/event-stream")
        body = resp.get_data(as_text=True)
        assert '"ai_available": false' in body


class TestD3CliExitCodes:
    def _run(self, *argv):
        return subprocess.run(
            [sys.executable, "-m", "openglaze_cli", *argv],
            capture_output=True,
            text=True,
            cwd=ROOT,
            timeout=120,
        )

    @pytest.mark.parametrize(
        "argv",
        [
            ("umf", "--recipe", "garbage recipe", "--cone", "6"),
            ("batch", "--recipe", "garbage recipe", "--size", "100"),
            ("substitutions", "--recipe", "garbage recipe"),
        ],
    )
    def test_failure_exits_nonzero_and_still_prints_json(self, argv):
        # Exit 2 with a retry hint on stderr is the CLI's error contract
        # (tests/test_errors.py); the JSON payload is still printed.
        proc = self._run(*argv)
        assert proc.returncode == 2
        assert "retry with" in proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["success"] is False

    def test_success_exits_0(self):
        proc = self._run("umf", "--recipe", RECIPE, "--cone", "6")
        assert proc.returncode == 0
        assert json.loads(proc.stdout)["success"] is True


class TestD4MaterialSubstitutions:
    def test_known_material_suggestions_via_param(self):
        from core.chemistry.substitutions import suggest_substitutions

        result = suggest_substitutions(RECIPE, materials=["Custer Feldspar"])
        assert result.success is True
        originals = [s.original.lower() for s in result.suggestions]
        assert "custer feldspar" in originals

    def test_recipe_only_call_is_unchanged(self):
        from core.chemistry.substitutions import suggest_substitutions

        result = suggest_substitutions(RECIPE)
        assert result.success is True
        assert not any(
            s.original.lower() == "custer feldspar" for s in result.suggestions
        )

    def test_mcp_tool_accepts_materials(self):
        from openglaze_mcp import handle_tool_call

        result = handle_tool_call(
            "suggest_material_substitutions",
            {"recipe": RECIPE, "materials": ["Custer Feldspar"]},
        )
        assert result["success"] is True
        originals = [s["original"].lower() for s in result["suggestions"]]
        assert "custer feldspar" in originals

    def test_cli_materials_flag(self):
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "openglaze_cli",
                "substitutions",
                "--recipe",
                RECIPE,
                "--materials",
                "Custer Feldspar, Silica",
            ],
            capture_output=True,
            text=True,
            cwd=ROOT,
            timeout=120,
        )
        assert proc.returncode == 0
        payload = json.loads(proc.stdout)
        originals = [s["original"].lower() for s in payload["suggestions"]]
        assert "custer feldspar" in originals


class TestD5PersonalModeAuth:
    def _token(self, client):
        resp = _post_json(client, "/api/auth/simple-login", {"display_name": "Tester"})
        assert resp.status_code == 200
        return json.loads(resp.data)["token"]

    def test_read_endpoints_with_token(self, client):
        headers = {"Authorization": f"Bearer {self._token(client)}"}
        for ep in ("/api/stats", "/api/progress", "/api/predictions/leaderboard"):
            resp = client.get(ep, headers=headers)
            assert resp.status_code == 200, (ep, resp.status_code, resp.data)

    def test_predictions_post_with_token(self, client):
        headers = {"Authorization": f"Bearer {self._token(client)}"}
        resp = _post_json(
            client,
            "/api/predictions",
            {"combo_id": 1, "predicted_outcome": "glossy"},
            headers=headers,
        )
        assert resp.status_code == 201

    def test_template_apply_with_token(self, client):
        headers = {"Authorization": f"Bearer {self._token(client)}"}
        resp = client.post("/api/templates/community-glazes/apply", headers=headers)
        assert resp.status_code == 200

    def test_still_401_without_token(self, client):
        for ep in ("/api/stats", "/api/progress", "/api/predictions/leaderboard"):
            assert client.get(ep).status_code == 401


class TestD6JsonErrors:
    def test_json_body_without_content_type_returns_json_415(self, client):
        resp = client.post(
            "/api/combinations/1/promote", data=json.dumps({"result": "x"})
        )
        assert resp.status_code == 415
        assert resp.content_type.startswith("application/json")
        assert "error" in json.loads(resp.data)
