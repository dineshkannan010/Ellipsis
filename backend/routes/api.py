from flask import Blueprint, jsonify, request

api_routes = Blueprint('api_routes', __name__)

# In-memory store (replace with DB in production)
connected_socials = []

# OAuth URLs (examples, replace with actual OAuth endpoints)
OAUTH_URLS = {
    "LinkedIn": "https://www.linkedin.com/oauth/v2/authorization",
    "Reddit": "https://www.reddit.com/api/v1/authorize",
    "Twitter": "https://api.twitter.com/oauth/authenticate"
}

@api_routes.route('/hello')
def hello():
    return jsonify({"message": "Hello from Flask backend!"})

@api_routes.route('/connect', methods=['POST'])
def connect_social():
    platform = request.json.get('platform')
    if platform and platform not in connected_socials:
        connected_socials.append(platform)
        return jsonify({"message": f"{platform} connected"}), 200
    return jsonify({"error": "Invalid request or platform already connected"}), 400

@api_routes.route('/disconnect', methods=['POST'])
def disconnect_social():
    platform = request.json.get('platform')
    if platform and platform in connected_socials:
        connected_socials.remove(platform)
        return jsonify({"message": f"{platform} disconnected"}), 200
    return jsonify({"error": "Invalid request or platform not connected"}), 400

@api_routes.route('/connected_platforms', methods=['GET'])
def get_connected_platforms():
    return jsonify({"connected_platforms": connected_socials}), 200

@api_routes.route('/oauth_url/<platform>', methods=['GET'])
def get_oauth_url(platform):
    url = OAUTH_URLS.get(platform)
    if url:
        return jsonify({"oauth_url": url}), 200
    return jsonify({"error": "Invalid platform"}), 400
