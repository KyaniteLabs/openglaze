"""Prediction routes (auth required)."""

import logging

from flask import Blueprint, g, jsonify, request

from core.security import rate_limit
from webapp.helpers import get_current_user_id

logger = logging.getLogger(__name__)

bp = Blueprint("predictions", __name__)


def _predictions_available() -> bool:
    from webapp.app_factory import PREDICTIONS_AVAILABLE

    return PREDICTIONS_AVAILABLE


@bp.route("/api/predictions", methods=["POST"])
@rate_limit(requests_per_minute=30)
def create_prediction():
    """Create a prediction for a combination."""
    if not _predictions_available():
        return jsonify({"error": "Predictions not available"}), 503

    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    data = request.json or {}
    combo_id = data.get("combo_id")
    predicted_outcome = data.get("predicted_outcome", "")
    confidence = data.get("confidence", 50)

    if not combo_id or not predicted_outcome:
        return (
            jsonify({"error": "combo_id and predicted_outcome are required"}),
            400,
        )

    try:
        result = g.prediction_manager.create_prediction(
            user_id, combo_id, predicted_outcome, confidence
        )
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Create prediction error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/predictions/leaderboard")
@rate_limit(requests_per_minute=60)
def get_prediction_leaderboard():
    """Get prediction leaderboard (user vs AI)."""
    if not _predictions_available():
        return jsonify({"error": "Predictions not available"}), 503

    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    try:
        leaderboard = g.prediction_manager.get_leaderboard(user_id)
        return jsonify(leaderboard)
    except Exception as e:
        logger.error(f"Leaderboard error: {e}")
        return jsonify({"error": str(e)}), 500
