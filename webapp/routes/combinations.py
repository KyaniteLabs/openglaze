"""Combination CRUD, simulation, and compatibility routes."""

import logging

from flask import Blueprint, current_app, g, jsonify, request

from core.combinations import Combination
from core.errors import error_payload
from core.security import rate_limit
from webapp.helpers import get_current_user_id, require_auth_for_write

logger = logging.getLogger(__name__)

bp = Blueprint("combinations", __name__)


@bp.route("/api/combinations")
@rate_limit(requests_per_minute=60)
def get_combinations():
    """Get all combinations."""
    combo_type = request.args.get("type")
    if combo_type == "research-backed":
        combos = g.combo_manager.get_research_backed()
    elif combo_type == "user-prediction":
        combos = g.combo_manager.get_user_predictions()
    elif combo_type == "proven":
        combos = g.combo_manager.get_research_backed()  # backward compat
    elif combo_type == "hypothesis":
        combos = g.combo_manager.get_user_predictions()  # backward compat
    else:
        combos = g.combo_manager.get_all()
    return jsonify([c.to_dict() for c in combos])


@bp.route("/api/combinations/grouped")
@rate_limit(requests_per_minute=60)
def get_combinations_grouped():
    """Get combinations grouped by base glaze."""
    grouped = g.combo_manager.get_grouped_by_base()
    result = {}
    for base, combos in grouped.items():
        result[base] = [c.to_dict() for c in combos]
    return jsonify(result)


@bp.route("/api/combinations/<int:combo_id>")
@rate_limit(requests_per_minute=60)
def get_combination(combo_id: int):
    """Get a specific combination."""
    combo = g.combo_manager.get_by_id(combo_id)
    if combo:
        return jsonify(combo.to_dict())
    return jsonify(error_payload("Combination not found", "combination_not_found")), 404


@bp.route("/api/combinations", methods=["POST"])
@rate_limit(requests_per_minute=30)
def create_combination():
    """Create a new combination."""
    auth_err = require_auth_for_write()
    if auth_err:
        return auth_err
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    combo = Combination.from_dict(data)

    # Check for Shino warning
    warning = g.combo_manager.check_shino_warning(combo.top, combo.base)
    if warning:
        logger.info(f"Shino warning for {combo.top} over {combo.base}")
        # Return warning but still create

    combo_id = g.combo_manager.create(combo)
    return jsonify({"id": combo_id, "warning": warning}), 201


@bp.route("/api/combinations/<int:combo_id>/promote", methods=["POST"])
@rate_limit(requests_per_minute=30)
def promote_combination(combo_id: int):
    """Promote a hypothesis to confirmed."""
    from webapp.app_factory import GAMIFICATION_AVAILABLE, PREDICTIONS_AVAILABLE

    auth_err = require_auth_for_write()
    if auth_err:
        return auth_err
    data = request.json or {}
    result = data.get("result", "")
    success = g.combo_manager.promote_to_confirmed(combo_id, result)
    if success:
        # Gamification hooks
        user_id = get_current_user_id()
        if user_id and GAMIFICATION_AVAILABLE:
            g.gamification_manager.on_combination_tested(user_id, combo_id, "proven")
            g.gamification_manager.log_activity(
                user_id, "combination_tested", {"combination_id": combo_id}
            )
        if user_id and PREDICTIONS_AVAILABLE:
            g.prediction_manager.resolve_predictions(combo_id, "proven")
        return jsonify({"success": True})
    return jsonify({"error": "Promotion failed"}), 400


@bp.route("/api/combinations/<int:combo_id>", methods=["PUT"])
@rate_limit(requests_per_minute=30)
def update_combination(combo_id: int):
    """Update a combination (stage, prediction_grade, etc.)."""
    auth_err = require_auth_for_write()
    if auth_err:
        return auth_err
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    success = g.combo_manager.update(combo_id, data)
    if success:
        return jsonify({"success": True})
    return jsonify({"error": "Update failed"}), 400


@bp.route("/api/combinations/<int:combo_id>/simulate", methods=["POST"])
@rate_limit(requests_per_minute=10)
def simulate_combination(combo_id: int):
    """Run chemistry simulation for a single combo."""
    try:
        from core.simulation.runner import simulate_combo

        combo = g.combo_manager.get_by_id(combo_id)
        if not combo:
            return (
                jsonify(
                    error_payload("Combination not found", "combination_not_found")
                ),
                404,
            )

        base_glaze = g.glaze_manager.get_by_name(combo.base)
        top_glaze = g.glaze_manager.get_by_name(combo.top)

        prediction = simulate_combo(
            base_glaze=base_glaze,
            top_glaze=top_glaze,
            combo=combo,
            db_path=current_app.config.get("DATABASE_PATH", "glaze.db"),
        )

        g.combo_manager.update(
            combo_id,
            {
                "prediction_grade": prediction.get("prediction_grade", "unknown"),
                "chemistry": prediction.get("chemistry_explanation"),
                "result": prediction.get("predicted_result"),
            },
        )
        return jsonify(prediction)
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/combinations/simulate-all", methods=["POST"])
@rate_limit(requests_per_minute=1)
def simulate_all_combinations():
    """Run chemistry simulation for all unsimulated combos."""
    try:
        from core.simulation.batch_simulate import batch_simulate

        auth_enabled = current_app.config.get("FEATURES", {}).get("auth_enabled")
        result = batch_simulate(
            db_path=current_app.config.get("DATABASE_PATH", "glaze.db"),
            user_id=get_current_user_id() if auth_enabled else None,
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"Batch simulation error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/combinations/<int:combo_id>/compatibility")
@rate_limit(requests_per_minute=60)
def get_combo_compatibility(combo_id: int):
    """Calculate compatibility for a specific combination.

    Query params:
        cone: Target firing cone (e.g., 6, 10). Defaults to 10.
    """
    try:
        from core.chemistry import CompatibilityAnalyzer
    except ImportError:
        return (
            jsonify(
                error_payload("Chemistry engine not available", "chemistry_unavailable")
            ),
            500,
        )

    combo = g.combo_manager.get_by_id(combo_id)
    if not combo:
        return (
            jsonify(error_payload("Combination not found", "combination_not_found")),
            404,
        )

    base_glaze = g.glaze_manager.get_by_name(combo.base)
    top_glaze = g.glaze_manager.get_by_name(combo.top)

    base_recipe = base_glaze.recipe if base_glaze else None
    top_recipe = top_glaze.recipe if top_glaze else None

    if not base_recipe and not top_recipe:
        return jsonify(
            {
                "success": False,
                "error": "One or both glazes have no recipe",
                "base_recipe_available": bool(base_recipe),
                "top_recipe_available": bool(top_recipe),
            }
        )

    # Parse optional cone parameter
    cone_param = request.args.get("cone")
    cone = int(cone_param) if cone_param and cone_param.isdigit() else None

    analyzer = CompatibilityAnalyzer()
    result = analyzer.analyze(
        base_recipe=base_recipe,
        top_recipe=top_recipe,
        base_name=combo.base or "",
        top_name=combo.top or "",
        cone=cone,
    )
    return jsonify(result.to_dict())
