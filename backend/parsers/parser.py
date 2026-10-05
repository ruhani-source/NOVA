from pathlib import Path

from backend.parsers.pdf_parser import parse_pdf
from backend.parsers.docx_parser import parse_docx
from backend.parsers.txt_parser import parse_txt
from backend.parsers.md_parser import parse_md
from backend.parsers.csv_parser import parse_csv
from backend.parsers.xlsx_parser import parse_xlsx
from backend.parsers.eml_parser import parse_eml


PARSERS = {
    ".pdf": parse_pdf,
    ".docx": parse_docx,
    ".txt": parse_txt,
    ".md": parse_md,
    ".csv": parse_csv,
    ".xlsx": parse_xlsx,
    ".eml": parse_eml,
    ".png": parse_txt,
}


def parse_document(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with path.open("rb") as f:
        header = f.read(16)

    # Real PDF regardless of extension
    if header.startswith(b"%PDF-"):
        result = parse_pdf(str(path))
        result["metadata"]["original_extension"] = path.suffix.lower()
        result["metadata"]["detected_type"] = "pdf"
        return result

    # Real PNG regardless of extension
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return {
            "filename": path.name,
            "file_type": "image",
            "text": "",
            "metadata": {
                "original_extension": path.suffix.lower(),
                "detected_type": "png",
                "image_path": str(path),
            },
        }

    # ZIP-based Office document regardless of extension
    if header.startswith(b"PK"):
        for parser, detected_type in [
            (parse_docx, "docx"),
            (parse_xlsx, "xlsx"),
        ]:
            try:
                result = parser(str(path))
                result["metadata"]["original_extension"] = path.suffix.lower()
                result["metadata"]["detected_type"] = detected_type
                return result
            except Exception:
                continue

        raise ValueError(f"Unsupported ZIP/Office document: {path.name}")

    extension = path.suffix.lower()

    # Files pretending to be PDF but actually containing readable text
    if extension == ".pdf":
        try:
            text = path.read_text(encoding="utf-8", errors="strict").strip()

            return {
                "filename": path.name,
                "file_type": "txt",
                "text": text,
                "metadata": {
                    "original_extension": ".pdf",
                    "detected_type": "text",
                },
            }
        except UnicodeDecodeError:
            raise ValueError(
                f"Could not determine actual format of {path.name}"
            )

    parser = PARSERS.get(extension)

    if parser is None:
        raise ValueError(f"Unsupported file type: {extension}")

    return parser(str(path))
