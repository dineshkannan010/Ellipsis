from flask import Blueprint, jsonify, request, current_app
from agent.crawler import crawler
from agent.generator import summarize_contents
from agent.voice import text_2_audio
from agent.generator import load_prompt_template
from dotenv import load_dotenv
from flask_sse import sse
from types import SimpleNamespace as Namespace
from threading import Thread


api_routes = Blueprint('api', __name__)

load_dotenv()


# In-memory store (replace with DB in production)
connected_socials = []



@api_routes.route('/connect', methods=['POST'])
def connect_platform():
    platform = request.json.get('platform')
    if platform and platform not in connected_socials:
        connected_socials.append(platform)
        return jsonify({"message": f"{platform} connected"}), 200
    return jsonify({"error": "Invalid request or already connected"}), 400

@api_routes.route('/disconnect', methods=['POST'])
def disconnect_platform():
    platform = request.json.get('platform')
    if platform and platform in connected_socials:
        connected_socials.remove(platform)
        return jsonify({"message": f"{platform} disconnected"}), 200
    return jsonify({"error": "Invalid request or not connected"}), 400

@api_routes.route('/connected_platforms', methods=['GET'])
def get_connected_platforms():
    return jsonify({"connected_platforms": connected_socials}), 200


def _run_pipeline(query: str, app):
    # push the Flask app context so current_app works
    with app.app_context():
        # 1) Crawl
        sse.publish({"status": "crawler_started"}, type="status")
        args = Namespace(
            url="https://www.nytimes.com/sitemaps/new/news.xml.gz",
            chunk_size=1000,
            max_depth=3,
            max_concurrent=10
        )
        url_to_text = crawler(args)
        sse.publish({"status": "content_crawled"}, type="status")

        # 2) Initial persona scripts
        sse.publish({"status": "initial_response_generation_started"}, type="status")
        responses, final_script = summarize_contents(url_to_text, sse)

        # 3) Publish final script
        formatted = "\n\n".join(f"**{sp}:** {ln}" for sp, ln in final_script)
        sse.publish({"script": formatted}, type="script")
        sse.publish({"status": "script_ready"}, type="status")

        # 4) Generate audio
        sse.publish({"status": "audio_generation_started"}, type="status")
        try:
            audio_file = text_2_audio(final_script)
        except Exception as e:
            current_app.logger.exception("TTS generation failed")
            sse.publish({
                "status": "audio_error",
                "message": str(e)
            }, type="status")
            return
        sse.publish({"audio": f"/audio/{audio_file}"}, type="audio")
        sse.publish({"status": "podcast_generated"}, type="status")


@api_routes.route('/generate', methods=['POST'])
def generate():
    data = request.json or {}
    query = data.get("query", "")

    # capture the true Flask app so the worker thread can push context
    app_obj = current_app._get_current_object()

    # fire-and-forget
    Thread(target=_run_pipeline, args=(query, app_obj), daemon=True).start()

    # immediately return so the frontend POST doesn’t hang
    return jsonify(success=True), 202