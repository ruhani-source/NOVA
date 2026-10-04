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

    extension = path.suffix.lower()

    parser = PARSERS.get(extension)

    if parser is None:
        raise ValueError(f"Unsupported file type: {extension}")

    return parser(str(path))
