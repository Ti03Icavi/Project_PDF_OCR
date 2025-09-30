import pdfplumber
import csv

def extract_to_csv(pdf_path, csv_path):
    """Extrai texto do PDF e salva em CSV, respeitando caracteres especiais."""
    try:
        with pdfplumber.open(pdf_path) as pdf, open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["pagina", "texto"])
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                writer.writerow([i+1, text if text else ""])
        print(f"Dados extraídos para: {csv_path}")
    except Exception as e:
        print(f"Erro na extração para CSV: {e}")
    print(f"Dados extraídos para: {csv_path}")
