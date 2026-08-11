from pathlib import Path

from documents.pdf_processor import extract_text_from_pdf


PDF_PATH = Path(__file__).parent / "sample_financial_report.pdf"


def main():
    print("=" * 60)
    print("ATLAS PDF EXTRACTION TEST")
    print("=" * 60)

    try:
        text = extract_text_from_pdf(str(PDF_PATH))

        print(f"PDF: {PDF_PATH.name}")
        print(f"Characters extracted: {len(text)}")
        print()
        print("FIRST 3000 CHARACTERS")
        print("-" * 60)
        print(text[:3000])
        print("-" * 60)
        print("PDF extraction successful.")

    except Exception as error:
        print(f"PDF processing error: {error}")


if __name__ == "__main__":
    main()