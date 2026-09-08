"""Construct control variables from real financial and governance data."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "financial_data"
    / "control_variables.csv"
)
OUTPUT_PATH = PROJECT_ROOT / "data" / "interim" / "control_variables.csv"

KEY_COLUMNS = ["firm_id", "year"]
SOURCE_COLUMNS = [
    "total_assets",
    "total_liabilities",
    "net_profit",
    "listing_year",
    "tobin_q",
    "largest_shareholder_ownership",
    "independent_directors",
    "total_directors",
]
REQUIRED_COLUMNS = [*KEY_COLUMNS, *SOURCE_COLUMNS]


def check_required_columns(data: "pd.DataFrame") -> None:
    """List missing raw fields required by the six control variables."""
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing))


def construct_controls(data: "pd.DataFrame") -> "pd.DataFrame":
    """Construct controls without imputing missing source values."""
    import numpy as np
    import pandas as pd

    check_required_columns(data)
    result = data.copy()
    result["firm_id"] = result["firm_id"].astype("string").str.strip()

    for column in ["year", *SOURCE_COLUMNS]:
        original = result[column]
        converted = pd.to_numeric(original, errors="coerce")
        invalid = original.notna() & converted.isna()
        if invalid.any():
            raise ValueError(
                f"Field '{column}' contains {int(invalid.sum())} invalid "
                "non-numeric value(s)."
            )
        result[column] = converted

    if result[REQUIRED_COLUMNS].isna().any(axis=None):
        counts = {
            column: int(result[column].isna().sum())
            for column in REQUIRED_COLUMNS
            if result[column].isna().any()
        }
        raise ValueError(f"Required source fields contain missing values: {counts}")
    if result["firm_id"].eq("").any():
        raise ValueError("firm_id cannot contain empty strings.")
    if result["year"].mod(1).ne(0).any():
        raise ValueError("year must contain integer values.")
    if result["listing_year"].mod(1).ne(0).any():
        raise ValueError("listing_year must contain integer values.")

    result["year"] = result["year"].astype(int)
    result["listing_year"] = result["listing_year"].astype(int)
    if result.duplicated(KEY_COLUMNS).any():
        count = int(result.duplicated(KEY_COLUMNS, keep=False).sum())
        raise ValueError(f"Found {count} rows with duplicate firm_id-year keys.")
    if result["total_assets"].le(0).any():
        raise ValueError("total_assets must be positive.")
    if result["total_directors"].le(0).any():
        raise ValueError("total_directors must be positive.")

    listing_age_years = result["year"] - result["listing_year"] + 1
    if listing_age_years.le(0).any():
        raise ValueError(
            "year - listing_year + 1 must be positive for every observation."
        )

    output = result[KEY_COLUMNS].copy()
    output["Size"] = np.log(result["total_assets"])
    output["LEV"] = result["total_liabilities"] / result["total_assets"]
    output["ROA"] = result["net_profit"] / result["total_assets"]
    output["ListAge"] = np.log(listing_age_years)
    output["TobinQ"] = result["tobin_q"]
    output["TOP1"] = result["largest_shareholder_ownership"]
    output["Indep"] = (
        result["independent_directors"] / result["total_directors"]
    )
    return output


def main() -> None:
    """Validate the real source file, construct controls, and save them."""
    if not INPUT_PATH.is_file():
        raise SystemExit(
            "Control-variable input file not found:\n"
            f"  {INPUT_PATH}\n"
            "Prepare the real source data first. No fake control variables "
            "were created."
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
        output = construct_controls(source)
    except (OSError, UnicodeError, ValueError) as error:
        raise SystemExit(f"Cannot construct control variables: {error}") from error

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output.sort_values(KEY_COLUMNS).to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )
    print(f"Constructed controls for {len(output)} real observation(s).")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
