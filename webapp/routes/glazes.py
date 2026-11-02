"""Glaze CRUD and UMF routes."""

import logging
import sqlite3

from flask import Blueprint, g, jsonify, request

from core.errors import error_payload
from core.glazes import Glaze
from core.security import rate_limit
from webapp.helpers import require_auth_for_write

logger = logging.getLogger(__name__)

bp = Blueprint("glazes", __name__)


@bp.route("/api/glazes")
@rate_limit(requests_per_minute=60)
def get_glazes():
    """Get all glazes."""
    try:
        glazes = g.glaze_manager.get_all()
        return jsonify([glaze.to_dict() for glaze in glazes])
    except sqlite3.OperationalError as e:
        logger.error(f"Database error: {e}")
        return jsonify([])


@bp.route("/api/glazes/<glaze_id>")
@rate_limit(requests_per_minute=60)
def get_glaze(glaze_id: str):
    """Get a specific glaze."""
    glaze = g.glaze_manager.get_by_id(glaze_id)
    if glaze:
        return jsonify(glaze.to_dict())
    return jsonify(error_payload("Glaze not found", "glaze_not_found")), 404


@bp.route("/api/glazes", methods=["POST"])
@rate_limit(requests_per_minute=30)
def create_glaze():
    """Create a new glaze."""
    auth_err = require_auth_for_write()
    if auth_err:
        return auth_err

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    glaze = Glaze.from_dict(data)
    glaze_id = g.glaze_manager.create(glaze)
    return jsonify({"id": glaze_id}), 201


@bp.route("/api/glazes/<glaze_id>", methods=["PUT"])
@rate_limit(requests_per_minute=30)
def update_glaze(glaze_id: str):
    """Update a glaze."""
    auth_err = require_auth_for_write()
    if auth_err:
        return auth_err

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    success = g.glaze_manager.update(glaze_id, data)
    if success:
        return jsonify({"success": True})
    return jsonify({"error": "Update failed"}), 400


@bp.route("/api/glazes/<glaze_id>", methods=["DELETE"])
@rate_limit(requests_per_minute=30)
def delete_glaze(glaze_id: str):
    """Delete a glaze."""
    auth_err = require_auth_for_write()
    if auth_err:
        return auth_err

    success = g.glaze_manager.delete(glaze_id)
    if success:
        return jsonify({"success": True})
    return jsonify({"error": "Delete failed"}), 400


@bp.route("/api/glazes/<glaze_id>/umf")
@rate_limit(requests_per_minute=60)
def get_glaze_umf(glaze_id: str):
    """Calculate UMF for a specific glaze by ID or name.

    Query params:
        cone: Target firing cone (e.g., 6, 10). Defaults to 10.
    """
    try:
        from core.chemistry import calculate_umf
    except ImportError:
        return jsonify(error_payload("Chemistry engine not available", "chemistry_unavailable")), 500

    glaze = g.glaze_manager.get_by_id(glaze_id)
    if not glaze:
        glaze = g.glaze_manager.get_by_name(glaze_id)
    if not glaze:
        return jsonify(error_payload("Glaze not found", "glaze_not_found")), 404

    if not glaze.recipe:
        return jsonify(
            {
                "success": False,
                "error": "No recipe available",
                "glaze_id": glaze_id,
                "glaze_name": glaze.name,
            }
        )

    # Parse optional cone parameter
    cone_param = request.args.get("cone")
    cone = int(cone_param) if cone_param and cone_param.isdigit() else None

    result = calculate_umf(glaze.recipe, cone=cone)
    response = result.to_dict()
    response["glaze_id"] = glaze_id
    response["glaze_name"] = glaze.name
    return jsonify(response)
