"""Studio and lab-queue routes."""

import logging

from flask import Blueprint, g, jsonify, request

from core.security import rate_limit
from webapp.helpers import require_auth_for_write

logger = logging.getLogger(__name__)

bp = Blueprint("studios", __name__)


def _studios_available() -> bool:
    from webapp.app_factory import STUDIOS_AVAILABLE

    return STUDIOS_AVAILABLE


def _get_studio_user():
    """Get user_id and display_name for studio operations."""
    from webapp.helpers import AUTH_AVAILABLE

    from core.auth.middleware import get_simple_user

    simple = get_simple_user()
    if simple:
        return simple["user_id"], simple["display_name"]
    if AUTH_AVAILABLE:
        from core.auth import get_current_user

        user = get_current_user()
        if user:
            return user["user_id"], user.get("email", user.get("display_name", ""))
    return None, None


@bp.route("/api/studios", methods=["POST"])
@rate_limit(requests_per_minute=10)
def create_studio():
    """Create a new studio."""
    if not _studios_available():
        return jsonify({"error": "Studios not available"}), 503

    user_id, display_name = _get_studio_user()
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    data = request.json or {}
    name = (data.get("name") or "").strip()
    if not name or len(name) > 100:
        return jsonify({"error": "Studio name is required (max 100 chars)"}), 400

    studio = g.studio_manager.create_studio(name, display_name)
    return jsonify(studio), 201


@bp.route("/api/studios/join", methods=["POST"])
@rate_limit(requests_per_minute=10)
def join_studio():
    """Join a studio by invite code."""
    if not _studios_available():
        return jsonify({"error": "Studios not available"}), 503

    user_id, display_name = _get_studio_user()
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    data = request.json or {}
    invite_code = (data.get("invite_code") or "").strip().upper()
    if not invite_code:
        return jsonify({"error": "Invite code is required"}), 400

    dn = (data.get("display_name") or display_name).strip()
    studio = g.studio_manager.join_by_code(invite_code, dn, user_id)
    if not studio:
        return jsonify({"error": "Invalid invite code"}), 404

    return jsonify(studio)


@bp.route("/api/studios")
def list_studios():
    """List studios the user belongs to."""
    if not _studios_available():
        return jsonify([])

    user_id, _ = _get_studio_user()
    if not user_id:
        return jsonify([])

    studios = g.studio_manager.get_user_studios(user_id)
    return jsonify(studios)


@bp.route("/api/studios/<studio_id>")
def get_studio_detail(studio_id):
    """Get studio details + members."""
    if not _studios_available():
        return jsonify({"error": "Not available"}), 503

    studio = g.studio_manager.get_studio(studio_id)
    if not studio:
        return jsonify({"error": "Studio not found"}), 404

    members = g.studio_manager.get_members(studio_id)
    return jsonify(
        {
            **studio.to_dict(),
            "members": [m.to_dict() for m in members],
        }
    )


@bp.route("/api/studios/<studio_id>/regenerate-code", methods=["POST"])
def regenerate_invite(studio_id):
    """Admin: regenerate invite code."""
    if not _studios_available():
        return jsonify({"error": "Not available"}), 503

    user_id, _ = _get_studio_user()
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    new_code = g.studio_manager.regenerate_invite_code(studio_id, user_id)
    if not new_code:
        return jsonify({"error": "Only admins can regenerate invite codes"}), 403

    return jsonify({"invite_code": new_code})


@bp.route("/api/studios/<studio_id>", methods=["DELETE"])
def delete_studio(studio_id):
    """Admin: delete studio."""
    if not _studios_available():
        return jsonify({"error": "Not available"}), 503

    user_id, _ = _get_studio_user()
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    if g.studio_manager.delete_studio(studio_id, user_id):
        return jsonify({"success": True})
    return jsonify({"error": "Only admins can delete studios"}), 403


@bp.route("/api/studios/<studio_id>/lab-queue")
def get_lab_queue(studio_id):
    """Get testable combos with claim status."""
    if not _studios_available():
        return jsonify([])

    queue = g.studio_manager.get_lab_queue(studio_id)
    return jsonify(queue)


@bp.route(
    "/api/studios/<studio_id>/lab-queue/<int:combo_id>/claim", methods=["POST"]
)
def claim_combo(studio_id, combo_id):
    """Claim a combo for testing."""
    if not _studios_available():
        return jsonify({"error": "Not available"}), 503

    user_id, display_name = _get_studio_user()
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    assignment = g.studio_manager.claim_combo(
        studio_id, combo_id, user_id, display_name
    )
    if not assignment:
        return jsonify({"error": "Already claimed by someone else"}), 409

    return jsonify(assignment.to_dict()), 201


@bp.route(
    "/api/studios/<studio_id>/lab-queue/<int:combo_id>/release", methods=["POST"]
)
def release_combo(studio_id, combo_id):
    """Release a claimed combo."""
    if not _studios_available():
        return jsonify({"error": "Not available"}), 503

    if g.studio_manager.release_combo(studio_id, combo_id):
        return jsonify({"success": True})
    return jsonify({"error": "Not claimed or already released"}), 404


@bp.route("/api/studios/<studio_id>/my-claims")
def get_my_claims(studio_id):
    """Get combos claimed by current user."""
    if not _studios_available():
        return jsonify([])

    user_id, _ = _get_studio_user()
    if not user_id:
        return jsonify([])

    claims = g.studio_manager.get_my_claims(studio_id, user_id)
    return jsonify([c.to_dict() for c in claims])


@bp.route("/api/studios/<studio_id>/experiments")
def get_studio_experiments(studio_id):
    """Get all experiments shared with a studio."""
    experiments = g.exp_manager.get_studio_experiments(studio_id)
    return jsonify([e.to_dict() for e in experiments])
