from flask import Blueprint, jsonify, request


api = Blueprint("api", __name__)
new_information = []


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

@api.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}

    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "error": "Question is required"
        }), 400

    return jsonify({
        "answer": "NOVA received your question. AI processing will be connected here."
    })

@api.route("/information", methods=["POST"])
def add_information():
    data = request.get_json(silent=True) or {}

    information = data.get("information", "").strip()

    if not information:
        return jsonify({
            "error": "Information is required"
        }), 400

    new_information.append(information)

    return jsonify({
        "message": "Information received successfully",
        "information": information
    })

@api.route("/information", methods=["GET"])
def get_information():
    return jsonify({
        "information": new_information
    })