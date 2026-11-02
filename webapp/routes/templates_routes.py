"""Template routes (mixed auth)."""

import logging

from flask import Blueprint, g, jsonify

from core.security import rate_limit
from webapp.helpers import get_current_user_id

logger = logging.getLogger(__name__)

bp = Blueprint("templates_routes", __name__)


def _templates_available() -> bool:
    try:
        from core.templates import load_template, list_templates  # noqa: F401

        return True
    except ImportError:
        return False


@bp.route("/api/templates")
def get_templates():
    """List available templates."""
    if not _templates_available():
        return jsonify({"error": "Templates not available"}), 503
    try:
        from core.templates import list_templates

        templates = list_templates()
        return jsonify(templates)
    except Exception as e:
        logger.error(f"List templates error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/templates/<template_id>")
def get_template(template_id):
    """Get a specific template by ID."""
    if not _templates_available():
        return jsonify({"error": "Templates not available"}), 503
    try:
        from core.templates import load_template

        template = load_template(template_id)
        if template:
            return jsonify(template)
        return jsonify({"error": "Template not found"}), 404
    except Exception as e:
        logger.error(f"Load template error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/templates/<template_id>/apply", methods=["POST"])
@rate_limit(requests_per_minute=10)
def apply_template(template_id):
    """Apply a template — insert glazes into user's account."""
    if not _templates_available():
        return jsonify({"error": "Templates not available"}), 503

    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    try:
        from core.templates import load_template

        template = load_template(template_id)
        if not template:
            return jsonify({"error": "Template not found"}), 404

        conn = g.db_conn
        cursor = conn.cursor()
        inserted = _insert_template_glazes(cursor, template_id, template, user_id)

        conn.commit()
        return jsonify(
            {"inserted": inserted, "total": len(template.get("glazes", []))}
        )
    except Exception as e:
        logger.error(f"Apply template error: {e}")
        return jsonify({"error": str(e)}), 500


def _insert_template_glazes(cursor, template_id: str, template: dict, user_id) -> int:
    """Insert a template's glazes; returns the number actually inserted."""
    inserted = 0
    for glaze in template.get("glazes", []):
        glaze_id = glaze.get("id", f"{template_id}-{inserted}")
        cursor.execute(
            """INSERT OR IGNORE INTO glazes
            (id, name, family, hex, chemistry, behavior, layering, warning, recipe, catalog_code, food_safe, notes, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                glaze_id,
                glaze.get("name"),
                glaze.get("family"),
                glaze.get("hex"),
                glaze.get("chemistry"),
                glaze.get("behavior"),
                glaze.get("layering"),
                glaze.get("warning"),
                glaze.get("recipe"),
                glaze.get("catalog_code"),
                glaze.get("food_safe"),
                glaze.get("notes"),
                user_id,
            ),
        )
        if cursor.rowcount > 0:
            inserted += 1
    return inserted
