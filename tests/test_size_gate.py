"""Mutation tests for the size gate (scripts/check_sizes.py).

The gate is a ratchet: oversized functions need an allowlist entry, and an
entry whose function is no longer oversized (or no longer exists) must
fail CI so the list cannot rot.
"""

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "check_sizes", REPO_ROOT / "scripts" / "check_sizes.py"
)
check_sizes = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_sizes)


def _write_module(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)


def _oversized() -> str:
    return "def big():\n" + "    x = 1\n" * 90


def _small() -> str:
    return "def small():\n    return 1\n"


def test_allowlisted_oversized_function_passes(tmp_path, capsys):
    _write_module(tmp_path, "pkg/mod.py", _oversized())
    rc = check_sizes.main(
        root=tmp_path, allowlist={"pkg/mod.py:big": "core UMF math table"}
    )
    assert rc == 0
    assert "size gate OK" in capsys.readouterr().out


def test_shrunk_allowlisted_function_fails_as_stale(tmp_path, capsys):
    """Security round-1 finding: a retained <=80-line exception must fail."""
    _write_module(tmp_path, "pkg/mod.py", _small())
    rc = check_sizes.main(
        root=tmp_path, allowlist={"pkg/mod.py:small": "was oversized once"}
    )
    assert rc == 1
    out = capsys.readouterr().out
    assert "stale allowlist entry" in out
    assert "pkg/mod.py:small" in out
    assert "remove the entry" in out


def test_absent_allowlist_entry_fails(tmp_path, capsys):
    _write_module(tmp_path, "pkg/mod.py", _small())
    rc = check_sizes.main(
        root=tmp_path, allowlist={"pkg/gone.py:big": "points at nothing"}
    )
    assert rc == 1
    assert "no such oversized function" in capsys.readouterr().out


def test_unknown_oversized_function_fails(tmp_path, capsys):
    _write_module(tmp_path, "pkg/mod.py", _oversized())
    rc = check_sizes.main(root=tmp_path, allowlist={})
    assert rc == 1
    out = capsys.readouterr().out
    assert "big() is 91 ln (max 80)" in out


def test_oversized_file_fails(tmp_path, capsys):
    _write_module(
        tmp_path,
        "pkg/huge.py",
        "".join(f"# line {i}\n" for i in range(1001)),
    )
    rc = check_sizes.main(root=tmp_path, allowlist={})
    assert rc == 1
    assert "file is 1001 ln (max 1000)" in capsys.readouterr().out


def test_real_repository_still_passes():
    """The shipped tree and allowlist satisfy the gate, as CI requires."""
    assert check_sizes.main() == 0


def test_gate_is_importable_as_ci_invokes_it():
    """CI runs ``python scripts/check_sizes.py``; the entrypoint must work."""
    import subprocess

    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "check_sizes.py")],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "size gate OK" in proc.stdout
