from __future__ import annotations

import sys
from pathlib import Path
import sqlite3
import pandas as pd

from transform_data import transform_all_data

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "property_data.db"


def ensure_output_dirs() -> None:
    """
    Create output folders if they do not exist.
    """
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)


def save_csv(df: pd.DataFrame, file_name: str) -> None:
    """
    Save DataFrame to processed CSV.
    """
    output_path = PROCESSED_DATA_DIR / file_name
    df.to_csv(output_path, index=False)
    print(f"Saved CSV: {output_path.resolve()}")


def save_all_processed_csvs(data: dict[str, pd.DataFrame]) -> None:
    """
    Save final analytical outputs to processed CSV files.
    """
    save_csv(data["revenue_summary"], "revenue_summary.csv")
    save_csv(data["expense_summary"], "expense_summary.csv")
    save_csv(data["occupancy_trends"], "occupancy_trends.csv")
    save_csv(data["pricing_comparison"], "pricing_comparison.csv")


def load_to_sqlite(data: dict[str, pd.DataFrame], db_path: Path = DATABASE_PATH) -> None:
    """
    Load cleaned and summary data into SQLite database tables.
    """
    with sqlite3.connect(db_path) as conn:
        data["clean_rent_payments"].to_sql("rent_payments", conn, if_exists="replace", index=False)
        data["clean_lease_data"].to_sql("lease_data", conn, if_exists="replace", index=False)
        data["clean_expenses"].to_sql("expenses", conn, if_exists="replace", index=False)
        data["clean_comparable_rents"].to_sql("comparable_rents", conn, if_exists="replace", index=False)
        data["clean_tenant_data"].to_sql("tenant_data", conn, if_exists="replace", index=False)

        data["revenue_summary"].to_sql("revenue_summary", conn, if_exists="replace", index=False)
        data["expense_summary"].to_sql("expense_summary", conn, if_exists="replace", index=False)
        data["occupancy_trends"].to_sql("occupancy_trends", conn, if_exists="replace", index=False)
        data["pricing_comparison"].to_sql("pricing_comparison", conn, if_exists="replace", index=False)

    print(f"Loaded data into SQLite database: {db_path.resolve()}")


def main() -> None:
    ensure_output_dirs()

    transformed_data = transform_all_data()

    save_all_processed_csvs(transformed_data)
    load_to_sqlite(transformed_data)

    print("\nETL load step complete.")
    print(f"Processed CSV files saved to: {PROCESSED_DATA_DIR}")
    print(f"SQLite database saved to: {DATABASE_PATH}")


if __name__ == "__main__":
    main()