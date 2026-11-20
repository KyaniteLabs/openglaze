"""Photo upload and listing routes."""

import logging
import os

from flask import Blueprint, g, jsonify, request

from core.security import rate_limit
from core.upload_utils import save_uploaded_file
from webapp.helpers import require_auth_for_write

logger = logging.getLogger(__name__)

bp = Blueprint("uploads", __name__)


@bp.route("/api/upload", methods=["POST"])
@rate_limit(requests_per_minute=20)
def upload_photo():
    """Upload a photo file. Accepts multipart/form-data with 'photo' field."""
    auth_err = require_auth_for_write()
    if auth_err:
        return auth_err
    if "photo" not in request.files:
        return jsonify({"error": "No photo field in upload"}), 400

    file = request.files["photo"]
    if not file or not file.filename:
        return jsonify({"error": "No file provided"}), 400
    try:
        relative_path = save_uploaded_file(file, os.path.join("frontend", "uploads"))
        return jsonify(
            {"success": True, "path": relative_path, "url": f"/{relative_path}"}
        )
    except (ValueError, OverflowError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"error": "Upload failed"}), 500


@bp.route("/api/photos", methods=["GET"])
@rate_limit(requests_per_minute=60)
def get_photos():
    """Return all experiments that have a photo attached."""
    photos = g.exp_manager.get_all_with_photos()
    return jsonify({"photos": photos})
