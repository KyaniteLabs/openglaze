"""Chemistry analysis routes: batch, scale, compare, optimize, substitutions, defects."""

import logging

from flask import Blueprint, current_app, jsonify, request

from core.errors import error_payload
from core.security import rate_limit
from webapp.helpers import get_current_user_id

logger = logging.getLogger(__name__)

bp = Blueprint("chemistry", __name__)


@bp.route("/api/chemistry/batch", methods=["POST"])
@rate_limit(requests_per_minute=5)
def batch_chemistry_analysis():
    """Run batch UMF and compatibility analysis for all glazes and combinations.

    Request body (optional):
        cone: Target firing cone for all analyses (default: 10)
    """
    data = request.json or {}
    cone = data.get("cone", 10)

    try:
        from core.chemistry import BatchAnalyzer
    except ImportError:
        return jsonify(error_payload("Chemistry engine not available", "chemistry_unavailable")), 500

    try:
        analyzer = BatchAnalyzer(
            db_path=current_app.config.get("DATABASE_PATH", "glaze.db"),
            user_id=get_current_user_id()
            if current_app.config.get("FEATURES", {}).get("auth_enabled")
            else None,
            cone=int(cone) if cone is not None else 10,
        )
        report = analyzer.generate_report()
        return jsonify(report)
    except Exception as e:
        logger.error(f"Batch chemistry analysis error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/chemistry/scale", methods=["POST"])
@rate_limit(requests_per_minute=60)
def scale_recipe():
    """Scale a glaze recipe to a target batch size."""
    data = request.json or {}
    recipe = data.get("recipe")
    batch_size = data.get("batch_size_grams")
    unit = data.get("unit", "grams")

    if not recipe or not batch_size:
        return jsonify(error_payload("recipe and batch_size_grams are required", "missing_batch_size")), 400

    try:
        from core.chemistry.batch import calculate_batch

        result = calculate_batch(recipe, float(batch_size), unit)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Recipe scaling error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/chemistry/compare", methods=["POST"])
@rate_limit(requests_per_minute=60)
def compare_glaze_recipes():
    """Compare two glaze recipes chemically.

    Request body:
        recipe_a: First recipe string
        recipe_b: Second recipe string
        name_a: Name for first recipe (optional)
        name_b: Name for second recipe (optional)
        cone: Target firing cone (optional, default 10)
    """
    data = request.json or {}
    recipe_a = data.get("recipe_a", "")
    recipe_b = data.get("recipe_b", "")
    name_a = data.get("name_a", "Recipe A")
    name_b = data.get("name_b", "Recipe B")
    cone = data.get("cone", 10)

    if not recipe_a or not recipe_b:
        return jsonify(error_payload("recipe_a and recipe_b are required", "missing_recipe")), 400

    try:
        from core.chemistry import compare_recipes

        result = compare_recipes(
            recipe_a,
            recipe_b,
            name_a=name_a,
            name_b=name_b,
            cone=int(cone) if cone is not None else 10,
        )
        return jsonify(result.to_dict())
    except Exception as e:
        logger.error(f"Recipe comparison error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/chemistry/optimize", methods=["POST"])
@rate_limit(requests_per_minute=60)
def optimize_glaze_recipe():
    """Optimize a glaze recipe to hit target properties.

    Request body:
        recipe: Recipe string (e.g. "Custer Feldspar 45, Silica 25, Whiting 18, EPK 12")
        target: One of 'target_cte', 'reduce_cte', 'increase_cte',
                'more_matte', 'more_glossy', 'reduce_alkali', 'reduce_running'
        target_value: Required for 'target_cte' (e.g. 6.5), optional hint for others
        max_suggestions: Number of suggestions to return (default 5)
    """
    data = request.json or {}
    recipe = data.get("recipe", "")
    target = data.get("target", "")
    target_value = data.get("target_value")
    max_suggestions = data.get("max_suggestions", 5)

    if not recipe:
        return jsonify(error_payload("recipe is required", "missing_recipe")), 400
    if not target:
        return jsonify(error_payload("target is required", "invalid_target")), 400

    valid_targets = {
        "target_cte",
        "reduce_cte",
        "increase_cte",
        "more_matte",
        "more_glossy",
        "reduce_alkali",
        "reduce_running",
    }
    if target not in valid_targets:
        return (
            jsonify(
                error_payload(
                    f"Invalid target. Must be one of: {', '.join(sorted(valid_targets))}",
                    "invalid_target",
                )
            ),
            400,
        )

    if target == "target_cte" and target_value is None:
        return jsonify(error_payload("target_value is required for target_cte", "missing_target_value")), 400

    try:
        tv = float(target_value) if target_value is not None else None
        ms = int(max_suggestions)
    except (ValueError, TypeError):
        return (
            jsonify(error_payload("target_value and max_suggestions must be numeric", "invalid_target")),
            400,
        )

    try:
        from core.chemistry import optimize_recipe

        result = optimize_recipe(
            recipe,
            target,
            target_value=tv,
            max_suggestions=ms,
        )
        return jsonify(result.to_dict())
    except Exception as e:
        logger.error(f"Recipe optimization error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/chemistry/substitutions", methods=["POST"])
@rate_limit(requests_per_minute=60)
def get_substitutions():
    """Get material substitution suggestions for a recipe.

    Request body:
        recipe: Recipe string or object
        material: Specific material name to find substitutes for (optional)
    """
    data = request.json or {}
    recipe = data.get("recipe", "")
    material = data.get("material", "")

    if not recipe and not material:
        return jsonify(error_payload("recipe or material is required", "missing_recipe")), 400

    try:
        from core.chemistry import SubstitutionEngine

        engine = SubstitutionEngine()

        if material:
            # Single material lookup
            suggestions = engine.suggest(material)
            return jsonify(
                {
                    "success": True,
                    "material": material,
                    "suggestions": [
                        {
                            "original": s.original,
                            "substitute": s.substitute,
                            "ratio": s.ratio,
                            "confidence": s.confidence,
                            "notes": s.notes,
                            "chemistry_impact": s.chemistry_impact,
                        }
                        for s in suggestions
                    ],
                }
            )
        else:
            # Full recipe analysis
            from core.chemistry import suggest_substitutions

            result = suggest_substitutions(recipe)
            return jsonify(result.to_dict())
    except Exception as e:
        logger.error(f"Substitution error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/chemistry/defects", methods=["POST"])
@rate_limit(requests_per_minute=60)
def predict_glaze_defects():
    """Predict potential defects for a glaze recipe.

    Request body:
        recipe: Recipe string or object
        cone: Target firing cone (optional, default 10)
        clay_body_cte: CTE of clay body in ×10⁻⁶/°C (optional)
    """
    data = request.json or {}
    recipe = data.get("recipe", "")
    cone = data.get("cone", 10)
    clay_body_cte = data.get("clay_body_cte")

    if not recipe:
        return jsonify(error_payload("recipe is required", "missing_recipe")), 400

    try:
        from core.chemistry import predict_defects

        result = predict_defects(
            recipe,
            cone=int(cone) if cone is not None else 10,
            clay_body_cte=(
                float(clay_body_cte) if clay_body_cte is not None else None
            ),
        )
        return jsonify(result.to_dict())
    except Exception as e:
        logger.error(f"Defect prediction error: {e}")
        return jsonify({"error": str(e)}), 500
