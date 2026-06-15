"""Merge digital-index and financial data into a firm-year panel."""

import pandas as pd


KEY_COLUMNS = ["firm_id", "year"]


def standardize_panel_keys(data: pd.DataFrame) -> pd.DataFrame:
    """Standardize firm identifiers and years without changing other columns."""
    missing = sorted(set(KEY_COLUMNS) - set(data.columns))
    if missing:
        raise KeyError(f"Missing panel keys: {missing}")

    result = data.copy()
    result["firm_id"] = result["firm_id"].astype("string").str.strip()
    result["year"] = pd.to_numeric(result["year"], errors="raise").astype(int)
    return result


def assert_unique_firm_year(data: pd.DataFrame, table_name: str) -> None:
    """Stop the merge when duplicate firm-year observations are present."""
    duplicates = data.duplicated(KEY_COLUMNS, keep=False)
    if duplicates.any():
        duplicate_count = int(duplicates.sum())
        raise ValueError(
            f"{table_name} contains {duplicate_count} rows with duplicate "
            "firm_id-year keys."
        )


def merge_panel_data(
    digital_data: pd.DataFrame,
    financial_data: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Inner-merge two tables and return both the panel and a merge diagnostic."""
    digital = standardize_panel_keys(digital_data)
    financial = standardize_panel_keys(financial_data)
    assert_unique_firm_year(digital, "digital_data")
    assert_unique_firm_year(financial, "financial_data")

    diagnostic = digital[KEY_COLUMNS].merge(
        financial[KEY_COLUMNS],
        on=KEY_COLUMNS,
        how="outer",
        indicator=True,
    )
    panel = digital.merge(
        financial,
        on=KEY_COLUMNS,
        how="inner",
        validate="one_to_one",
    )
    return panel.sort_values(KEY_COLUMNS).reset_index(drop=True), diagnostic


def main() -> None:
    print("Panel merge functions are ready.")
    print("No data was loaded, merged, or written.")


if __name__ == "__main__":
    main()

