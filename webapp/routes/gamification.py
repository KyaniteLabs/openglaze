"""Gamification routes (auth required)."""

import logging

from flask import Blueprint, g, jsonify

from core.security import rate_limit
from webapp.helpers import get_current_user_id

logger = logging.getLogger(__name__)

bp = Blueprint("gamification", __name__)


def _gamification_available() -> bool:
    from webapp.app_factory import GAMIFICATION_AVAILABLE

    return GAMIFICATION_AVAILABLE


@bp.route("/api/stats")
@rate_limit(requests_per_minute=60)
def get_user_stats():
    """Get user gamification stats and badges."""
    if not _gamification_available():
        return jsonify({"error": "Gamification not available"}), 503

    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    try:
        stats = g.gamification_manager.get_stats(user_id)
        badges = g.gamification_manager.get_badges(user_id)
        return jsonify(
            {
                "stats": stats.to_dict() if stats else None,
                "badges": [b.to_dict() for b in badges] if badges else [],
            }
        )
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/progress")
@rate_limit(requests_per_minute=60)
def get_progress():
    """Get user progress — combo counts + gamification stats."""
    if not _gamification_available():
        return jsonify({"error": "Gamification not available"}), 503

    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    try:
        conn = g.db_conn
        cursor = conn.cursor()

        combo_counts = _combo_counts(cursor, user_id)
        stats = g.gamification_manager.get_stats(user_id)

        return jsonify(
            {
                **combo_counts,
                "stats": stats.to_dict() if stats else None,
            }
        )
    except Exception as e:
        logger.error(f"Progress error: {e}")
        return jsonify({"error": str(e)}), 500


def _combo_counts(cursor, user_id) -> dict:
    """Count combinations by test state and type for the progress report."""

    def count(sql):
        cursor.execute(sql, (user_id,))
        return cursor.fetchone()[0]

    cursor.execute(
        "SELECT stage, COUNT(*) FROM combinations WHERE user_id = ? GROUP BY stage",
        (user_id,),
    )
    stage_breakdown = dict(cursor.fetchall())

    return {
        "total_combos": count("SELECT COUNT(*) FROM combinations WHERE user_id = ?"),
        "tested_combos": count(
            "SELECT COUNT(*) FROM combinations "
            "WHERE user_id = ? AND stage IN ('tested', 'proven', 'confirmed')"
        ),
        "research_combos": count(
            "SELECT COUNT(*) FROM combinations "
            "WHERE user_id = ? AND type = 'research-backed'"
        ),
        "prediction_combos": count(
            "SELECT COUNT(*) FROM combinations "
            "WHERE user_id = ? AND type = 'user-prediction'"
        ),
        "stage_breakdown": stage_breakdown,
    }
