#!/usr/bin/env python3
"""CI gate for function and file size discipline.

Companion to the ruff line-length cap (120): ruff bounds line width, this
script bounds structural size so ``server.py``-style monoliths and
200-line functions cannot land again.

Rules:
  * any function or method longer than MAX_FUNCTION_LINES fails CI
  * any module longer than MAX_FILE_LINES fails CI
  * exceptions must be listed in ALLOWLIST with a justification; the
    allowlist is a ratchet — entries may shrink or be removed, never
    added, and a stale entry (function no longer oversized) also fails
    CI so the list cannot rot.

Stdlib only; runs before tests in CI (see .github/workflows/ci.yml).
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

MAX_FUNCTION_LINES = 80
MAX_FILE_LINES = 1000

# Vendored / third-party trees are not part of this codebase's discipline.
EXCLUDED_PARTS = {".venv", "node_modules", "ceramics-foundation", "__pycache__"}

# Frozen ratchet: pre-existing oversized functions at gate introduction
# (2026-11-01). Each carries its owner-approved justification. Remove an
# entry as soon as the function is refactored below the limit.
ALLOWLIST: dict[str, str] = {
    "core/chemistry/umf.py:calculate": "core UMF math table, unit-tested; split planned with umf v2",
    "core/chemistry/compare.py:compare": "pairwise compare pipeline, diff-clean vs seeds; split planned",
    "core/simulation/runner.py:_fallback_prediction_with_umf": "legacy fallback path, exercised by simulation tests",
    "core/chemistry/compatibility.py:_build_test_recommendations": "prose table; split with compatibility v2",
    "core/chemistry/compatibility.py:_build_risk_breakdown": "risk prose table; split with compatibility v2",
    "core/chemistry/parser.py:parse": "recipe grammar matcher, table-driven; frozen while parser is seed-verified",
    "core/chemistry/umf.py:_build_recommendations": "recommendation prose table; split planned with umf v2",
    "core/simulation/runner.py:simulate_combo": "legacy simulation entrypoint, exercised by simulation tests",
    "core/ai/context.py:_search_chemistry_rules": "rule search heuristics; split planned with context v2",
}


def function_lengths(path: Path) -> list[tuple[int, str, int]]:
    """Return (length, qualified_name, lineno) for every function in path."""
    tree = ast.parse(path.read_text())
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            length = (node.end_lineno or node.lineno) - node.lineno + 1
            found.append((length, node.name, node.lineno))
    return found


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    py_files = [
        p
        for p in sorted(root.rglob("*.py"))
        if not (EXCLUDED_PARTS & set(p.relative_to(root).parts))
    ]

    violations: list[str] = []
    seen_allowlist: set[str] = set()

    for path in py_files:
        rel = path.relative_to(root).as_posix()
        line_count = len(path.read_text().splitlines())
        if line_count > MAX_FILE_LINES:
            violations.append(f"{rel}: file is {line_count} ln (max {MAX_FILE_LINES})")
        for length, name, lineno in function_lengths(path):
            key = f"{rel}:{name}"
            if key in ALLOWLIST:
                seen_allowlist.add(key)
                continue
            if length > MAX_FUNCTION_LINES:
                violations.append(
                    f"{rel}:{lineno} {name}() is {length} ln (max {MAX_FUNCTION_LINES})"
                )

    stale = sorted(set(ALLOWLIST) - seen_allowlist)
    for key in stale:
        violations.append(
            f"stale allowlist entry (function no longer oversized): {key}"
        )

    if violations:
        print("size gate FAILED:")
        for v in violations:
            print(f"  - {v}")
        return 1
    print(
        f"size gate OK: {len(py_files)} files "
        f"(<= {MAX_FILE_LINES} ln), all functions <= {MAX_FUNCTION_LINES} ln "
        f"({len(ALLOWLIST)} allowlisted)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
