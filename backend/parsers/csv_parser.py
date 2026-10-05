from pathlib import Path
import csv

def parse_csv(file_path: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    rows = []
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(" | ".join(str(cell) for cell in row))

    return {
        "filename": path.name,
        "file_type": "csv",
        "text": "\n".join(rows).strip(),
        "metadata": {"row_count": len(rows)},
    }
