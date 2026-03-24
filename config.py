import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

RAW_DATA_DIR = BASE_DIR / "data" / "raw"


def ensure_output_dir() -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)