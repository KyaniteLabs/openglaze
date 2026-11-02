"""Application factory for the OpenGlaze Flask app."""

import logging
import os
import secrets

from flask import Flask, g, jsonify
from flask_cors import CORS

from config import load_config, ConfigurationError
from core.errors import error_payload
from core.glazes import GlazeManager
from core.combinations import CombinationManager
from core.experiments import ExperimentManager
from core.ai.context import ContextRetriever
from core.security import init_security
from webapp.db import get_db_connection, init_db
from webapp.helpers import AUTH_AVAILABLE, auth_enabled
from webapp.routes import ALL_BLUEPRINTS

try:
    from core.auth import AuthMiddleware

except ImportError:
    AUTH_AVAILABLE = False

try:
    from core.studios import StudioManager

    STUDIOS_AVAILABLE = True
except ImportError:
    STUDIOS_AVAILABLE = False

try:
    from core.gamification.manager import GamificationManager

    GAMIFICATION_AVAILABLE = True
except ImportError:
    GAMIFICATION_AVAILABLE = False

try:
    from core.predictions.manager import PredictionManager

    PREDICTIONS_AVAILABLE = True
except ImportError:
    PREDICTIONS_AVAILABLE = False

logger = logging.getLogger(__name__)


def create_app(config: dict = None) -> Flask:
    """Create and configure the OpenGlaze Flask application."""
    from webapp import REPO_ROOT

    app = Flask(__name__, static_folder=str(REPO_ROOT / "frontend"))

    # Load configuration if not provided
    if config is None:
        try:
            config = load_config()
        except ConfigurationError as e:
            logger.error(f"Configuration error: {e}")
            raise

    mode = config.get("mode")
    app.config["MODE"] = mode

    # Secret key for sessions
    secret_key = getattr(mode, "security", None)
    if secret_key:
        secret_key = secret_key.secret_key
    if not secret_key:
        secret_key = secrets.token_hex(32)
    app.config["SECRET_KEY"] = secret_key

    # Feature flags
    features = {
        "auth_enabled": getattr(mode, "AUTH_ENABLED", False),
        "multi_tenant": getattr(mode, "MULTI_TENANT", False),
        "api_access": getattr(mode, "API_ACCESS", False),
        "analytics": getattr(mode, "ANALYTICS", False),
    }
    app.config["FEATURES"] = features

    # Database path (routes read this via current_app.config)
    db_path = config.get("database", {}).get("path", "glaze.db")
    app.config["DATABASE_PATH"] = db_path

    _configure_cors(app)

    # Initialize security
    init_security(app)

    # Initialize auth middleware (cloud mode)
    if features["auth_enabled"] and AUTH_AVAILABLE:
        AuthMiddleware(app)
        logger.info("Authentication middleware enabled")

    # Initialize database schema
    init_db(db_path)

    app.before_request(_make_request_setup(db_path))

    _register_error_handlers(app)

    # Register route blueprints; the static/docs blueprint owns a catch-all
    # route and must be registered last.
    for blueprint in ALL_BLUEPRINTS:
        app.register_blueprint(blueprint)

    return app


def _make_request_setup(db_path: str):
    """Build the per-request manager setup closure bound to a database path."""

    def setup_managers():
        """Set up managers for each request."""
        user_id = None
        if auth_enabled():
            from core.auth import get_user_id

            user_id = get_user_id()
        g.glaze_manager = GlazeManager(db_path, user_id=user_id)
        g.combo_manager = CombinationManager(db_path, user_id=user_id)
        g.exp_manager = ExperimentManager(db_path, user_id=user_id)
        g.context_retriever = ContextRetriever(db_path)
        # Shared DB connection for gamification/predictions (takes conn, not db_path)
        g.db_conn = get_db_connection(db_path)
        if GAMIFICATION_AVAILABLE:
            g.gamification_manager = GamificationManager(g.db_conn)
        if PREDICTIONS_AVAILABLE:
            g.prediction_manager = PredictionManager(g.db_conn)
        if STUDIOS_AVAILABLE:
            # For studio endpoints, user_id comes from simple auth or Ory
            from core.auth.middleware import get_user_id_or_simple

            studio_user_id = get_user_id_or_simple()
            g.studio_manager = StudioManager(db_path, user_id=studio_user_id)

    return setup_managers


def _configure_cors(app: Flask) -> None:
    """Allow localhost dev origins plus any operator-provided extras."""
    configured_port = os.environ.get("FLASK_PORT", "8767")
    cors_origins = [
        f"http://localhost:{configured_port}",
        f"http://127.0.0.1:{configured_port}",
    ]
    extra_cors_origins = [
        origin.strip()
        for origin in os.environ.get("CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    cors_origins.extend(extra_cors_origins)
    CORS(app, origins=cors_origins, supports_credentials=True)


def _register_error_handlers(app: Flask) -> None:
    """Attach JSON error handlers with concrete retry invocations."""

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error_payload("Not found", "not_found")), 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Server error: {e}")
        return jsonify(error_payload("Internal server error", "server_error")), 500

    @app.errorhandler(429)
    def rate_limited(e):
        payload = error_payload(
            "Rate limit exceeded",
            "rate_limited",
            message="Too many requests. Please slow down.",
            retry_after=60,
        )
        response = jsonify(payload)
        response.headers["Retry-After"] = "60"
        return response, 429
