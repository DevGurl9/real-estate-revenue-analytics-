from pathlib import Path

import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config import RAW_DATA_DIR, ensure_output_dir

EXPECTED_OUTPUT_FILES = {
    "rent_payments.csv",
    "lease_data.csv",
    "expenses.csv",
    "comparable_rents.csv",
    "tenant_data.csv",
}

def clear_existing_output_files(remove_all_csv: bool = False) -> None:
    """
    Remove existing output CSV files from data/raw.

    If remove_all_csv is False:
        remove only the expected project output files.

    If remove_all_csv is True:
        remove every CSV file in data/raw.
    """
    ensure_output_dir()

    if remove_all_csv:
        files_to_remove = RAW_DATA_DIR.glob("*.csv")
    else:
        files_to_remove = [RAW_DATA_DIR / name for name in EXPECTED_OUTPUT_FILES]

    for file_path in files_to_remove:
        if file_path.exists():
            file_path.unlink()
            print(f"Removed existing file: {file_path}")
            

