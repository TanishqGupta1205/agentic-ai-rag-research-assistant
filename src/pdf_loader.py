from PyPDF2 import PdfReader


def extract_text_from_pdf(pdf_path):
    pdf = PdfReader(pdf_path)

    pages = []

    for page_number, page in enumerate(pdf.pages, start=1):
        text = page.extract_text()

        if text:
            pages.append({
                "text": text,
                "page": page_number
            })

    return pages