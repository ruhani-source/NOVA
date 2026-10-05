from pathlib import Path

def parse_txt(file_path: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"TXT file not found: {file_path}")
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    return {"filename": path.name, "file_type": "txt", "text": text, "metadata": {}}
