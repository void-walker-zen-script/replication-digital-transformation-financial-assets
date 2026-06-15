"""Check whether the packages required by this replication project are installed."""

from importlib.util import find_spec


REQUIRED_PACKAGES = [
    "pandas",
    "numpy",
    "statsmodels",
    "linearmodels",
    "openpyxl",
    "pdfplumber",
    "jieba",
]


def check_packages(package_names: list[str]) -> dict[str, bool]:
    """Return an installation-status dictionary without importing packages."""
    return {name: find_spec(name) is not None for name in package_names}


def main() -> None:
    """Print a readable environment report."""
    status = check_packages(REQUIRED_PACKAGES)

    print("Replication project environment check")
    print("=" * 37)
    for package, installed in status.items():
        label = "OK" if installed else "MISSING"
        print(f"{package:<15} {label}")

    missing = [name for name, installed in status.items() if not installed]
    if missing:
        print("\nMissing packages:", ", ".join(missing))
        print("Install them with: python -m pip install -r requirements.txt")
        raise SystemExit(1)

    print("\nAll required packages are installed.")


if __name__ == "__main__":
    main()

