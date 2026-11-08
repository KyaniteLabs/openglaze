#!/usr/bin/env python3
"""OpenGlaze command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, NoReturn

from core.chemistry.batch import calculate_batch
from core.chemistry.substitutions import suggest_substitutions
from core.chemistry.umf import calculate_umf
from core.errors import retry_message


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _parse_cone(value: Any) -> int | str:
    raw = str(value).strip()
    if raw.startswith("0") and len(raw) > 1:
        return raw
    return int(raw)


def _project_brief() -> dict[str, Any]:
    return {
        "name": "OpenGlaze",
        "summary": (
            "Open-source ceramic glaze calculator, UMF analyzer, CTE estimator, recipe manager, and self-hosted "
            "studio tool."
        ),
        "surfaces": {
            "web": "python server.py",
            "cli": "python -m openglaze_cli",
            "mcp": "python -m openglaze_mcp",
            "skill": "skills/openglaze/SKILL.md",
        },
        "core_workflows": [
            "calculate UMF and oxide ratios from glaze recipes",
            "estimate thermal expansion and surface character",
            "scale recipes into practical test batches",
            "suggest substitutions for unavailable materials",
        ],
        "guardrail": (
            "Computational glaze analysis guides test tiles; it does not replace real firings or food-safety "
            "validation."
        ),
    }


def _fail(message: str, code: str) -> NoReturn:
    """Print an actionable error with a concrete retry invocation and exit."""
    print(f"error: {retry_message(message, code)}", file=sys.stderr)
    raise SystemExit(2)


def _run(args: argparse.Namespace) -> dict[str, Any]:
    """Execute a chemistry command; edges raise ValueError for bad input."""
    if args.command == "umf":
        try:
            cone = _parse_cone(args.cone)
        except ValueError:
            _fail(
                f"Invalid cone {args.cone!r}. Use an integer or a zero-padded string like '04'.",
                "invalid_cone",
            )
        return calculate_umf(args.recipe, cone=cone).to_dict()
    if args.command == "batch":
        return calculate_batch(args.recipe, args.size, args.unit)
    return suggest_substitutions(args.recipe).to_dict()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="OpenGlaze CLI for ceramic glaze analysis."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("brief", help="Print a project and agent-surface brief.")

    umf = subparsers.add_parser("umf", help="Calculate UMF and CTE for a recipe.")
    umf.add_argument(
        "--recipe",
        required=True,
        help="Recipe string, e.g. 'Custer Feldspar 45, Silica 25, Whiting 18, EPK 12'.",
    )
    umf.add_argument(
        "--cone",
        default="10",
        help='Firing cone. Use leading zero for low-fire cones, e.g. "04". Defaults to 10.',
    )

    batch = subparsers.add_parser("batch", help="Scale a recipe to a test batch.")
    batch.add_argument("--recipe", required=True, help="Recipe string to scale.")
    batch.add_argument("--size", type=float, required=True, help="Target batch size.")
    batch.add_argument(
        "--unit", default="grams", help="grams or pounds. Defaults to grams."
    )

    substitutions = subparsers.add_parser(
        "substitutions", help="Suggest material substitutions for a recipe."
    )
    substitutions.add_argument(
        "--recipe", required=True, help="Recipe string to analyze."
    )

    args = parser.parse_args(argv)

    if args.command == "brief":
        _print_json(_project_brief())
        return

    payload = _run(args)
    _print_json(payload)
    if payload.get("error"):
        _fail(payload["error"], "unparseable_recipe")


if __name__ == "__main__":
    main()
