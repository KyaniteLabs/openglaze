"""WSGI entry: lazy app proxy so importing has no import-time side effects."""

import logging

from config import load_config, ConfigurationError

logger = logging.getLogger(__name__)


class AppProxy:
    """Lazily create the Flask app on first request (critical for tests)."""

    def __init__(self):
        self._app = None

    def _ensure_app(self):
        if self._app is None:
            try:
                config = load_config()
                from webapp import create_app

                self._app = create_app(config)
            except ConfigurationError as e:
                logger.error(f"Failed to create app: {e}")
                raise
        return self._app

    def __call__(self, environ, start_response):
        return self._ensure_app()(environ, start_response)

    def __getattr__(self, name):
        return getattr(self._ensure_app(), name)


app = AppProxy()
