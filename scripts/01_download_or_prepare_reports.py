"""Prepare a local annual-report file inventory.

This module intentionally does not crawl or download from any website.
Researchers should obtain reports lawfully and place them in the ignored
data/raw/annual_reports directory.
"""

from pathlib import Path


def expected_report_name(firm_id: str, year: int) -> str:
    """Return the recommended, auditable PDF filename."""
    clean_firm_id = str(firm_id).strip()
    if not clean_firm_id:
        raise ValueError("firm_id cannot be empty.")
    if year < 1900 or year > 2100:
        raise ValueError("year does not look valid.")
    return f"{clean_firm_id}_{year}_annual_report.pdf"


def list_local_reports(report_dir: Path) -> list[Path]:
    """List locally supplied PDF reports without changing any files."""
    report_dir = Path(report_dir)
    if not report_dir.exists():
        raise FileNotFoundError(
            f"Report directory does not exist: {report_dir}. "
            "Create it locally and add legally obtained annual reports."
        )
    return sorted(path for path in report_dir.glob("*.pdf") if path.is_file())


def validate_filename(report_path: Path) -> bool:
    """Check whether a report follows firm_id_year_annual_report.pdf."""
    name = Path(report_path).stem
    parts = name.rsplit("_", maxsplit=3)
    return (
        len(parts) == 4
        and bool(parts[0])
        and parts[1].isdigit()
        and parts[2:] == ["annual", "report"]
    )


def main() -> None:
    print("No reports were downloaded.")
    print("Place legally obtained PDFs in data/raw/annual_reports/.")
    print("Recommended filename: firm_id_year_annual_report.pdf")


if __name__ == "__main__":
    main()

