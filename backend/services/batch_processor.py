import json
from pathlib import Path

from backend.parsers.parser import parse_document
from backend.services.ai_extractor import extract_insights


SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".txt", ".md", ".csv", ".xlsx", ".eml", ".png"
}


def process_dataset(
    input_dir: str = "data/raw",
    output_file: str = "data/processed_insights.json",
) -> list:
    input_path = Path(input_dir)
    output_path = Path(output_file)

    # Resume previous work instead of calling Gemini again.
    if output_path.exists():
        try:
            results = json.loads(output_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            results = []
    else:
        results = []

    already_processed = {
        item["filename"]
        for item in results
        if "filename" in item
    }

    files = [
        path for path in input_path.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    print(f"📂 Found {len(files)} supported documents")

    for index, path in enumerate(files, start=1):
        print(f"\n[{index}/{len(files)}] 📄 {path.name}")

        if path.name in already_processed:
            print("⏭️ Already processed — skipped")
            continue

        try:
            document = parse_document(str(path))

            if document["file_type"] == "image":
                print("🖼️ Real image detected — image analysis pending")
                continue

            if not document["text"].strip():
                print("⚠️ No extractable text — skipped")
                continue

            insights = extract_insights(
                text=document["text"],
                filename=document["filename"],
            )

            results.append({
                "filename": document["filename"],
                "file_type": document["file_type"],
                "metadata": document["metadata"],
                "insights": insights,
            })

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps(results, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            print(
                "✅ "
                f"{len(insights['decisions'])} decisions | "
                f"{len(insights['owners'])} owners | "
                f"{len(insights['deadlines'])} deadlines | "
                f"{len(insights['commitments'])} commitments | "
                f"{len(insights['risks'])} risks"
            )

        except Exception as error:
            print(f"❌ Skipped: {error}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\n💾 Saved {len(results)} processed documents to {output_path}")

    return results


if __name__ == "__main__":
    process_dataset()
