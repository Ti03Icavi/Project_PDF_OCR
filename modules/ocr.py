import ocrmypdf

def to_searchable_pdf(pdf_in, pdf_out):
    """
    Converte PDF de imagem em PDF pesquisável usando OCR.
    """
    try:
        ocrmypdf.ocr(pdf_in, pdf_out, deskew=True, progress_bar=False)
    except Exception as e:
        print(f"Erro no OCR: {e}")
