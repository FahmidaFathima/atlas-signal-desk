from pathlib import Path
import pypdf


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract readable text from a PDF document.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.stat().st_size == 0:
        raise ValueError(f"PDF file is empty: {path}")

    reader = pypdf.PdfReader(str(path))

    if not reader.pages:
        raise ValueError("PDF contains no pages.")

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            pages.append(
                f"\n--- PAGE {page_number} ---\n{text.strip()}"
            )

    if not pages:
        raise ValueError(
            "No readable text found. "
            "The PDF may contain scanned images."
        )

    return "\n".join(pages)


def get_pdf_summary_text(text: str, max_characters: int = 30000) -> str:
    """
    Prepare extracted PDF text for the first-pass AI analysis.

    Keeps the document beginning and end so that important
    company information and later risk/disclosure sections
    are both represented.
    """

    if len(text) <= max_characters:
        return text

    half = max_characters // 2

    beginning = text[:half]
    ending = text[-half:]

    return (
        beginning
        + "\n\n[...MIDDLE OF DOCUMENT OMITTED FOR FIRST-PASS ANALYSIS...]\n\n"
        + ending
    )