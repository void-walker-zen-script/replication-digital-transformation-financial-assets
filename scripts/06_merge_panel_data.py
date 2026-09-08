"""Merge real digital, financial-asset, and control-variable datasets."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATHS = {
    "digital": PROJECT_ROOT / "data" / "interim" / "digital_index.csv",
    "financial_assets": (
        PROJECT_ROOT / "data" / "interim" / "financial_assets.csv"
    ),
    "controls": PROJECT_ROOT / "data" / "interim" / "control_variables.csv",
}
OUTPUT_PATH = (
    PROJECT_ROOT / "data" / "processed" / "panel_for_replication.csv"
)

KEY_COLUMNS = ["firm_id", "year"]
REQUIRED_BY_INPUT = {
    "digital": [*KEY_COLUMNS, "digital"],
    "financial_assets": [*KEY_COLUMNS, "fin1", "fin2"],
    "controls": [
        *KEY_COLUMNS,
        "Size",
        "LEV",
        "ROA",
        "ListAge",
        "TobinQ",
        "TOP1",
        "Indep",
    ],
}
FINAL_COLUMNS = [
    "firm_id",
    "year",
    "fin1",
    "fin2",
    "digital",
    "Size",
    "LEV",
    "ROA",
    "ListAge",
    "TobinQ",
    "TOP1",
    "Indep",
]


def validate_input(data: "pd.DataFrame", name: str) -> "pd.DataFrame":
    """Validate required fields, panel keys, and one-row-per-firm-year."""
    import pandas as pd

    required = REQUIRED_BY_INPUT[name]
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing fields: {', '.join(missing)}")

    result = data[required].copy()
    result["firm_id"] = result["firm_id"].astype("string").str.strip()
    original_year = result["year"]
    result["year"] = pd.to_numeric(original_year, errors="coerce")
    invalid_year = original_year.notna() & result["year"].isna()

    if invalid_year.any():
        raise ValueError(
            f"{name}.year contains {int(invalid_year.sum())} invalid value(s)."
        )
    if result[KEY_COLUMNS].isna().any(axis=None):
        raise ValueError(f"{name} contains missing firm_id or year values.")
    if result["firm_id"].eq("").any():
        raise ValueError(f"{name} contains empty firm_id values.")
    if result["year"].mod(1).ne(0).any():
        raise ValueError(f"{name}.year must contain integer values.")

    result["year"] = result["year"].astype(int)
    if result.duplicated(KEY_COLUMNS).any():
        count = int(result.duplicated(KEY_COLUMNS, keep=False).sum())
        raise ValueError(
            f"{name} contains {count} rows with duplicate firm_id-year keys."
        )
    return result


def merge_panel(
    digital: "pd.DataFrame",
    financial_assets: "pd.DataFrame",
    controls: "pd.DataFrame",
) -> "pd.DataFrame":
    """Perform one-to-one inner merges without manufacturing unmatched rows."""
    digital = validate_input(digital, "digital")
    financial_assets = validate_input(financial_assets, "financial_assets")
    controls = validate_input(controls, "controls")

    first = digital.merge(
        financial_assets,
        on=KEY_COLUMNS,
        how="inner",
        validate="one_to_one",
    )
    panel = first.merge(
        controls,
        on=KEY_COLUMNS,
        how="inner",
        validate="one_to_one",
    )

    print(
        "Merge counts: "
        f"digital={len(digital)}, "
        f"financial_assets={len(financial_assets)}, "
        f"controls={len(controls)}, "
        f"digital+financial_assets={len(first)}, "
        f"final={len(panel)}"
    )
    if panel.empty:
        raise ValueError("The three real input files have no matched firm-year rows.")

    missing_final = [
        column for column in FINAL_COLUMNS if column not in panel.columns
    ]
    if missing_final:
        raise ValueError(
            "Final panel is missing fields: " + ", ".join(missing_final)
        )
    return panel[FINAL_COLUMNS].sort_values(KEY_COLUMNS).reset_index(drop=True)


def main() -> None:
    """Read validated inputs, merge them, and save the final real panel."""
    missing_files = [
        str(path) for path in INPUT_PATHS.values() if not path.is_file()
    ]
    if missing_files:
        raise SystemExit(
            "Cannot create panel_for_replication.csv. Missing real input file(s):\n"
            + "\n".join(f"  {path}" for path in missing_files)
            + "\nNo fake panel was created."
        )

    try:
        import pandas as pd
    except ModuleNotFoundError as error:
        raise SystemExit(
            "The required package 'pandas' is not installed. Run:\n"
            "  python -m pip install -r requirements.txt"
        ) from error

    try:
        datasets = {
            name: pd.read_csv(path, dtype={"firm_id": "string"})
            for name, path in INPUT_PATHS.items()
        }
        panel = merge_panel(
            datasets["digital"],
            datasets["financial_assets"],
            datasets["controls"],
        )
    except (OSError, UnicodeError, ValueError) as error:
        raise SystemExit(f"Cannot merge replication panel: {error}") from error

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Created panel from {len(panel)} matched real observation(s).")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
