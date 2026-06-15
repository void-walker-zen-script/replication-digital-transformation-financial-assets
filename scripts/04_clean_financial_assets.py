"""Clean financial data and construct financial-asset ratios.

The account lists below are placeholders. Replace them only after checking the
paper's definitions, database documentation, and accounting-standard changes.
"""

from collections.abc import Sequence

import numpy as np
import pandas as pd


IDENTIFIER_COLUMNS = ["firm_id", "year"]

# Candidate mappings only; they are not asserted to be the paper's exact scope.
SHORT_TERM_ASSET_COLUMNS = [
    "trading_financial_assets",
    "derivative_financial_assets_current",
    "other_current_financial_assets",
]
LONG_TERM_ASSET_COLUMNS = [
    "debt_investments",
    "other_debt_investments",
    "other_equity_instrument_investments",
    "other_noncurrent_financial_assets",
]


def require_columns(data: pd.DataFrame, columns: Sequence[str]) -> None:
    """Raise a clear error when required source fields are absent."""
    missing = sorted(set(columns) - set(data.columns))
    if missing:
        raise KeyError(f"Missing required columns: {missing}")


def row_sum_with_missing_check(
    data: pd.DataFrame,
    columns: Sequence[str],
) -> pd.Series:
    """Sum selected accounts while preserving rows where every value is missing."""
    return data[list(columns)].sum(axis=1, min_count=1)


def construct_financial_asset_ratios(
    data: pd.DataFrame,
    short_columns: Sequence[str] = SHORT_TERM_ASSET_COLUMNS,
    long_columns: Sequence[str] = LONG_TERM_ASSET_COLUMNS,
) -> pd.DataFrame:
    """Create short-, long-, and total-financial-asset ratios.

    The function does not winsorize or impute observations. Those choices must
    be documented after the original paper's treatment is confirmed.
    """
    required = [*IDENTIFIER_COLUMNS, "total_assets", *short_columns, *long_columns]
    require_columns(data, required)

    cleaned = data.copy()
    numeric_columns = ["total_assets", *short_columns, *long_columns]
    cleaned[numeric_columns] = cleaned[numeric_columns].apply(
        pd.to_numeric, errors="coerce"
    )

    cleaned["short_financial_assets"] = row_sum_with_missing_check(
        cleaned, short_columns
    )
    cleaned["long_financial_assets"] = row_sum_with_missing_check(
        cleaned, long_columns
    )
    cleaned["financial_assets"] = (
        cleaned["short_financial_assets"] + cleaned["long_financial_assets"]
    )

    valid_assets = cleaned["total_assets"].where(cleaned["total_assets"] > 0)
    cleaned["short_fin_assets_ratio"] = (
        cleaned["short_financial_assets"] / valid_assets
    )
    cleaned["long_fin_assets_ratio"] = (
        cleaned["long_financial_assets"] / valid_assets
    )
    cleaned["financial_assets_ratio"] = cleaned["financial_assets"] / valid_assets

    ratio_columns = [
        "financial_assets_ratio",
        "short_fin_assets_ratio",
        "long_fin_assets_ratio",
    ]
    cleaned[ratio_columns] = cleaned[ratio_columns].replace(
        [np.inf, -np.inf], np.nan
    )
    return cleaned


def main() -> None:
    print("Financial-asset cleaning functions are ready.")
    print("No source data was loaded and no ratios were generated.")


if __name__ == "__main__":
    main()

