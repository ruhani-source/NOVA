import json
import os
import time

from google import genai
from google.genai import types


def extract_insights(text: str, filename: str = "") -> dict:
    """
    Extract structured project information from document text using Gemini.
    """

    if not text.strip():
        return {
            "decisions": [],
            "owners": [],
            "deadlines": [],
            "commitments": [],
            "risks": [],
        }

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are NOVA, an AI assistant analyzing enterprise project documents.

Analyze the document below and extract ONLY information explicitly supported
by the document. Do not invent missing information.

Return:
- decisions: important decisions that were made
- owners: people or teams responsible for work
- deadlines: dates or time limits associated with work
- commitments: promises, obligations, or agreed actions
- risks: problems, blockers, uncertainties, or project risks

For each extracted item, preserve enough context that another person can
understand it.

Source filename: {filename}

DOCUMENT:
{text}
"""

    response = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "decisions": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "owners": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "deadlines": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "commitments": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "risks": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": [
                    "decisions",
                    "owners",
                    "deadlines",
                    "commitments",
                    "risks",
                ],
            },
        ),
            )
            break

        except Exception as error:
            if attempt == 2:
                raise

            print(f"⚠️ Gemini unavailable — retrying in {2 ** (attempt + 1)}s...")
            time.sleep(2 ** (attempt + 1))

    return json.loads(response.text)
