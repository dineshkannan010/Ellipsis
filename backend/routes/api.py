from flask import Blueprint, jsonify

api_routes = Blueprint('api_routes', __name__)

@api_routes.route('/hello')
def hello():
    return jsonify({"message": "Hello from Flask backend!"})