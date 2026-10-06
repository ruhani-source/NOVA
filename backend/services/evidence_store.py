"""
Evidence corpus for NOVA: every passage of data/raw with a precise locator.

Each file is read according to its *actual* content (not its extension):
- PDF:   one segment per page            -> "page 1"
- XLSX:  one segment per row with cells  -> "feuille 'Plan projet', ligne 7 (A7:G7)"
- Email: headers + decoded body lines    -> "en-têtes", "L12"
- Text:  one segment per line            -> "L12"
- PNG:   manual transcription from data/image_transcriptions.json

Email attachments are matched to the identical file in data/raw by SHA-256,
so a duplicated attachment is never counted as independent evidence.

Rebuild the corpus with:
    python -m backend.services.evidence_store
"""

import hashlib
import json
import re
import unicodedata
from email import policy
from email.parser import BytesParser
from io import BytesIO
from pathlib import Path

import openpyxl
from pypdf import PdfReader


BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
CORPUS_FILE = BASE_DIR / "data" / "evidence_corpus.json"
IMAGE_TRANSCRIPTIONS_FILE = BASE_DIR / "data" / "image_transcriptions.json"

# Challenge instructions, not project evidence.
EXCLUDED_FILES = {"README.txt", ".gitkeep"}

EMAIL_HEADER = re.compile(
    rb"^(Date|From|To|Subject|Message-ID|MIME-Version):", re.MULTILINE
)


def detect_type(data: bytes) -> str:
    if data.startswith(b"%PDF-"):
        return "pdf"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"PK"):
        return "xlsx"
    if len(EMAIL_HEADER.findall(data[:2000])) >= 3:
        return "email"
    return "text"


def _pdf_segments(data: bytes) -> list[dict]:
    reader = PdfReader(BytesIO(data))

    return [
        {"locator": f"page {number}", "text": (page.extract_text() or "").strip()}
        for number, page in enumerate(reader.pages, start=1)
    ]


def _xlsx_segments(data: bytes) -> list[dict]:
    workbook = openpyxl.load_workbook(BytesIO(data))
    segments = []

    for sheet in workbook.worksheets:
        for row in sheet.iter_rows():
            cells = [cell for cell in row if cell.value not in (None, "")]

            if not cells:
                continue

            first, last = row[0].coordinate, row[-1].coordinate
            values = " | ".join(f"{c.coordinate}={c.value}" for c in cells)

            segments.append({
                "locator": f"feuille '{sheet.title}', ligne {row[0].row} ({first}:{last})",
                "text": values,
            })

            for cell in cells:
                if cell.comment:
                    segments.append({
                        "locator": f"feuille '{sheet.title}', commentaire {cell.coordinate}",
                        "text": cell.comment.text,
                    })

    return segments


def _line_segments(text: str) -> list[dict]:
    return [
        {"locator": f"L{number}", "text": line.strip()}
        for number, line in enumerate(text.splitlines(), start=1)
        if line.strip()
    ]


def _email_segments(data: bytes, hashes: dict[str, str]) -> list[dict]:
    message = BytesParser(policy=policy.default).parsebytes(data)

    headers = " | ".join(
        f"{name}: {message.get(name, '')}"
        for name in ("Date", "From", "To", "Subject")
    )
    segments = [{"locator": "en-têtes", "text": headers}]

    body = ""
    attachments = []

    for part in message.walk():
        if part.is_multipart():
            continue

        if part.get_content_disposition() == "attachment":
            payload = part.get_payload(decode=True) or b""
            digest = hashlib.sha256(payload).hexdigest()
            attachments.append((part.get_filename(), hashes.get(digest)))

        elif part.get_content_type() == "text/plain" and not body:
            body = part.get_content()

    segments.extend(_line_segments(body))

    for name, same_file in attachments:
        note = f"Pièce jointe « {name} »"

        if same_file:
            note += (
                f" : contenu identique au fichier {same_file} du corpus "
                "(ne pas compter comme confirmation indépendante)"
            )

        segments.append({"locator": "pièce jointe", "text": note})

    return segments


def _load_image_transcriptions() -> dict:
    if not IMAGE_TRANSCRIPTIONS_FILE.exists():
        return {}

    data = json.loads(IMAGE_TRANSCRIPTIONS_FILE.read_text(encoding="utf-8"))
    return data.get("images", {})


def build_evidence_corpus(raw_dir: Path = RAW_DIR) -> list[dict]:
    paths = sorted(
        path for path in Path(raw_dir).iterdir()
        if path.is_file() and path.name not in EXCLUDED_FILES
    )

    hashes = {
        hashlib.sha256(path.read_bytes()).hexdigest(): path.name
        for path in paths
    }
    transcriptions = _load_image_transcriptions()
    corpus = []

    for path in paths:
        data = path.read_bytes()
        detected = detect_type(data)
        note = ""

        if detected == "pdf":
            segments = _pdf_segments(data)
        elif detected == "xlsx":
            segments = _xlsx_segments(data)
        elif detected == "email":
            segments = _email_segments(data, hashes)
        elif detected == "png":
            image = transcriptions.get(path.name)

            if image:
                note = "Image : transcription manuelle. " + image["shows"]
                segments = [
                    {"locator": f"capture, élément {number}", "text": line}
                    for number, line in enumerate(image["lines"], start=1)
                ]
            else:
                note = "Image non transcrite : contenu inconnu."
                segments = []
        else:
            segments = _line_segments(data.decode("utf-8", errors="replace"))

        corpus.append({
            "filename": path.name,
            "extension": path.suffix.lower(),
            "detected_type": detected,
            "extension_matches": _extension_matches(path.suffix.lower(), detected),
            "note": note,
            "segments": segments,
        })

    return corpus


def _extension_matches(extension: str, detected: str) -> bool:
    expected = {
        "pdf": {".pdf"},
        "png": {".png"},
        "xlsx": {".xlsx"},
        "email": {".eml"},
        "text": {".txt", ".md", ".csv"},
    }
    return extension in expected[detected]


def save_evidence_corpus(output_file: Path = CORPUS_FILE) -> list[dict]:
    corpus = build_evidence_corpus()
    output_file.write_text(
        json.dumps(corpus, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return corpus


def load_evidence_corpus() -> list[dict]:
    """Saved corpus if present, otherwise built from data/raw."""

    if CORPUS_FILE.exists():
        return json.loads(CORPUS_FILE.read_text(encoding="utf-8"))

    if RAW_DIR.exists():
        return build_evidence_corpus()

    return []


def format_corpus_for_prompt(corpus: list[dict]) -> str:
    blocks = []

    for document in corpus:
        header = (
            f"=== FICHIER : {document['filename']} "
            f"(contenu réel : {document['detected_type']}"
        )

        if not document["extension_matches"]:
            header += ", l'extension ne correspond pas au contenu"

        header += ")"

        if document["segments"] and document["detected_type"] in ("text", "email"):
            first = document["segments"][0]["text"][:90]
            header += f" — commence par : « {first} »"

        lines = [header]

        if document["note"]:
            lines.append(document["note"])

        lines.extend(
            f"[{segment['locator']}] {segment['text']}"
            for segment in document["segments"]
        )
        blocks.append("\n".join(lines))

    return "\n\n".join(blocks)


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in text if not unicodedata.combining(char))


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9-]+", _normalize(text)) if len(token) > 2}


def search_evidence(query: str, limit: int = 10, corpus: list[dict] | None = None) -> list[dict]:
    """
    Keyword search over the corpus. Returns the best-matching passages:
    [{"filename", "locator", "text", "score"}], best first.
    """

    query_tokens = _tokens(query)

    if not query_tokens:
        return []

    corpus = corpus if corpus is not None else load_evidence_corpus()
    results = []

    for document in corpus:
        for segment in document["segments"]:
            score = len(query_tokens & _tokens(segment["text"]))

            if score:
                results.append({
                    "filename": document["filename"],
                    "locator": segment["locator"],
                    "text": segment["text"],
                    "score": score,
                })

    results.sort(key=lambda item: -item["score"])
    return results[:limit]


QUOTE = re.compile(r"«\s*(.+?)\s*»")
FRAGMENT_SEPARATORS = re.compile(r"\[\s*(?:\.\.\.|…)\s*\]|\.\.\.|…|\s/\s")


def _comparable(text: str) -> str:
    text = _normalize(text).replace("*", "").replace("`", "")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def verify_quotes(answer: str, corpus: list[dict] | None = None) -> list[dict]:
    """
    Check that each «quoted» passage appears in a file cited on the same
    line. Returns the problems: [{"files", "quote"}]. Nested quotes and
    fragments shorter than 15 characters are not checked.
    """

    corpus = corpus if corpus is not None else load_evidence_corpus()
    texts = {
        document["filename"]: _comparable(
            " ".join(segment["text"] for segment in document["segments"])
        )
        for document in corpus
    }
    problems = []

    for line in answer.splitlines():
        files = [name for name in texts if name in line]

        if not files:
            continue

        for quote in QUOTE.findall(line):
            for fragment in FRAGMENT_SEPARATORS.split(quote):
                fragment = _comparable(fragment)

                if len(fragment) < 15:
                    continue

                if not any(fragment in texts[name] for name in files):
                    problems.append({"files": files, "quote": quote})
                    break

    return problems


if __name__ == "__main__":
    documents = save_evidence_corpus()
    segment_count = sum(len(document["segments"]) for document in documents)
    print(f"💾 Saved {len(documents)} documents / {segment_count} passages to {CORPUS_FILE}")
