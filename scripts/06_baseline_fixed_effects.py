"""Replicate the two baseline fixed-effects regressions reported in Table 3.

The script only works with a real, locally prepared firm-year panel. It does
not create sample data or insert coefficients from the original paper.
"""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "panel_for_replication.csv"
FULL_OUTPUT_PATH = (
    PROJECT_ROOT / "outputs" / "tables" / "table3_baseline_regression.txt"
)
COEFFICIENT_OUTPUT_PATH = (
    PROJECT_ROOT / "outputs" / "tables" / "table3_baseline_coefficients.csv"
)

DEPENDENT_VARIABLES = ["fin1", "fin2"]
EXPLANATORY_VARIABLES = [
    "digital",
    "Size",
    "LEV",
    "ROA",
    "ListAge",
    "TOP1",
    "Indep",
]
REQUIRED_COLUMNS = ["firm_id", "year", *DEPENDENT_VARIABLES, *EXPLANATORY_VARIABLES]


def check_required_columns(data: "pd.DataFrame") -> None:
    """Stop and list every required variable that is absent."""
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError("Missing required variables: " + ", ".join(missing))


def prepare_regression_panel(data: "pd.DataFrame") -> "pd.DataFrame":
    """Clean regression fields and set the firm-year MultiIndex.

    Non-empty text that cannot be converted to a number is treated as a data
    error rather than being silently discarded. Model-specific missing values
    are removed later, separately for the fin1 and fin2 regressions.
    """
    import pandas as pd

    panel = data[REQUIRED_COLUMNS].copy()
    panel["firm_id"] = panel["firm_id"].astype("string").str.strip()
    panel["firm_id"] = panel["firm_id"].replace("", pd.NA)

    numeric_columns = ["year", *DEPENDENT_VARIABLES, *EXPLANATORY_VARIABLES]
    for variable in numeric_columns:
        original = panel[variable]
        converted = pd.to_numeric(original, errors="coerce")
        invalid = original.notna() & converted.isna()
        if invalid.any():
            raise ValueError(
                f"Variable '{variable}' contains {int(invalid.sum())} "
                "non-numeric value(s)."
            )
        panel[variable] = converted

    # A year must be an integer before it can serve as the time index.
    non_integer_year = panel["year"].notna() & panel["year"].mod(1).ne(0)
    if non_integer_year.any():
        raise ValueError(
            f"year contains {int(non_integer_year.sum())} non-integer value(s)."
        )

    rows_before = len(panel)
    panel = panel.dropna(subset=["firm_id", "year"])
    rows_dropped = rows_before - len(panel)
    if rows_dropped:
        print(
            f"Dropped {rows_dropped} observation(s) with missing panel keys."
        )

    panel["year"] = panel["year"].astype(int)
    if panel.duplicated(["firm_id", "year"]).any():
        duplicate_count = int(
            panel.duplicated(["firm_id", "year"], keep=False).sum()
        )
        raise ValueError(
            f"Found {duplicate_count} row(s) with duplicate firm_id-year keys."
        )

    return panel.set_index(["firm_id", "year"]).sort_index()


def run_fixed_effects_model(panel: "pd.DataFrame", dependent: str):
    """Estimate one firm and year fixed-effects model."""
    from linearmodels.panel import PanelOLS

    model_data = panel[[dependent, *EXPLANATORY_VARIABLES]].dropna()
    if model_data.empty:
        raise ValueError(
            f"No complete observations remain for the {dependent} regression."
        )

    dropped = len(panel) - len(model_data)
    print(
        f"{dependent}: dropped {dropped} observation(s) with missing model "
        f"variables; using {len(model_data)} observation(s)."
    )

    regressors = " + ".join(EXPLANATORY_VARIABLES)
    formula = (
        f"{dependent} ~ 1 + {regressors} + EntityEffects + TimeEffects"
    )
    model = PanelOLS.from_formula(formula, data=model_data, drop_absorbed=True)
    return model.fit(cov_type="clustered", cluster_entity=True)


def significance_stars(p_value: float) -> str:
    """Translate a p-value into conventional significance stars."""
    if p_value < 0.01:
        return "***"
    if p_value < 0.05:
        return "**"
    if p_value < 0.10:
        return "*"
    return ""


def build_coefficient_table(
    fin1_result,
    fin2_result,
) -> "pd.DataFrame":
    """Build the compact side-by-side coefficient and standard-error table."""
    import pandas as pd

    rows: list[dict[str, object]] = []
    for variable in EXPLANATORY_VARIABLES:
        rows.append(
            {
                "variable": variable,
                "fin1_coefficient": fin1_result.params[variable],
                "fin1_standard_error": fin1_result.std_errors[variable],
                "fin1_significance": significance_stars(
                    fin1_result.pvalues[variable]
                ),
                "fin2_coefficient": fin2_result.params[variable],
                "fin2_standard_error": fin2_result.std_errors[variable],
                "fin2_significance": significance_stars(
                    fin2_result.pvalues[variable]
                ),
            }
        )

    table = pd.DataFrame(rows)
    numeric_columns = [
        "fin1_coefficient",
        "fin1_standard_error",
        "fin2_coefficient",
        "fin2_standard_error",
    ]
    table[numeric_columns] = table[numeric_columns].round(6)
    return table


def format_full_results(fin1_result, fin2_result) -> str:
    """Combine the complete linearmodels summaries into one text report."""
    sections = [
        "TABLE 3 BASELINE FIXED-EFFECTS REGRESSIONS",
        "=" * 48,
        "",
        "Model 1: dependent variable = fin1",
        "-" * 36,
        str(fin1_result.summary),
        "",
        "",
        "Model 2: dependent variable = fin2",
        "-" * 36,
        str(fin2_result.summary),
        "",
        "Both models include firm and year fixed effects.",
        "Standard errors are clustered at the firm level.",
    ]
    return "\n".join(sections)


def print_digital_result(dependent: str, result) -> None:
    """Print the coefficient, standard error, p-value, and stars for digital."""
    coefficient = result.params["digital"]
    standard_error = result.std_errors["digital"]
    p_value = result.pvalues["digital"]
    stars = significance_stars(p_value)
    significance = stars if stars else "not significant at the 10% level"

    print(
        f"{dependent}: coefficient={coefficient:.6f}, "
        f"standard error={standard_error:.6f}, "
        f"p-value={p_value:.6f}, significance={significance}"
    )


def main() -> None:
    """Load the real panel, estimate both models, and save Table 3 outputs."""
    if not INPUT_PATH.is_file():
        raise SystemExit(
            "Input data file not found:\n"
            f"  {INPUT_PATH}\n"
            "Please prepare the real panel_for_replication.csv at this path. "
            "No fake data or regression results were created."
        )

    try:
        import pandas as pd
        from linearmodels.panel import PanelOLS  # noqa: F401
    except ModuleNotFoundError as error:
        package = error.name or "a required package"
        raise SystemExit(
            f"The required package '{package}' is not installed. "
            "Install project dependencies with:\n"
            "  python -m pip install -r requirements.txt"
        ) from error

    try:
        data = pd.read_csv(INPUT_PATH, low_memory=False)
        check_required_columns(data)
        panel = prepare_regression_panel(data)
        fin1_result = run_fixed_effects_model(panel, "fin1")
        fin2_result = run_fixed_effects_model(panel, "fin2")
        coefficient_table = build_coefficient_table(fin1_result, fin2_result)
    except (KeyError, TypeError, ValueError) as error:
        raise SystemExit(f"Cannot generate Table 3: {error}") from error

    FULL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    FULL_OUTPUT_PATH.write_text(
        format_full_results(fin1_result, fin2_result),
        encoding="utf-8",
    )
    coefficient_table.to_csv(
        COEFFICIENT_OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print("\nCore digital results")
    print("=" * 20)
    print_digital_result("fin1", fin1_result)
    print_digital_result("fin2", fin2_result)
    print(f"\nFull regression output saved to: {FULL_OUTPUT_PATH}")
    print(f"Coefficient table saved to: {COEFFICIENT_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
