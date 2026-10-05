from flask import Blueprint, jsonify, request

from backend.services.ask_nova import answer_question
from backend.services import database_service


api = Blueprint("api", __name__)


@api.route("/", methods=["GET"])
def home():
    return jsonify({"message": "NOVA API is running"})


@api.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


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
        return jsonify({"error": "Question is required"}), 400

    try:
        additional_information = database_service.get_information()

        answer = answer_question(
            question,
            additional_information
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
        return jsonify({"error": "Information is required"}), 400

    try:
        database_service.save_information(information)

        return jsonify({
            "message": "Information received successfully",
            "information": information
        })

    except Exception as error:
        print(f"Information save error: {error}")

        return jsonify({
            "error": "Could not save the information."
        }), 500


@api.route("/information", methods=["GET"])
def get_information():
    try:
        information = database_service.get_information()

        return jsonify({
            "information": information
        })

    except Exception as error:
        print(f"Information retrieval error: {error}")

        return jsonify({
            "error": "Could not retrieve information."
        }), 500


@api.route("/memory", methods=["GET"])
def get_memory():
    try:
        from backend.services.ask_nova import load_knowledge

        knowledge = load_knowledge()

        decisions = []
        owners = []
        deadlines = []
        commitments = []
        risks = []
        sources = []

        for document in knowledge:
            filename = document.get("filename", "Unknown source")
            insights = document.get("insights", {})

            sources.append({
                "filename": filename
            })

            for item in insights.get("decisions", []):
                decisions.append({
                    "text": item,
                    "source": filename
                })

            for item in insights.get("owners", []):
                owners.append({
                    "text": item,
                    "source": filename
                })

            for item in insights.get("deadlines", []):
                deadlines.append({
                    "text": item,
                    "source": filename
                })

            for item in insights.get("commitments", []):
                commitments.append({
                    "text": item,
                    "source": filename
                })

            for item in insights.get("risks", []):
                risks.append({
                    "text": item,
                    "source": filename
                })

        return jsonify({
            "decisions": decisions,
            "owners": owners,
            "deadlines": deadlines,
            "commitments": commitments,
            "risks": risks,
            "sources": sources,
            "new_information": database_service.get_information()
        })

    except Exception as error:
        print(f"Memory error: {error}")

        return jsonify({
            "error": "Could not load NOVA project memory."
        }), 500