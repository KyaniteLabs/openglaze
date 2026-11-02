"""Health and mode-info routes."""

from flask import Blueprint, current_app, jsonify

from core.security import get_rate_limiter

from webapp import APP_VERSION

bp = Blueprint("health", __name__)


@bp.route("/health")
def health_check():
    """Basic health check."""
    mode = current_app.config.get("MODE")
    return jsonify(
        {
            "status": "healthy",
            "mode": mode.name if hasattr(mode, "name") else "unknown",
            "version": APP_VERSION,
        }
    )


@bp.route("/api/health")
def api_health():
    """Detailed health check."""
    mode = current_app.config.get("MODE")
    return jsonify(
        {
            "status": "healthy",
            "mode": mode.name if hasattr(mode, "name") else "unknown",
            "features": current_app.config.get("FEATURES", {}),
            "rate_limit_stats": get_rate_limiter().get_stats(),
        }
    )


@bp.route("/api/mode")
def get_mode_info():
    """Get current mode information."""
    mode = current_app.config.get("MODE")
    return jsonify(
        {
            "mode": mode.name if hasattr(mode, "name") else "personal",
            "features": current_app.config.get("FEATURES", {}),
            "theme": getattr(mode, "DEFAULT_THEME", "dark"),
        }
    )
