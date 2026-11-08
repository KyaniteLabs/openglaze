"""Simple auth routes."""

import logging

from flask import Blueprint, jsonify, request

from core.errors import error_payload
from core.security import rate_limit

logger = logging.getLogger(__name__)

bp = Blueprint("auth_routes", __name__)


@bp.route("/api/auth/simple-login", methods=["POST"])
@rate_limit(requests_per_minute=10)
def simple_login():
    """Login with display name — returns token."""
    from webapp.app_factory import STUDIOS_AVAILABLE

    if not STUDIOS_AVAILABLE:
        return jsonify({"error": "Studios not available"}), 503

    data = request.json or {}
    display_name = (data.get("display_name") or "").strip()
    if not display_name or len(display_name) > 50:
        return jsonify({"error": "Display name is required (max 50 chars)"}), 400

    from core.auth.simple_auth import create_session

    session = create_session(display_name)
    return jsonify(session)


@bp.route("/api/auth/me")
def auth_me():
    """Get current user info from simple auth or Ory."""
    from webapp.helpers import AUTH_AVAILABLE

    from core.auth.middleware import get_simple_user

    simple = get_simple_user()
    if simple:
        return jsonify(simple)

    if AUTH_AVAILABLE:
        from core.auth import get_current_user

        user = get_current_user()
        if user:
            return jsonify(
                {
                    "user_id": user["user_id"],
                    "display_name": user.get("email", user.get("display_name", "")),
                }
            )

    return jsonify(error_payload("Not authenticated", "auth_required")), 401
