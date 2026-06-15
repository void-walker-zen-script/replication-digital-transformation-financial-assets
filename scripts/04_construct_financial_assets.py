"""Construct fin1 and fin2 from real financial-statement items."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "financial_data"
    / "financial_statement_items.csv"
)
OUTPUT_PATH = PROJECT_ROOT / "data" / "interim" / "financial_assets.csv"

KEY_COLUMNS = ["firm_id", "year"]
TOTAL_ASSETS = "total_assets"
FIN1_COMPONENTS = [
    "monetary_funds",
    "fair_value_through_profit_or_loss_financial_assets",
]
FIN2_COMPONENTS = [
    "interest_receivable_net",
    "dividend_receivable_net",
    "available_for_sale_financial_assets_net",
    "held_to_maturity_investments_net",
    "long_term_equity_investments_net",
    "investment_property_net",
]
REQUIRED_COLUMNS = [
    *KEY_COLUMNS,
    TOTAL_ASSETS,
    *FIN1_COMPONENTS,
    *FIN2_COMPONENTS,
]


def check_required_columns(data: "pd.DataFrame") -> None:
    """List every missing source field instead of silently substituting zero."""
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing))


def convert_required_numeric(data: "pd.DataFrame") -> "pd.DataFrame":
    """Convert source amounts to numeric and reject invalid non-empty text."""
    import pandas as pd

    result = data.copy()
    for column in ["year", TOTAL_ASSETS, *FIN1_COMPONENTS, *FIN2_COMPONENTS]:
        original = result[column]
        converted = pd.to_numeric(original, errors="coerce")
        invalid = original.notna() & converted.isna()
        if invalid.any():
            raise ValueError(
                f"Field '{column}' contains {int(invalid.sum())} invalid "
                "non-numeric value(s)."
            )
        result[column] = converted
    return result


def construct_financial_assets(data: "pd.DataFrame") -> "pd.DataFrame":
    """Calculate fin1 and fin2 without treating missing components as zero."""
    import pandas as pd

    check_required_columns(data)
    result = convert_required_numeric(data)
    result["firm_id"] = result["firm_id"].astype("string").str.strip()

    if result[KEY_COLUMNS].isna().any(axis=None):
        raise ValueError("firm_id and year cannot contain missing values.")
    if result["firm_id"].eq("").any():
        raise ValueError("firm_id cannot contain empty strings.")
    if result["year"].mod(1).ne(0).any():
        raise ValueError("year must contain integer values.")
    result["year"] = result["year"].astype(int)

    if result.duplicated(KEY_COLUMNS).any():
        count = int(result.duplicated(KEY_COLUMNS, keep=False).sum())
        raise ValueError(f"Found {count} rows with duplicate firm_id-year keys.")
    if result[TOTAL_ASSETS].isna().any():
        raise ValueError("total_assets contains missing values.")
    if result[TOTAL_ASSETS].le(0).any():
        raise ValueError("total_assets must be positive.")

    component_columns = [*FIN1_COMPONENTS, *FIN2_COMPONENTS]
    missing_components = result[component_columns].isna()
    if missing_components.any(axis=None):
        details = {
            column: int(missing_components[column].sum())
            for column in component_columns
            if missing_components[column].any()
        }
        raise ValueError(
            "Financial-asset components contain missing values. Verify whether "
            f"they are true zeros before editing the source: {details}"
        )

    fin1_amount = result[FIN1_COMPONENTS].sum(axis=1)
    fin2_amount = result[FIN2_COMPONENTS].sum(axis=1)
    output = result[KEY_COLUMNS].copy()
    output["fin1"] = fin1_amount / result[TOTAL_ASSETS]
    output["fin2"] = fin2_amount / result[TOTAL_ASSETS]
    return output


def main() -> None:
    """Validate the real source file, construct ratios, and save them."""
    if not INPUT_PATH.is_file():
        raise SystemExit(
            "Financial-statement input file not found:\n"
            f"  {INPUT_PATH}\n"
            "Prepare the real source data first. No fake financial data or "
            "fin1/fin2 values were created."
        )

    try:
        import pandas as pd
    except ModuleNotFoundError as error:
        raise SystemExit(
            "The required package 'pandas' is not installed. Run:\n"
            "  python -m pip install -r requirements.txt"
        ) from error

    try:
        source = pd.read_csv(INPUT_PATH, dtype={"firm_id": "string"})
        output = construct_financial_assets(source)
    except (OSError, UnicodeError, ValueError) as error:
        raise SystemExit(f"Cannot construct fin1 and fin2: {error}") from error

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output.sort_values(KEY_COLUMNS).to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )
    print(f"Constructed fin1 and fin2 for {len(output)} real observation(s).")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

