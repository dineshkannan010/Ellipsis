from flask import Flask, jsonify
from flask_session import Session
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from routes.api import api_routes
from flask_sse import sse
from flask import send_from_directory
from routes.podbean import podbean_bp

app = Flask(__name__)
# Set the secret key for session management. Used for securely signing the session cookie.
app.config["SECRET_KEY"] = "8zMym2xRX3*wRu&2"
# Configure session to not be permanent, meaning sessions will be cleared when the browser is closed.
app.config["SESSION_PERMANENT"] = False
# Set the session type to filesystem to store session data on the local filesystem.
app.config["SESSION_TYPE"] = "filesystem"

app.config["REDIS_URL"] = "redis://localhost:6380"
app.config["SSE_REDIS_URL"] = app.config["REDIS_URL"]

# Initialize session handling for the app.
Session(app)

# CORS(app, supports_credentials=True, resources={r"/ask": {"origins": ["192.168.50.58"]}})
# Enable Cross-Origin Resource Sharing (CORS) for all domains on all routes. This allows AJAX requests from other domains.
CORS(app, resources={
    r"/api/*": {"origins": "http://localhost:5173"},
    r"/stream": {"origins": "http://localhost:5173"}
})

JWTManager(app)
# SSE setup
app.register_blueprint(sse, url_prefix='/stream')

# Register API routes
app.register_blueprint(api_routes, url_prefix='/api')

app.register_blueprint(podbean_bp)

@app.route('/audio/<path:filename>')
def audio(filename):
    return send_from_directory('static/audio', filename, mimetype='audio/wav')

if __name__ == "__main__":
    # enable threading so /stream can stay alive while /generate runs
    app.run(debug=True, port=5000, threaded=True)