#!/usr/bin/env python3
"""
OpenGlaze - Unified Glaze Management Server
Supports both personal (single-user) and cloud (multi-tenant) modes.

Facade module: the implementation lives in the ``webapp`` package
(app factory, routed blueprint modules, DB bootstrap, compatibility
helpers). This file re-exports the public surface so ``python server.py``
(Dockerfile CMD) and ``from server import create_app`` (tests, WSGI)
keep working unchanged.
"""

import logging
import os

from config import load_config

# Configure logging
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

from webapp import (  # noqa: E402
    compute_compatibility,
    compute_compatibility_from_properties,
    create_app,
    get_db_connection,
    init_db,
    seed_database,
)
from webapp.db import _load_seed_rules, _run_migrations  # noqa: E402,F401
from webapp.wsgi import app  # noqa: E402

__all__ = [
    "app",
    "compute_compatibility",
    "compute_compatibility_from_properties",
    "create_app",
    "get_db_connection",
    "init_db",
    "seed_database",
]


# Convenience for direct execution / development
if __name__ == "__main__":
    config = load_config()
    mode = config.get("mode")

    debug = config.get("server", {}).get("debug", False)
    if os.environ.get("FLASK_DEBUG", "").lower() not in ("true", "1"):
        debug = False

    host = config.get("server", {}).get("host", getattr(mode, "HOST", "127.0.0.1"))
    port = int(config.get("server", {}).get("port", getattr(mode, "PORT", 8767)))

    flask_app = create_app(config)

    print("=" * 50)
    print("OpenGlaze - Unified Glaze Management")
    print(f"Mode: {mode.name if hasattr(mode, 'name') else 'personal'}")
    print(f"Running on http://{host}:{port}")
    print(f"Debug: {debug}")
    print("=" * 50)

    flask_app.run(host=host, port=port, debug=debug)
