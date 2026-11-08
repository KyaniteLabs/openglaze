"""Validate the checked-in architecture owner inventory against repository paths."""

import fnmatch
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_architecture_inventory():
    policy = json.loads((ROOT / "qa/architecture-paths.json").read_text())
    assert set(policy) == {"schema_version", "repo", "paths"}
    assert policy["schema_version"] == 1
    assert policy["repo"] == "github.com/KyaniteLabs/openglaze"
    assert policy["paths"]
    files = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file()]
    patterns = []
    for entry in policy["paths"]:
        assert set(entry) == {"pattern", "layer", "owner"}
        assert entry["owner"] in {"Engineering", "Product"}
        assert entry["layer"].strip()
        pattern = entry["pattern"]
        assert not pattern.startswith("/") and ".." not in pattern.split("/")
        assert any(fnmatch.fnmatchcase(p, pattern) for p in files), pattern
        patterns.append(pattern)
    assert len(patterns) == len(set(patterns))
    for sensitive in (
        "server.py",
        "core/auth/simple_auth.py",
        "core/db.py",
        "core/upload_utils.py",
        "config/loader.py",
        ".github/workflows/ci.yml",
        ".forgejo/workflows/ci.yml",
        "docker-compose.yml",
    ):
        assert any(fnmatch.fnmatchcase(sensitive, p) for p in patterns), sensitive


def test_worker_read_contract():
    instructions = (ROOT / "AGENTS.md").read_text()
    for name in ("PRODUCT.md", "ARCHITECTURE.md"):
        assert name in instructions
        assert (ROOT / name).read_text().strip()
