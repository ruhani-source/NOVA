from pathlib import Path
from zipfile import BadZipFile

from openpyxl import load_workbook


def parse_xlsx(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"XLSX file not found: {file_path}")

    try:
        workbook = load_workbook(path, data_only=True)
        text_parts = []

        for sheet in workbook.worksheets:
            text_parts.append(f"[Sheet: {sheet.title}]")

            for row in sheet.iter_rows(values_only=True):
                values = [str(value) for value in row if value is not None]

                if values:
                    text_parts.append(" | ".join(values))

        return {
            "filename": path.name,
            "file_type": "xlsx",
            "text": "\n".join(text_parts).strip(),
            "metadata": {
                "sheet_count": len(workbook.sheetnames),
                "sheets": workbook.sheetnames,
            },
        }

    except (BadZipFile, ValueError, KeyError):
        # Some NOVA files have an .xlsx extension but actually contain text.
        try:
            text = path.read_text(
                encoding="utf-8",
                errors="strict"
            ).strip()

            return {
                "filename": path.name,
                "file_type": "xlsx",
                "text": text,
                "metadata": {
                    "warning": "File has .xlsx extension but contains plain text",
                    "detected_type": "text",
                },
            }

        except (UnicodeDecodeError, OSError):
            raise ValueError(
                f"{path.name} has an .xlsx extension but is not a valid "
                "Excel or UTF-8 text file."
            )