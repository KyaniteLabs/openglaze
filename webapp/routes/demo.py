"""Public demo routes (no auth)."""

import json
import logging
from pathlib import Path

from flask import Blueprint, current_app, g, jsonify, request

from webapp import REPO_ROOT
from webapp.compat import compute_compatibility

logger = logging.getLogger(__name__)

bp = Blueprint("demo", __name__)


def _load_demo_glazes():
    """Load curated demo glazes from ceramics-foundation data."""
    try:
        demo_path = REPO_ROOT / "ceramics-foundation" / "data" / "demo-glazes.json"
        if demo_path.exists():
            with open(demo_path, "r") as f:
                data = json.load(f)
                return data.get("glazes", [])
    except Exception as e:
        logger.debug(f"Could not load demo glazes: {e}")
    return []


def _get_demo_glaze_by_name(name: str):
    """Find a demo glaze by name (case-insensitive)."""
    demos = _load_demo_glazes()
    name_lower = name.lower().strip()
    for demo in demos:
        if (
            demo.get("name", "").lower().strip() == name_lower
            or demo.get("id", "").lower().strip() == name_lower
        ):
            return demo
    return None


@bp.route("/api/demo/glazes")
def get_demo_glazes():
    """Get curated demo glazes — real, open-source reference formulations."""
    try:
        glazes = _load_demo_glazes()
        if glazes:
            return jsonify(glazes)
        # Fallback to DB if demo file unavailable
        conn = g.db_conn
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM glazes LIMIT 5")
        rows = cursor.fetchall()
        return jsonify([dict(row) for row in rows])
    except Exception as e:
        logger.error(f"Demo glazes error: {e}")
        return jsonify([])


@bp.route("/api/demo/compatibility", methods=["POST"])
def check_demo_compatibility():
    """Check compatibility between two glazes (public endpoint).

    Works with demo glaze names from the curated collection.
    """
    data = request.json or {}
    glaze_a_name = data.get("glaze_a")
    glaze_b_name = data.get("glaze_b")
    cone = data.get("cone", 10)
    if not glaze_a_name or not glaze_b_name:
        return jsonify({"error": "Both glaze_a and glaze_b are required"}), 400

    try:
        # Try demo glazes first
        demo_a = _get_demo_glaze_by_name(glaze_a_name)
        demo_b = _get_demo_glaze_by_name(glaze_b_name)

        if demo_a and demo_b and demo_a.get("recipe") and demo_b.get("recipe"):
            from core.chemistry import CompatibilityAnalyzer

            analyzer = CompatibilityAnalyzer()
            result = analyzer.analyze(
                base_recipe=demo_a["recipe"],
                top_recipe=demo_b["recipe"],
                base_name=demo_a.get("name", glaze_a_name),
                top_name=demo_b.get("name", glaze_b_name),
                cone=(
                    int(cone)
                    if isinstance(cone, (int, str)) and str(cone).isdigit()
                    else 10
                ),
            )
            return jsonify(result.to_dict())

        # Fallback to DB-based compatibility
        result = compute_compatibility(
            glaze_a_name, glaze_b_name, db_path=current_app.config.get("DATABASE_PATH")
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"Compatibility check error: {e}")
        return jsonify({"error": str(e)}), 500
