from pypdf import PdfReader


def extract_text(pdf_path):
    reader = PdfReader(pdf_path)

    # Some PDFs return None for page.extract_text(); keep it robust.
    parts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text:
            parts.append(page_text)

    return "\n".join(parts)
