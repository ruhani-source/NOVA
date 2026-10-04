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
}


def parse_document(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Detect real PDFs even when the extension is wrong.
    with path.open("rb") as f:
        header = f.read(8)

    if header.startswith(b"%PDF-"):
        result = parse_pdf(str(path))
        result["metadata"]["original_extension"] = path.suffix.lower()
        result["metadata"]["detected_type"] = "pdf"
        return result

    extension = path.suffix.lower()
    parser = PARSERS.get(extension)

    if parser is None:
        raise ValueError(f"Unsupported file type: {extension}")

    return parser(str(path))
