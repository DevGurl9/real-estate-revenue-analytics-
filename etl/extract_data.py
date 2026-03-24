from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config import RAW_DATA_DIR


def read_csv_file(file_name: str) -> pd.DataFrame:
    """
    Read a CSV file from the raw data directory.
    """
    file_path = RAW_DATA_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return pd.read_csv(file_path)


def extract_rent_payments() -> pd.DataFrame:
    """
    Load raw rent payment records.
    Expected columns:
        month, unit_id, tenant_id, rent_due, rent_paid, payment_status
    """
    return read_csv_file("rent_payments.csv")


def extract_lease_data() -> pd.DataFrame:
    """
    Load raw lease records.
    Expected columns:
        unit_id, tenant_id, lease_start, lease_end, monthly_rent, bedrooms
    """
    return read_csv_file("lease_data.csv")


def extract_expenses() -> pd.DataFrame:
    """
    Load raw property expense data.
    Expected columns:
        date, category, vendor, amount
    """
    return read_csv_file("expenses.csv")


def extract_comparable_rents() -> pd.DataFrame:
    """
    Load raw comparable market rent data.
    Expected columns:
        neighborhood, bedrooms, square_feet, rent_price
    """
    return read_csv_file("comparable_rents.csv")


def extract_tenant_data() -> pd.DataFrame:
    """
    Load raw tenant/application data.
    Expected columns:
        tenant_id, application_status, source_platform, move_in_date
    """
    return read_csv_file("tenant_data.csv")


def extract_all_data() -> dict[str, pd.DataFrame]:
    """
    Load all raw input files and return them in a dictionary.
    """
    return {
        "rent_payments": extract_rent_payments(),
        "lease_data": extract_lease_data(),
        "expenses": extract_expenses(),
        "comparable_rents": extract_comparable_rents(),
        "tenant_data": extract_tenant_data(),
    }


def main() -> None:
    data = extract_all_data()

    print("Raw data successfully extracted:\n")
    for name, df in data.items():
        print(f"{name}: {df.shape[0]:,} rows x {df.shape[1]} columns")


if __name__ == "__main__":
    main()