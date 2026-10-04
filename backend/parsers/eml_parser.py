from pathlib import Path
from email import policy
from email.parser import BytesParser

def parse_eml(file_path: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"EML file not found: {file_path}")

    with path.open("rb") as f:
        message = BytesParser(policy=policy.default).parse(f)

    body_parts = []

    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain" and part.get_content_disposition() != "attachment":
                try:
                    body_parts.append(part.get_content())
                except Exception:
                    pass
    else:
        try:
            body_parts.append(message.get_content())
        except Exception:
            pass

    body = "\n".join(body_parts).strip()

    text = (
        f"From: {message.get('From', '')}\n"
        f"To: {message.get('To', '')}\n"
        f"Date: {message.get('Date', '')}\n"
        f"Subject: {message.get('Subject', '')}\n\n"
        f"{body}"
    ).strip()

    return {
        "filename": path.name,
        "file_type": "eml",
        "text": text,
        "metadata": {
            "from": str(message.get("From", "")),
            "to": str(message.get("To", "")),
            "subject": str(message.get("Subject", "")),
            "date": str(message.get("Date", "")),
        },
    }
