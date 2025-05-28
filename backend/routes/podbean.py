from flask import Blueprint, request, jsonify, current_app
from integrations.podbean_mcp.client import MCPClient
import asyncio
from pathlib import Path

podbean_bp = Blueprint("podbean", __name__, url_prefix="/api/podbean")

@podbean_bp.route("/publish", methods=["POST"])
def publish():
    data = request.get_json() or {}
    audio_url = data.get("audioUrl")
    notes     = data.get("notes", "")
    if not audio_url:
        return jsonify(error="audioUrl required"), 400

    async def _do_publish():
        client = MCPClient()
        server_py = (
            Path(__file__).parent.parent
            / "integrations" / "podbean_mcp" / "server.py"
        )
        await client.connect_to_server(str(server_py))
        result = await client.session.call_tool(
            "publish_episode",
            {"file_url": audio_url, "notes": notes}
        )
        await client.cleanup()
        return result

    try:
        raw = asyncio.run(_do_publish())

        # --- STEP 1: unwrap list if needed ---
        if isinstance(raw, list) and raw:
            first = raw[0]
        else:
            first = raw

        # --- STEP 2: extract a plain dict if possible ---
        if hasattr(first, "content") and isinstance(first.content, dict):
            payload = first.content
        # maybe it's already a dict
        elif isinstance(first, dict):
            payload = first
        else:
            # fallback: stringify whatever the tool returned
            payload = {"result": str(first)}

        # --- STEP 3: send only JSON-serializable payload ---
        return jsonify(success=True, **payload)

    except Exception as e:
        current_app.logger.exception("Podbean publish failed")
        return jsonify(error=str(e)), 500