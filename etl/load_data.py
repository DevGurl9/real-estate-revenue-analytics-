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

ANALYSIS_DIR = PROJECT_ROOT / "Real Estate Analysis"

# Template on ONE DRIVE will always autosave and/or sync.
EXCEL_TEMPLATE_PATH = ANALYSIS_DIR / "Real_Estate_Dashboard_Template.xlsm"

# Change to use template on C:\Temp after creating code to copy template from OneDrive to C:\Temp before refreshing dashboard. 
# This will prevent sync issues and allow the template to stay in it's original format with loaded data and formatting.
# EXCEL_TEMPLATE_PATH = Path(r"C:\Temp\Real_Estate_Dashboard_Template.xlsm")

EXCEL_OUTPUT_PATH = ANALYSIS_DIR / "Real_Estate_Dashboard.xlsx"


def ensure_output_dirs() -> None:
    """
    Create output folders if they do not exist.
    """
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)


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


def refresh_excel_dashboard() -> None:
    """
    Open the copied Excel macro-enabled template in C:\\Temp,
    run VBA RefreshDashboard, and let VBA save the final
    Real_Estate_Dashboard.xlsx in the same folder.
    """
    try:
        import win32com.client as win32
    except ImportError as exc:
        raise ImportError(
            "pywin32 is required to run Excel VBA automation. "
            "Install it with: pip install pywin32"
        ) from exc

    temp_template_path = Path(r"C:\Temp\Real_Estate_Dashboard_Template.xlsm")
    excel_output_path = Path(r"C:\Temp\Real_Estate_Dashboard.xlsx")

    if not temp_template_path.exists():
        raise FileNotFoundError(
            f"Copied Excel template not found: {temp_template_path}\n"
            "Expected load_data.py or an earlier step to copy the template to C:\\Temp first."
        )

    excel = None
    wb = None

    try:
        excel = win32.DispatchEx("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False

        print("____________refresh_excel_dashboard before Open__________________")
        print("Template path:", temp_template_path.resolve())
        print("Expected output path:", excel_output_path.resolve())
        print("Output exists before refresh:", excel_output_path.exists())
        print("____________refresh_excel_dashboard end before Open______________")

        wb = excel.Workbooks.Open(str(temp_template_path.resolve()))

        # Write runtime config into hidden config sheet
        ws_config = wb.Worksheets("_config")
        ws_config.Range("B1").Value = str(DATABASE_PATH.resolve())
        ws_config.Range("B2").Value = str(PROJECT_ROOT.resolve())

        # Run VBA macro stored inside the workbook
        excel.Application.Run(f"'{wb.Name}'!RefreshDashboard")

        print("____________refresh_excel_dashboard after VBA____________________")
        print("Template path:", temp_template_path.resolve())
        print("Expected output path:", excel_output_path.resolve())
        print("Output exists after refresh:", excel_output_path.exists())
        print("____________refresh_excel_dashboard end _________________________")

        print(f"Refreshed Excel dashboard: {excel_output_path.resolve()}")

    finally:
        if wb is not None:
            try:
                wb.Close(SaveChanges=False)
            except Exception:
                pass

        if excel is not None:
            try:
                excel.Quit()
            except Exception:
                pass

        wb = None
        excel = None

def run_step(step_name, func, *args, outputs=None):
    try:
        result = func(*args)
        print(f"{step_name} complete")
        
        # Print output locations if provided
        if outputs:
            for label, path in outputs.items():
                print(f"{label}: {path}")
        
        return result
    
    except Exception as e:
        print(f"Failed: {step_name} → {e}")
        raise

def main() -> None:

    run_step("ensure_output_dirs", ensure_output_dirs)

    transformed_data = run_step("transformed_data",  transform_all_data)

    run_step("save_all_processed_csvs", save_all_processed_csvs, transformed_data, outputs={"Processed CSV files": PROCESSED_DATA_DIR})
    run_step("load_to_sqlite", load_to_sqlite, transformed_data, outputs={"SQLite database": DATABASE_PATH})
    run_step("refresh_excel_dashboard", refresh_excel_dashboard, outputs={"Excel dashboard": EXCEL_OUTPUT_PATH})

    print("\nETL load step complete.")

        
         

if __name__ == "__main__":
    main()