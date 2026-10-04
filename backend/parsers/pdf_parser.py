from pathlib import Path

from pypdf import PdfReader


def parse_pdf(file_path: str) -> dict:
    """
    Extract text and basic metadata from a PDF file.

    Args:
        file_path: Path to the PDF file.

    Returns:
        A standardized dictionary containing the file information and text.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    reader = PdfReader(path)

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    full_text = "\n".join(pages).strip()

    return {
        "filename": path.name,
        "file_type": "pdf",
        "text": full_text,
        "metadata": {
            "page_count": len(reader.pages),
        },
    }