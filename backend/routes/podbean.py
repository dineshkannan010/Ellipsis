from flask import Blueprint, request, jsonify, current_app
from integrations.podbean_mcp.client import publish_episode  # your function

podbean_bp = Blueprint("podbean", __name__, url_prefix="/api/podbean")

@podbean_bp.route("/publish", methods=["POST"])
def publish():
    data = request.json or {}
    audio_url = data.get("audioUrl")
    notes     = data.get("notes", "")
    if not audio_url:
        return jsonify(error="audioUrl required"), 400

    try:
        result = publish_episode(audio_url, notes)
        return jsonify(success=True, **result)
    except Exception as e:
        current_app.logger.exception("Podbean publish failed")
        return jsonify(error=str(e)), 500