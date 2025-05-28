from flask import Blueprint, request, jsonify, current_app
from integrations.podbean_mcp.client import MCPClient
import asyncio
from pathlib import Path

podbean_bp = Blueprint("podbean", __name__, url_prefix="/api/podbean")

@podbean_bp.route("/publish", methods=["POST"])
def publish():
    data = request.json or {}
    audio_url = data.get("audioUrl")
    notes     = data.get("notes", "")
    if not audio_url:
        return jsonify(error="audioUrl required"), 400

    try:
        # do the async dance inline:
        async def _do_publish():
            client = MCPClient()
            server_path = Path(__file__).parent.parent / "integrations" / "podbean_mcp" / "server.py"
            await client.connect_to_server(str(server_path))
            res = await client.session.call_tool(
                "publish_episode", 
                {"file_url": audio_url, "notes": notes}
            )
            await client.cleanup()
            return res

        result = asyncio.run(_do_publish())
        return jsonify(success=True, **result)
    except Exception as e:
        current_app.logger.exception("Podbean publish failed")
        return jsonify(error=str(e)), 500