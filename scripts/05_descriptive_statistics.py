"""Generate the descriptive statistics used to replicate Table 2.

The script reads a locally prepared firm-year panel. It never creates sample
data. If the input file or required columns are missing, it stops with a clear
message so that data problems can be corrected before statistics are reported.
"""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "panel_for_replication.csv"
OUTPUT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "table2_descriptive_statistics.csv"
)

REQUIRED_COLUMNS = [
    "firm_id",
    "year",
    "fin1",
    "fin2",
    "digital",
    "Size",
    "LEV",
    "ROA",
    "ListAge",
    "TOP1",
    "Indep",
]

# Keep this order consistent with the original Table 2 replication target.
TABLE2_VARIABLES = [
    "fin1",
    "fin2",
    "digital",
    "Size",
    "LEV",
    "ROA",
    "ListAge",
    "TOP1",
    "Indep",
]


def check_required_columns(data: "pd.DataFrame") -> None:
    """Raise an informative error listing every missing field."""
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError("Missing required variables: " + ", ".join(missing))


def prepare_numeric_variables(data: "pd.DataFrame") -> "pd.DataFrame":
    """Convert Table 2 variables to numeric values and reject invalid text.

    Empty cells remain missing. Non-empty values that cannot be interpreted as
    numbers trigger an error instead of being silently removed from the sample.
    """
    import pandas as pd

    numeric_data = pd.DataFrame(index=data.index)

    for variable in TABLE2_VARIABLES:
        original = data[variable]
        converted = pd.to_numeric(original, errors="coerce")
        invalid = original.notna() & converted.isna()

        if invalid.any():
            invalid_count = int(invalid.sum())
            raise ValueError(
                f"Variable '{variable}' contains {invalid_count} non-numeric "
                "value(s). Please clean the source data before continuing."
            )

        numeric_data[variable] = converted

    return numeric_data


def calculate_descriptive_statistics(data: "pd.DataFrame") -> "pd.DataFrame":
    """Calculate N, mean, sample standard deviation, minimum, and maximum."""
    numeric_data = prepare_numeric_variables(data)

    statistics = numeric_data.agg(["count", "mean", "std", "min", "max"]).T
    statistics = statistics.rename(columns={"count": "N", "std": "sd"})
    statistics.index.name = "variable"

    # N is a count and should be displayed as an integer.
    statistics["N"] = statistics["N"].astype(int)
    statistics[["mean", "sd", "min", "max"]] = statistics[
        ["mean", "sd", "min", "max"]
    ].round(4)
    return statistics[["N", "mean", "sd", "min", "max"]]


def main() -> None:
    """Read the local panel, calculate Table 2, print it, and save it."""
    if not INPUT_PATH.is_file():
        raise SystemExit(
            "Input data file not found:\n"
            f"  {INPUT_PATH}\n"
            "Please prepare the real replication panel at this path. "
            "No fake data or placeholder results were created."
        )

    try:
        import pandas as pd
    except ModuleNotFoundError as error:
        raise SystemExit(
            "The required package 'pandas' is not installed. "
            "Install project dependencies with:\n"
            "  python -m pip install -r requirements.txt"
        ) from error

    data = pd.read_csv(INPUT_PATH, low_memory=False)

    try:
        check_required_columns(data)
        table2 = calculate_descriptive_statistics(data)
    except ValueError as error:
        raise SystemExit(f"Cannot generate Table 2: {error}") from error

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    table2.to_csv(OUTPUT_PATH, encoding="utf-8-sig")

    print("Table 2 descriptive statistics")
    print("=" * 30)
    print(table2.to_string())
    print(f"\nSaved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
