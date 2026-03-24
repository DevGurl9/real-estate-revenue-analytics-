"""
generate_synthetic_data
    Purpose:
        Creates raw data tables described in the project plan: 
        rent_payments.csv, lease_data.csv, expenses.csv, comparable_rents.csv, 
        and tenant_data.csv. It’s designed to generate realistic synthetic data 
        for a portfolio-safe real estate analytics project.
"""
from __future__ import annotations

import sys
from pathlib import Path
import random
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


from config import RAW_DATA_DIR, ensure_output_dir
from clear_output_files import clear_existing_output_files

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
SEED = 42
NUM_UNITS = 12
NUM_TENANTS = 18
START_MONTH = "2024-01-01"
NUM_MONTHS = 24

RAW_DATA_DIR = Path("data/raw")


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def ensure_output_dir() -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def set_random_seed(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)


def random_date_between(start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.Timestamp:
    """Return a random date between two timestamps."""
    delta_days = (end_date - start_date).days
    if delta_days <= 0:
        return start_date
    return start_date + pd.Timedelta(days=random.randint(0, delta_days))


# ------------------------------------------------------------
# Synthetic master data
# ------------------------------------------------------------
def generate_units() -> pd.DataFrame:
    neighborhoods = [
        "Astoria",
        "Bronx",
        "Brooklyn",
        "Flushing",
        "Harlem",
        "Jersey City",
        "Long Island City",
        "Queens",
        "Staten Island",
        "Upper Manhattan",
        "Yonkers",
        "Hoboken",
    ]

    rows = []
    for i in range(1, NUM_UNITS + 1):
        bedrooms = random.choice([0, 1, 1, 2, 2, 3])
        square_feet = {
            0: random.randint(350, 550),
            1: random.randint(500, 750),
            2: random.randint(700, 1050),
            3: random.randint(950, 1400),
        }[bedrooms]

        rows.append(
            {
                "unit_id": i,
                "unit_code": f"UNIT-{i:03d}",
                "bedrooms": bedrooms,
                "square_feet": square_feet,
                "neighborhood": random.choice(neighborhoods),
            }
        )

    return pd.DataFrame(rows)


def generate_tenant_data(num_tenants: int = NUM_TENANTS) -> pd.DataFrame:
    first_names = [
        "James", "Maria", "David", "Aisha", "Kevin", "Sofia", "Daniel",
        "Nina", "Michael", "Rosa", "Chris", "Tiana", "Andre", "Elena",
        "Marcus", "Janelle", "Brian", "Lina", "Omar", "Rachel"
    ]
    last_names = [
        "Brown", "Johnson", "Lee", "Martinez", "Khan", "Wilson", "Davis",
        "Taylor", "Moore", "Clark", "Allen", "Young", "Wright", "Scott"
    ]
    application_statuses = ["Approved", "Approved", "Approved", "Pending", "Denied"]
    source_platforms = ["Apartments.com", "Zillow", "Airbnb", "Referral", "StreetEasy"]

    start_move_in = pd.Timestamp("2023-01-01")
    end_move_in = pd.Timestamp("2025-12-31")

    rows = []
    for tenant_id in range(1001, 1001 + num_tenants):
        full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        app_status = random.choice(application_statuses)

        move_in_date = pd.NaT
        if app_status == "Approved":
            move_in_date = random_date_between(start_move_in, end_move_in)

        rows.append(
            {
                "tenant_id": tenant_id,
                "tenant_name": full_name,
                "application_status": app_status,
                "source_platform": random.choice(source_platforms),
                "move_in_date": move_in_date,
            }
        )

    return pd.DataFrame(rows)


# ------------------------------------------------------------
# Lease data
# ------------------------------------------------------------
def generate_lease_data(units_df: pd.DataFrame, tenants_df: pd.DataFrame) -> pd.DataFrame:
    approved_tenants = tenants_df[tenants_df["application_status"] == "Approved"].copy()
    approved_tenants = approved_tenants.sample(frac=1, random_state=SEED).reset_index(drop=True)

    base_rents = {0: 1450, 1: 1800, 2: 2350, 3: 2950}

    lease_rows = []
    used_tenant_ids = set()

    for _, unit in units_df.iterrows():
        available_tenants = approved_tenants[~approved_tenants["tenant_id"].isin(used_tenant_ids)]
        if available_tenants.empty:
            break

        tenant = available_tenants.iloc[0]
        used_tenant_ids.add(tenant["tenant_id"])

        lease_start = tenant["move_in_date"]
        if pd.isna(lease_start):
            lease_start = pd.Timestamp("2024-01-01")

        lease_term_months = random.choice([12, 12, 12, 18, 24])
        lease_end = lease_start + pd.DateOffset(months=lease_term_months) - pd.Timedelta(days=1)

        neighborhood_adjustment = random.randint(-150, 250)
        monthly_rent = base_rents[unit["bedrooms"]] + neighborhood_adjustment

        lease_rows.append(
            {
                "unit_id": unit["unit_id"],
                "tenant_id": tenant["tenant_id"],
                "lease_start": lease_start.normalize(),
                "lease_end": lease_end.normalize(),
                "monthly_rent": monthly_rent,
                "bedrooms": unit["bedrooms"],
            }
        )

    return pd.DataFrame(lease_rows).sort_values(["unit_id"]).reset_index(drop=True)


# ------------------------------------------------------------
# Rent payments
# ------------------------------------------------------------
def generate_rent_payments(lease_df: pd.DataFrame) -> pd.DataFrame:
    months = pd.date_range(start=START_MONTH, periods=NUM_MONTHS, freq="MS")

    payment_rows = []

    for _, lease in lease_df.iterrows():
        for month_start in months:
            lease_start = pd.Timestamp(lease["lease_start"]).replace(day=1)
            lease_end = pd.Timestamp(lease["lease_end"])

            if month_start < lease_start or month_start > lease_end:
                continue

            rent_due = int(lease["monthly_rent"])

            # Realistic payment behavior
            payment_roll = random.random()
            if payment_roll < 0.80:
                rent_paid = rent_due
                payment_status = "Paid"
            elif payment_roll < 0.90:
                reduction = random.randint(50, 250)
                rent_paid = max(0, rent_due - reduction)
                payment_status = "Partial"
            elif payment_roll < 0.97:
                rent_paid = 0
                payment_status = "Late"
            else:
                rent_paid = 0
                payment_status = "Unpaid"

            payment_rows.append(
                {
                    "month": month_start.strftime("%Y-%m-%d"),
                    "unit_id": int(lease["unit_id"]),
                    "tenant_id": int(lease["tenant_id"]),
                    "rent_due": rent_due,
                    "rent_paid": rent_paid,
                    "payment_status": payment_status,
                }
            )

    return pd.DataFrame(payment_rows).sort_values(["month", "unit_id"]).reset_index(drop=True)


# ------------------------------------------------------------
# Expenses
# ------------------------------------------------------------
def generate_expenses() -> pd.DataFrame:
    categories_and_vendors = {
        "Utilities": ["ConEdison", "National Grid", "Veolia Water"],
        "Repairs": ["FixRight Services", "Urban Repair Co", "QuickPatch LLC"],
        "Renovation": ["Metro Renovations", "Prime Build Group", "NYHandyman LLC"],
        "Maintenance": ["Clean Sweep", "All Seasons Maintenance", "Building Care Inc"],
    }

    start_date = pd.Timestamp(START_MONTH)
    end_date = start_date + pd.DateOffset(months=NUM_MONTHS) - pd.Timedelta(days=1)

    expense_rows = []

    for _ in range(160):
        category = random.choice(list(categories_and_vendors.keys()))
        vendor = random.choice(categories_and_vendors[category])
        date_value = random_date_between(start_date, end_date)

        if category == "Utilities":
            amount = random.randint(150, 700)
        elif category == "Repairs":
            amount = random.randint(200, 2500)
        elif category == "Maintenance":
            amount = random.randint(120, 1200)
        else:  # Renovation
            amount = random.randint(1000, 9000)

        expense_rows.append(
            {
                "date": date_value.strftime("%Y-%m-%d"),
                "category": category,
                "vendor": vendor,
                "amount": amount,
            }
        )

    return pd.DataFrame(expense_rows).sort_values("date").reset_index(drop=True)


# ------------------------------------------------------------
# Comparable rents
# ------------------------------------------------------------
def generate_comparable_rents(units_df: pd.DataFrame) -> pd.DataFrame:
    neighborhoods = sorted(units_df["neighborhood"].unique().tolist())

    rows = []
    for _ in range(80):
        bedrooms = random.choice([0, 1, 1, 2, 2, 3])
        neighborhood = random.choice(neighborhoods)

        base_sqft = {
            0: random.randint(350, 550),
            1: random.randint(500, 750),
            2: random.randint(700, 1050),
            3: random.randint(950, 1400),
        }[bedrooms]

        base_rent = {
            0: random.randint(1400, 1800),
            1: random.randint(1750, 2400),
            2: random.randint(2300, 3200),
            3: random.randint(2900, 4200),
        }[bedrooms]

        rows.append(
            {
                "neighborhood": neighborhood,
                "bedrooms": bedrooms,
                "square_feet": base_sqft,
                "rent_price": base_rent,
            }
        )

    return pd.DataFrame(rows).sort_values(["neighborhood", "bedrooms"]).reset_index(drop=True)


# ------------------------------------------------------------
# Save files
# ------------------------------------------------------------
def save_csv(df: pd.DataFrame, file_name: str) -> None:
    output_path = RAW_DATA_DIR / file_name
    df.to_csv(output_path, index=False)
    print(f"Saved: {output_path} ({len(df):,} rows)")

def main() -> None:
    ensure_output_dir()
    clear_existing_output_files(remove_all_csv=False)
    set_random_seed()

    units_df = generate_units()
    tenant_df = generate_tenant_data()
    lease_df = generate_lease_data(units_df, tenant_df)
    rent_payments_df = generate_rent_payments(lease_df)
    expenses_df = generate_expenses()
    comparable_rents_df = generate_comparable_rents(units_df)

    # Save only the raw files required by the project plan
    save_csv(rent_payments_df, "rent_payments.csv")
    save_csv(lease_df, "lease_data.csv")
    save_csv(expenses_df, "expenses.csv")
    save_csv(comparable_rents_df, "comparable_rents.csv")
    save_csv(
        tenant_df[["tenant_id", "application_status", "source_platform", "move_in_date"]],
        "tenant_data.csv",
    )

    print("\nSynthetic raw data generation complete.")
    print("Files created in: data/raw/")


if __name__ == "__main__":
    main()
