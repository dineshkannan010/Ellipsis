from flask import Blueprint, jsonify, request
from agent.crawler import crawler
from agent.generator import summarize_contents
from agent.voice import text_2_audio
from agent.generator import load_prompt_template
from dotenv import load_dotenv
from flask_sse import sse
from argparse import Namespace

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

@api_routes.route('/generate', methods=['POST'])
def generate():
    # data = request.json
    # query = data.get('query')
    args = Namespace(
        url="https://www.nytimes.com/sitemaps/new/news.xml.gz",
        chunk_size=1000,
        max_depth=3,
        max_concurrent=10
    )

    # Step 1: Notify frontend crawling started
    sse.publish({"status": "crawler_started"}, type='status')

    url_to_text = crawler(args)  # modify crawler to accept direct queries
    sse.publish({"status": "content_crawled"}, type='status')

    # Step 2: Initial responses generation
    sse.publish({"status": "initial_response_generation_started"}, type='status')

    responses, final_script = summarize_contents(url_to_text, sse)  # Pass sse for live updates

    # Step 3: Notify frontend audio generation started
    sse.publish({"status": "audio_generation_started"}, type='status')

    # Generate audio from the script
    audio_path = text_2_audio(final_script)  # Modify function to return audio file path

    # Publish audio URL to frontend via SSE
    sse.publish({"audio": f"/audio/{audio_path}"}, type='audio')
    print(f"SSE Audio URL sent: /audio/{audio_path}")
    return jsonify({
        "responses": responses,
        "final_script": final_script,
        "audio_url": f"/audio/{audio_path}"
    })


