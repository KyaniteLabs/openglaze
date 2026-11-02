"""Shared request helpers for OpenGlaze route blueprints."""

import logging
from typing import Optional

from flask import current_app, jsonify

try:
    from core.auth import get_current_user, get_user_id

    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    logging.getLogger(__name__).warning("Auth module not available - cloud mode disabled")

logger = logging.getLogger(__name__)


def auth_enabled() -> bool:
    """True when cloud-mode authentication is enabled and importable."""
    features = current_app.config.get("FEATURES", {})
    return bool(features.get("auth_enabled")) and AUTH_AVAILABLE


def require_auth_for_write():
    """Enforce authentication on write endpoints in cloud mode.

    Returns an error response if auth is required but user is not
    authenticated, or None if the request may proceed.
    """
    if not auth_enabled():
        return None
    try:
        user = get_current_user()
        if user:
            return None
    except Exception as e:
        logger.warning(f"Auth check failed: {e}")
    return jsonify({"error": "Authentication required"}), 401


def get_current_user_id() -> Optional[str]:
    """Get current user ID (cloud mode only)."""
    features = current_app.config.get("FEATURES", {})
    if not features.get("auth_enabled") or not AUTH_AVAILABLE:
        return None
    return get_user_id()
