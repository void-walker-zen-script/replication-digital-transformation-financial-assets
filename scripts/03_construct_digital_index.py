"""Construct digital from real annual-report text files.

The script never creates sample text or placeholder index values. Expected
filenames are firm_id_year.txt or firm_id_year_annual_report.txt.
"""

from __future__ import annotations

import math
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEXT_DIR = PROJECT_ROOT / "data" / "interim" / "annual_report_text"
OUTPUT_PATH = PROJECT_ROOT / "data" / "interim" / "digital_index.csv"

DIGITAL_KEYWORDS = [
    "数字化",
    "数字经济",
    "大数据",
    "云计算",
    "人工智能",
    "区块链",
    "物联网",
    "智能制造",
    "工业互联网",
    "数据中台",
    "数字平台",
    "信息系统",
    "ERP",
    "RPA",
    "金融科技",
    "数字金融",
    "移动支付",
    "电子商务",
    "智能物流",
    "数据挖掘",
    "数据管理",
    "数据中心",
]

FILENAME_PATTERN = re.compile(
    r"^(?P<firm_id>.+?)_(?P<year>\d{4})(?:_annual_report)?\.txt$",
    flags=re.IGNORECASE,
)


def parse_firm_year(path: Path) -> tuple[str, int]:
    """Read firm_id and year from an expected text filename."""
    match = FILENAME_PATTERN.match(path.name)
    if not match:
        raise ValueError(
            f"Cannot parse firm_id and year from '{path.name}'. Expected "
            "firm_id_year.txt or firm_id_year_annual_report.txt."
        )
    return match.group("firm_id").strip(), int(match.group("year"))


def read_report_text(path: Path) -> str:
    """Read one UTF-8 text file and explain encoding failures."""
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError(
            f"Cannot decode '{path.name}' as UTF-8. Convert the extracted "
            "text to UTF-8 before running this script."
        ) from error


def count_keywords(text: str) -> dict[str, int]:
    """Count non-overlapping exact occurrences of every dictionary term."""
    normalized = re.sub(r"\s+", "", text).upper()
    return {
        keyword: normalized.count(keyword.upper())
        for keyword in DIGITAL_KEYWORDS
    }


def construct_record(path: Path) -> dict[str, object]:
    """Construct one auditable firm-year keyword-count record."""
    firm_id, year = parse_firm_year(path)
    text = read_report_text(path)
    counts = count_keywords(text)
    total_count = sum(counts.values())

    record: dict[str, object] = {
        "firm_id": firm_id,
        "year": year,
        "digital_keyword_count": total_count,
        "digital": math.log1p(total_count),
        "source_text_file": path.name,
    }
    record.update({f"count_{keyword}": count for keyword, count in counts.items()})
    return record


def main() -> None:
    """Validate real text inputs, construct digital, and save the result."""
    if not TEXT_DIR.is_dir():
        raise SystemExit(
            "Annual-report text directory not found:\n"
            f"  {TEXT_DIR}\n"
            "Prepare real extracted text files first. No fake text or digital "
            "values were created."
        )

    text_files = sorted(TEXT_DIR.glob("*.txt"))
    if not text_files:
        raise SystemExit(
            "No annual-report text files were found in:\n"
            f"  {TEXT_DIR}\n"
            "Expected firm_id_year.txt or firm_id_year_annual_report.txt. "
            "No fake text or digital values were created."
        )

    try:
        import pandas as pd
    except ModuleNotFoundError as error:
        raise SystemExit(
            "The required package 'pandas' is not installed. Run:\n"
            "  python -m pip install -r requirements.txt"
        ) from error

    try:
        records = [construct_record(path) for path in text_files]
        result = pd.DataFrame(records)
        if result.duplicated(["firm_id", "year"]).any():
            duplicates = result.loc[
                result.duplicated(["firm_id", "year"], keep=False),
                ["firm_id", "year", "source_text_file"],
            ]
            raise ValueError(
                "Duplicate firm_id-year text files found:\n"
                + duplicates.to_string(index=False)
            )
    except ValueError as error:
        raise SystemExit(f"Cannot construct digital: {error}") from error

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.sort_values(["firm_id", "year"]).to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )
    print(f"Constructed digital for {len(result)} real firm-year text file(s).")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

