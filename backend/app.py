from flask import Flask, jsonify
from flask_session import Session
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from routes.api import api_routes

app = Flask(__name__)
# Set the secret key for session management. Used for securely signing the session cookie.
app.config["SECRET_KEY"] = "8zMym2xRX3*wRu&2"
# Configure session to not be permanent, meaning sessions will be cleared when the browser is closed.
app.config["SESSION_PERMANENT"] = False
# Set the session type to filesystem to store session data on the local filesystem.
app.config["SESSION_TYPE"] = "filesystem"

# Initialize session handling for the app.
Session(app)

# CORS(app, supports_credentials=True, resources={r"/ask": {"origins": ["192.168.50.58"]}})
# Enable Cross-Origin Resource Sharing (CORS) for all domains on all routes. This allows AJAX requests from other domains.
CORS(app, origins=["http://localhost:5173"]) 

JWTManager(app)

app.register_blueprint(api_routes, url_prefix='/api')

if __name__ == "__main__":
    app.run(debug=True, port=5000)