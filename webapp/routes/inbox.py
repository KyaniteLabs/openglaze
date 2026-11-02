"""Inbox routes."""

import logging

from flask import Blueprint, current_app, jsonify, request

from core.security import rate_limit
from webapp.db import get_db_connection
from webapp.helpers import get_current_user_id, require_auth_for_write

logger = logging.getLogger(__name__)

bp = Blueprint("inbox", __name__)


@bp.route("/api/inbox", methods=["GET"])
@rate_limit(requests_per_minute=60)
def get_inbox():
    """Get inbox items."""
    conn = get_db_connection(current_app.config.get("DATABASE_PATH", "glaze.db"))
    cursor = conn.cursor()

    user_id = get_current_user_id()
    if user_id:
        cursor.execute(
            "SELECT * FROM inbox WHERE user_id = ? OR user_id IS NULL", (user_id,)
        )
    else:
        cursor.execute("SELECT * FROM inbox WHERE user_id IS NULL")

    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@bp.route("/api/inbox", methods=["POST"])
@rate_limit(requests_per_minute=30)
def add_to_inbox():
    """Add idea to inbox."""
    auth_err = require_auth_for_write()
    if auth_err:
        return auth_err
    data = request.json or {}
    conn = get_db_connection(current_app.config.get("DATABASE_PATH", "glaze.db"))
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO inbox (base, top, notes, user_id) VALUES (?, ?, ?, ?)",
        (
            data.get("base"),
            data.get("top"),
            data.get("notes"),
            get_current_user_id(),
        ),
    )
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": last_id}), 201
