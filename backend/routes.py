from flask import Blueprint, jsonify, request

from backend.services.ask_nova import answer_question


api = Blueprint("api", __name__)


# Temporary in-memory storage for information
# added during the challenge.
new_information = []


# =========================================
# BASIC API
# =========================================

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


# =========================================
# PREDICT
# =========================================

@api.route("/predict", methods=["POST"])
def predict():

    data = request.get_json(silent=True) or {}

    return jsonify({
        "message": "Prediction endpoint ready",
        "received": data
    })


# =========================================
# ASK NOVA
# =========================================

@api.route("/ask", methods=["POST"])
def ask():

    data = request.get_json(silent=True) or {}

    question = data.get(
        "question",
        ""
    ).strip()


    if not question:

        return jsonify({
            "error": "Question is required"
        }), 400


    try:

        answer = answer_question(
            question,
            new_information
        )


        return jsonify({
            "answer": answer
        })


    except Exception as error:

        print(
            f"Ask NOVA error: {error}"
        )


        return jsonify({
            "error":
                "NOVA could not answer the question right now."
        }), 500


# =========================================
# NEW INFORMATION
# =========================================

@api.route(
    "/information",
    methods=["POST"]
)
def add_information():

    data = request.get_json(
        silent=True
    ) or {}


    information = data.get(
        "information",
        ""
    ).strip()


    if not information:

        return jsonify({
            "error": "Information is required"
        }), 400


    new_information.append(
        information
    )


    return jsonify({
        "message":
            "Information received successfully",

        "information":
            information
    })


@api.route(
    "/information",
    methods=["GET"]
)
def get_information():

    return jsonify({
        "information":
            new_information
    })


# =========================================
# PROJECT MEMORY
# =========================================

@api.route(
    "/memory",
    methods=["GET"]
)
def get_memory():

    try:

        from backend.services.ask_nova import (
            load_knowledge
        )


        knowledge = load_knowledge()


        decisions = []
        owners = []
        deadlines = []
        commitments = []
        risks = []
        sources = []


        for document in knowledge:

            filename = document.get(
                "filename",
                "Unknown source"
            )


            insights = document.get(
                "insights",
                {}
            )


            sources.append({
                "filename": filename
            })


            for item in insights.get(
                "decisions",
                []
            ):

                decisions.append({
                    "text": item,
                    "source": filename
                })


            for item in insights.get(
                "owners",
                []
            ):

                owners.append({
                    "text": item,
                    "source": filename
                })


            for item in insights.get(
                "deadlines",
                []
            ):

                deadlines.append({
                    "text": item,
                    "source": filename
                })


            for item in insights.get(
                "commitments",
                []
            ):

                commitments.append({
                    "text": item,
                    "source": filename
                })


            for item in insights.get(
                "risks",
                []
            ):

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

            "new_information":
                new_information

        })


    except Exception as error:

        print(
            f"Memory error: {error}"
        )


        return jsonify({
            "error":
                "Could not load NOVA project memory."
        }), 500