#!/usr/bin/env python3
"""OpenGlaze command-line interface."""

from __future__ import annotations

import argparse
import json
from typing import Any

from core.chemistry.batch import calculate_batch
from core.chemistry.substitutions import suggest_substitutions
from core.chemistry.umf import calculate_umf


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _project_brief() -> dict[str, Any]:
    return {
        "name": "OpenGlaze",
        "summary": "Open-source ceramic glaze calculator, UMF analyzer, CTE estimator, recipe manager, and self-hosted studio tool.",
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
        "guardrail": "Computational glaze analysis guides test tiles; it does not replace real firings or food-safety validation.",
    }


def main() -> None:
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
        "--cone", type=int, default=10, help="Firing cone. Defaults to 10."
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

    args = parser.parse_args()

    if args.command == "brief":
        _print_json(_project_brief())
    elif args.command == "umf":
        _print_json(calculate_umf(args.recipe, cone=args.cone).to_dict())
    elif args.command == "batch":
        _print_json(calculate_batch(args.recipe, args.size, args.unit))
    elif args.command == "substitutions":
        _print_json(suggest_substitutions(args.recipe).to_dict())


if __name__ == "__main__":
    main()
