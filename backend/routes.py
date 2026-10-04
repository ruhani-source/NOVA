from flask import Blueprint, jsonify, request

from backend.services.ask_nova import answer_question


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

    try:
        information = new_information

        answer = answer_question(
            question,
            information
        )

        return jsonify({
            "answer": answer
        })

    except Exception as error:
        print(f"Ask NOVA error: {error}")

        return jsonify({
            "error": "NOVA could not answer the question right now."
        }), 500

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