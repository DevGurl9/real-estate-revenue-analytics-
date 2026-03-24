from __future__ import annotations

import pandas as pd

from extract_data import (
    extract_rent_payments,
    extract_lease_data,
    extract_expenses,
    extract_comparable_rents,
    extract_tenant_data,
)


def clean_rent_payments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean rent payments data:
    - convert dates
    - standardize text
    - ensure numeric columns
    - calculate unpaid balance
    """
    df = df.copy()

    df["month"] = pd.to_datetime(df["month"], errors="coerce")
    df["unit_id"] = pd.to_numeric(df["unit_id"], errors="coerce")
    df["tenant_id"] = pd.to_numeric(df["tenant_id"], errors="coerce")
    df["rent_due"] = pd.to_numeric(df["rent_due"], errors="coerce").fillna(0)
    df["rent_paid"] = pd.to_numeric(df["rent_paid"], errors="coerce").fillna(0)
    df["payment_status"] = df["payment_status"].astype(str).str.strip().str.title()

    df["unpaid_balance"] = df["rent_due"] - df["rent_paid"]
    df["collection_rate"] = df["rent_paid"] / df["rent_due"]
    df["collection_rate"] = df["collection_rate"].fillna(0)

    return df


def clean_lease_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean lease data:
    - convert dates
    - enforce numeric fields
    - create lease month fields
    """
    df = df.copy()

    df["lease_start"] = pd.to_datetime(df["lease_start"], errors="coerce")
    df["lease_end"] = pd.to_datetime(df["lease_end"], errors="coerce")
    df["unit_id"] = pd.to_numeric(df["unit_id"], errors="coerce")
    df["tenant_id"] = pd.to_numeric(df["tenant_id"], errors="coerce")
    df["monthly_rent"] = pd.to_numeric(df["monthly_rent"], errors="coerce")
    df["bedrooms"] = pd.to_numeric(df["bedrooms"], errors="coerce")

    df["lease_start_month"] = df["lease_start"].dt.to_period("M").astype(str)
    df["lease_end_month"] = df["lease_end"].dt.to_period("M").astype(str)

    return df


def clean_expenses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean expense data:
    - convert dates
    - standardize text
    - ensure numeric amounts
    """
    df = df.copy()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["category"] = df["category"].astype(str).str.strip().str.title()
    df["vendor"] = df["vendor"].astype(str).str.strip()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    df["expense_month"] = df["date"].dt.to_period("M").astype(str)

    return df


def clean_comparable_rents(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean comparable rent data.
    """
    df = df.copy()

    df["neighborhood"] = df["neighborhood"].astype(str).str.strip()
    df["bedrooms"] = pd.to_numeric(df["bedrooms"], errors="coerce")
    df["square_feet"] = pd.to_numeric(df["square_feet"], errors="coerce")
    df["rent_price"] = pd.to_numeric(df["rent_price"], errors="coerce")

    return df


def clean_tenant_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean tenant/application data.
    """
    df = df.copy()

    df["tenant_id"] = pd.to_numeric(df["tenant_id"], errors="coerce")
    df["application_status"] = df["application_status"].astype(str).str.strip().str.title()
    df["source_platform"] = df["source_platform"].astype(str).str.strip()
    df["move_in_date"] = pd.to_datetime(df["move_in_date"], errors="coerce")

    return df


def create_revenue_summary(rent_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create monthly revenue summary:
    - total rent due
    - total rent paid
    - total unpaid balance
    - collection rate
    """
    revenue_summary = (
        rent_df.groupby("month", as_index=False)
        .agg(
            total_rent_due=("rent_due", "sum"),
            total_rent_paid=("rent_paid", "sum"),
            total_unpaid_balance=("unpaid_balance", "sum"),
            paid_records=("payment_status", lambda x: (x == "Paid").sum()),
            late_records=("payment_status", lambda x: (x == "Late").sum()),
            unpaid_records=("payment_status", lambda x: (x == "Unpaid").sum()),
        )
    )

    revenue_summary["monthly_collection_rate"] = (
        revenue_summary["total_rent_paid"] / revenue_summary["total_rent_due"]
    ).fillna(0)

    revenue_summary["month"] = pd.to_datetime(revenue_summary["month"])

    return revenue_summary.sort_values("month").reset_index(drop=True)


def create_expense_summary(expenses_df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize expenses by month and category.
    """
    expense_summary = (
        expenses_df.groupby(["expense_month", "category"], as_index=False)
        .agg(
            total_expense_amount=("amount", "sum"),
            expense_count=("amount", "count"),
        )
        .sort_values(["expense_month", "category"])
        .reset_index(drop=True)
    )

    return expense_summary


def create_occupancy_trends(lease_df: pd.DataFrame, total_units: int | None = None) -> pd.DataFrame:
    """
    Create monthly occupancy trends based on lease periods.

    Assumes each lease row represents one occupied unit during its active months.
    """
    records = []

    if lease_df.empty:
        return pd.DataFrame(
            columns=["month", "occupied_units", "total_units", "occupancy_rate"]
        )

    if total_units is None:
        total_units = int(lease_df["unit_id"].nunique())

    for _, row in lease_df.iterrows():
        if pd.isna(row["lease_start"]) or pd.isna(row["lease_end"]):
            continue

        month_range = pd.period_range(
            start=row["lease_start"].to_period("M"),
            end=row["lease_end"].to_period("M"),
            freq="M",
        )

        for period in month_range:
            records.append(
                {
                    "month": str(period),
                    "unit_id": row["unit_id"],
                }
            )

    occupancy_df = pd.DataFrame(records).drop_duplicates()

    occupancy_summary = (
        occupancy_df.groupby("month", as_index=False)
        .agg(occupied_units=("unit_id", "nunique"))
        .sort_values("month")
        .reset_index(drop=True)
    )

    occupancy_summary["total_units"] = total_units
    occupancy_summary["vacant_units"] = total_units - occupancy_summary["occupied_units"]
    occupancy_summary["occupancy_rate"] = (
        occupancy_summary["occupied_units"] / occupancy_summary["total_units"]
    ).fillna(0)

    return occupancy_summary


def create_pricing_comparison(
    lease_df: pd.DataFrame,
    comparable_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compare actual lease rent to market comparable averages by bedroom count.
    """
    actual_rent = (
        lease_df.groupby("bedrooms", as_index=False)
        .agg(
            avg_actual_rent=("monthly_rent", "mean"),
            lease_count=("unit_id", "count"),
        )
    )

    market_rent = (
        comparable_df.groupby("bedrooms", as_index=False)
        .agg(
            avg_market_rent=("rent_price", "mean"),
            comparable_count=("rent_price", "count"),
        )
    )

    pricing_comparison = actual_rent.merge(
        market_rent,
        on="bedrooms",
        how="outer",
    )

    pricing_comparison["rent_gap"] = (
        pricing_comparison["avg_market_rent"] - pricing_comparison["avg_actual_rent"]
    )

    pricing_comparison["pricing_position"] = pricing_comparison["rent_gap"].apply(
        lambda x: "Below Market"
        if pd.notna(x) and x > 0
        else ("Above Market" if pd.notna(x) and x < 0 else "At Market")
    )

    return pricing_comparison.sort_values("bedrooms").reset_index(drop=True)


def transform_all_data() -> dict[str, pd.DataFrame]:
    """
    Full transformation pipeline:
    1. extract raw data
    2. clean datasets
    3. build analytical outputs
    """
    rent_df = clean_rent_payments(extract_rent_payments())
    lease_df = clean_lease_data(extract_lease_data())
    expenses_df = clean_expenses(extract_expenses())
    comparable_df = clean_comparable_rents(extract_comparable_rents())
    tenant_df = clean_tenant_data(extract_tenant_data())

    revenue_summary = create_revenue_summary(rent_df)
    expense_summary = create_expense_summary(expenses_df)
    occupancy_trends = create_occupancy_trends(lease_df)
    pricing_comparison = create_pricing_comparison(lease_df, comparable_df)

    return {
        "clean_rent_payments": rent_df,
        "clean_lease_data": lease_df,
        "clean_expenses": expenses_df,
        "clean_comparable_rents": comparable_df,
        "clean_tenant_data": tenant_df,
        "revenue_summary": revenue_summary,
        "expense_summary": expense_summary,
        "occupancy_trends": occupancy_trends,
        "pricing_comparison": pricing_comparison,
    }


def main() -> None:
    transformed = transform_all_data()

    print("Transformation complete:\n")
    for name, df in transformed.items():
        print(f"{name}: {df.shape[0]:,} rows x {df.shape[1]} columns")


if __name__ == "__main__":
    main()