from flask import Blueprint, jsonify, request


api = Blueprint("api", __name__)


@api.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "NOVA API is running"
    })


@api.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy"
    })


@api.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}

    return jsonify({
        "message": "Prediction endpoint ready",
        "received": data
    })