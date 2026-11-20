"""OpenGlaze web application package.

Splits the former 2,283-line ``server.py`` monolith into routed blueprint
modules behind a small application factory. ``server.py`` remains the public
facade (Dockerfile CMD and tests import it), re-exporting everything that
used to live there.
"""

from pathlib import Path

# Repository root (the directory that contains server.py, core/, frontend/, ...).
# The app runs from source with the repo root as the working directory; all
# file-asset paths that used to be ``Path(__file__).parent`` in server.py are
# resolved against this constant instead.
REPO_ROOT = Path(__file__).resolve().parents[1]

# Single source of truth for the version reported by /health.
APP_VERSION = "1.1.0"

from webapp.app_factory import create_app  # noqa: E402
from webapp.compat import (  # noqa: E402
    compute_compatibility,
    compute_compatibility_from_properties,
)
from webapp.db import get_db_connection, init_db, seed_database  # noqa: E402

__all__ = [
    "REPO_ROOT",
    "create_app",
    "compute_compatibility",
    "compute_compatibility_from_properties",
    "get_db_connection",
    "init_db",
    "seed_database",
]
