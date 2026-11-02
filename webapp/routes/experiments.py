"""Experiment pipeline routes."""

import logging

from flask import Blueprint, g, jsonify, request

from core.errors import error_payload
from core.experiments import Experiment
from core.security import rate_limit
from webapp.helpers import require_auth_for_write

logger = logging.getLogger(__name__)

bp = Blueprint("experiments", __name__)


@bp.route("/api/experiments")
@rate_limit(requests_per_minute=60)
def get_experiments():
    """Get all experiments."""
    stage = request.args.get("stage")
    if stage:
        experiments = g.exp_manager.get_by_stage(stage)
    else:
        experiments = g.exp_manager.get_all()
    return jsonify([e.to_dict() for e in experiments])


@bp.route("/api/experiments/active")
@rate_limit(requests_per_minute=60)
def get_active_experiments():
    """Get active experiments."""
    experiments = g.exp_manager.get_active()
    return jsonify([e.to_dict() for e in experiments])


@bp.route("/api/experiments/stats")
@rate_limit(requests_per_minute=60)
def get_experiment_stats():
    """Get experiment pipeline statistics."""
    stats = g.exp_manager.get_pipeline_stats()
    return jsonify(stats)


@bp.route("/api/experiments/<int:exp_id>")
@rate_limit(requests_per_minute=60)
def get_experiment(exp_id: int):
    """Get a specific experiment."""
    exp = g.exp_manager.get_by_id(exp_id)
    if exp:
        return jsonify(exp.to_dict())
    return jsonify(error_payload("Experiment not found", "experiment_not_found")), 404


@bp.route("/api/experiments", methods=["POST"])
@rate_limit(requests_per_minute=30)
def create_experiment():
    """Create a new experiment."""
    auth_err = require_auth_for_write()
    if auth_err:
        return auth_err
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    exp = Experiment.from_dict(data)
    exp_id = g.exp_manager.create(exp)
    return jsonify({"id": exp_id}), 201


@bp.route("/api/experiments/<int:exp_id>/advance", methods=["POST"])
@rate_limit(requests_per_minute=30)
def advance_experiment(exp_id: int):
    """Advance experiment to next stage."""
    auth_err = require_auth_for_write()
    if auth_err:
        return auth_err
    success = g.exp_manager.advance_stage(exp_id)
    if success:
        return jsonify({"success": True})
    return jsonify({"error": "Advance failed"}), 400


@bp.route("/api/experiments/<int:exp_id>/result", methods=["POST"])
@rate_limit(requests_per_minute=30)
def record_experiment_result(exp_id: int):
    """Record experiment result."""
    auth_err = require_auth_for_write()
    if auth_err:
        return auth_err
    data = request.json or {}
    result = data.get("result", "")
    rating = data.get("rating")
    photo = data.get("photo")
    success = g.exp_manager.record_result(exp_id, result, rating, photo)
    if success:
        return jsonify({"success": True})
    return jsonify({"error": "Record failed"}), 400


@bp.route("/api/experiments/<int:exp_id>/archive", methods=["POST"])
@rate_limit(requests_per_minute=30)
def archive_experiment(exp_id: int):
    """Archive an experiment."""
    auth_err = require_auth_for_write()
    if auth_err:
        return auth_err
    data = request.json or {}
    archive_type = data.get("type", "successful")
    success = g.exp_manager.archive(exp_id, archive_type)
    if success:
        return jsonify({"success": True})
    return jsonify({"error": "Archive failed"}), 400


@bp.route("/api/experiments/<int:exp_id>/firing-log", methods=["POST"])
def submit_firing_log(exp_id):
    """Submit a firing log for an experiment."""
    auth_err = require_auth_for_write()
    if auth_err:
        return auth_err
    data = request.json or {}
    try:
        success = g.exp_manager.log_firing_result(exp_id, data)
        if not success:
            return jsonify(error_payload("Experiment not found", "experiment_not_found")), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Update combo prediction grade if confirmation provided
    confirmation = data.get("confirmation")
    exp = g.exp_manager.get_by_id(exp_id)
    if exp and exp.combination_id and confirmation in ("confirmed", "surprise"):
        g.combo_manager.update(
            exp.combination_id,
            {
                "prediction_grade": confirmation,
                "type": confirmation,
            },
        )

        # Complete any lab claim
        if data.get("studio_id"):
            from webapp.app_factory import STUDIOS_AVAILABLE

            if STUDIOS_AVAILABLE:
                g.studio_manager.complete_claim(
                    data["studio_id"], exp.combination_id, exp_id
                )

    return jsonify({"success": True})


@bp.route("/api/experiments/<int:exp_id>/share", methods=["POST"])
def share_experiment(exp_id):
    """Share experiment result with studio."""
    auth_err = require_auth_for_write()
    if auth_err:
        return auth_err
    from webapp.app_factory import STUDIOS_AVAILABLE

    if not STUDIOS_AVAILABLE:
        return jsonify({"error": "Not available"}), 503

    data = request.json or {}
    studio_id = data.get("studio_id")
    if not studio_id:
        return jsonify({"error": "studio_id is required"}), 400

    if g.exp_manager.share_with_studio(exp_id, studio_id):
        return jsonify({"success": True})
    return jsonify(error_payload("Experiment not found", "experiment_not_found")), 404
