"""Functions for extracting text from locally supplied annual-report PDFs."""

from pathlib import Path

import pdfplumber


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract page text from one PDF.

    Scanned PDFs may return little or no text and require a separate,
    carefully reviewed OCR workflow that is outside this first-stage template.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
        raise FileNotFoundError(f"Valid PDF not found: {pdf_path}")

    page_texts: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                page_texts.append(f"\n--- PAGE {page_number} ---\n{text}")

    return "".join(page_texts).strip()


def save_extracted_text(text: str, output_path: Path) -> None:
    """Save extracted text only inside a local, git-ignored data directory."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def main() -> None:
    print("This script provides extraction functions only.")
    print("It does not open a real report path or create extracted text by default.")


if __name__ == "__main__":
    main()

