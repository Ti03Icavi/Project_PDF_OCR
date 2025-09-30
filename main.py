import os
import shutil
import pdfplumber
import ocrmypdf
import unicodedata

from modules import monitoramento

PDF_INPUT_DIR = monitoramento.base
PDF_OCR_DIR = "data/processado/"
CSV_OUTPUT_DIR = "data/extraido/"
RELATORIO_SISTEMA = "data/extraido/relatorio_sistema.csv"
LOG_DIR = r"C:\pdf_ocr_project\data\log"
LOG_FILE = os.path.join(LOG_DIR, "erros_ocr.txt")
LOG_CONVERSAO_FILE = os.path.join(LOG_DIR, "status_conversao.txt")

def log_ocr_error(pdf_name, motivo):
    # Garante que o diretório existe antes de gravar o log
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as logf:
            logf.write(f"{pdf_name}: {motivo}\n")
    except Exception as e:
        print(f"Erro ao gravar log em {LOG_FILE}: {e}")

def log_conversao(pdf_name, status, motivo=""):
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_CONVERSAO_FILE, "a", encoding="utf-8") as logf:
        if status == "sucesso":
            logf.write(f"{pdf_name}: sucesso\n")
        else:
            logf.write(f"{pdf_name}: erro - {motivo}\n")

def normaliza_texto(texto):
    """Normaliza texto para garantir apenas caracteres válidos UTF-8 e acentuados."""
    if texto is None:
        return ""
    # Remove caracteres não identificados e normaliza acentuação
    texto = unicodedata.normalize("NFC", texto)
    # Remove caracteres não imprimíveis
    return ''.join(c for c in texto if c.isprintable())

def is_pdf_searchable(pdf_path):
    """Valida se o PDF contém texto pesquisável e exibe o texto extraído."""
    especiais = "áéíóúãõâêôçÁÉÍÓÚÃÕÂÊÔÇ"
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                text = normaliza_texto(text)
                if text and text.strip():
                    print(f"[VALIDAÇÃO] Página {i+1} - Texto encontrado: {text[:100]!r}")
                    encontrados = [c for c in especiais if c in text]
                    if encontrados:
                        print(f"[VALIDAÇÃO] Caracteres especiais encontrados: {encontrados}")
                    else:
                        print("[VALIDAÇÃO] Nenhum caractere especial encontrado no texto extraído.")
                    return True
                else:
                    print(f"[VALIDAÇÃO] Página {i+1} - Nenhum texto encontrado.")
    except Exception as e:
        print(f"Erro ao verificar PDF: {pdf_path} - {e}")
        log_ocr_error(os.path.basename(pdf_path), f"Erro ao verificar PDF: {e}")
    return False

def convert_to_searchable_pdf(pdf_in, pdf_out):
    """Converte PDF imagem para PDF pesquisável usando ocrmypdf."""
    try:
        print(f"[OCR] Iniciando conversão: {pdf_in}")
        ocrmypdf.ocr(pdf_in, pdf_out, deskew=True, progress_bar=False, language="por")
        print(f"OCR concluído: {pdf_out}")
        # Verifica se o PDF gerado está marcado como inválido pelo ocrmypdf
        if os.path.exists(pdf_out):
            with open(pdf_out, "rb") as f:
                pdf_bytes = f.read(2048)
                if b"PDF is INVALID" in pdf_bytes or b"Output file: The generated PDF is INVALID" in pdf_bytes:
                    print(f"⚠️ PDF '{pdf_out}' gerado como INVÁLIDO pelo OCR!")
                    log_ocr_error(os.path.basename(pdf_in), "PDF gerado como INVÁLIDO pelo OCR (imagem truncada ou corrompida)")
    except Exception as e:
        print(f"Erro na conversão OCR do arquivo '{pdf_in}': {e}")
        log_ocr_error(os.path.basename(pdf_in), f"Erro na conversão OCR: {e}")

def is_pdf_valid(pdf_path):
    """Verifica se o PDF pode ser aberto e lido após o OCR."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            _ = len(pdf.pages)
        return True
    except Exception as e:
        print(f"PDF inválido ou corrompido: {pdf_path} - {e}")
        log_ocr_error(os.path.basename(pdf_path), f"PDF inválido ou corrompido: {e}")
        return False

def is_pdf_truncada(pdf_path):
    """Verifica se há erro de imagem truncada no PDF OCR gerado."""
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read(4096)
            if b"truncated" in pdf_bytes or b"invalid jpeg data" in pdf_bytes or b"PDF is INVALID" in pdf_bytes:
                return True
    except Exception as e:
        log_ocr_error(os.path.basename(pdf_path), f"Erro ao verificar truncamento: {e}")
    return False

def compara_dados(pdf_ocr_path, csv_path):
    """Compara os dados extraídos do CSV com o texto do PDF OCR gerado."""
    try:
        with pdfplumber.open(pdf_ocr_path) as pdf:
            texto_pdf = " ".join([page.extract_text() or "" for page in pdf.pages])
        with open(csv_path, encoding="utf-8") as f:
            texto_csv = f.read()
        if texto_pdf.strip() and texto_csv.strip() and texto_pdf[:100] in texto_csv:
            print(f"[COMPARAÇÃO] Dados extraídos do CSV conferem com o PDF OCR gerado.")
        else:
            print(f"[COMPARAÇÃO] Diferença entre dados extraídos e PDF OCR gerado!")
            log_ocr_error(os.path.basename(pdf_ocr_path), "Diferença entre dados extraídos e PDF OCR gerado")
    except Exception as e:
        print(f"Erro na comparação dos dados: {e}")
        log_ocr_error(os.path.basename(pdf_ocr_path), f"Erro na comparação dos dados: {e}")

def main():
    # Garante que os diretórios de saída existem
    os.makedirs(PDF_OCR_DIR, exist_ok=True)
    os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)

    # Lista e limita aos 10 primeiros PDFs que começam com 'NF' na pasta de entrada
    pdf_files = [f for f in os.listdir(PDF_INPUT_DIR) if f.lower().endswith('.pdf') and f.upper().startswith('NF')][:10]
    for pdf_name in pdf_files:
        pdf_input_path = os.path.join(PDF_INPUT_DIR, pdf_name)
        pdf_ocr_path = os.path.join(PDF_OCR_DIR, pdf_name)
        csv_output_path = os.path.join(CSV_OUTPUT_DIR, pdf_name.replace('.pdf', '.csv'))
        pdf_ocr_for_extract = os.path.join(CSV_OUTPUT_DIR, pdf_name)

        # Verifica se o arquivo de entrada existe
        if not os.path.exists(pdf_input_path):
            print(f"Arquivo de entrada não encontrado: {pdf_input_path}")
            continue

        # Prioriza conversão para PDF pesquisável
        if not os.path.exists(pdf_ocr_path):
            print(f"[1] Convertendo '{pdf_name}' para PDF pesquisável...")
            convert_to_searchable_pdf(pdf_input_path, pdf_ocr_path)
            # Filtro para imagem truncada
            if is_pdf_truncada(pdf_ocr_path):
                print(f"⚠️ PDF '{pdf_ocr_path}' contém imagem truncada ou dados inválidos!")
                log_ocr_error(pdf_name, "PDF contém imagem truncada ou dados inválidos após OCR")
            # Verifica se o PDF convertido é válido
            if not is_pdf_valid(pdf_ocr_path):
                log_ocr_error(pdf_name, "PDF convertido está inválido ou corrompido após OCR")
                log_conversao(pdf_name, "erro", "PDF convertido está inválido ou corrompido após OCR")
                print(f"⚠️ PDF '{pdf_ocr_path}' está inválido ou corrompido após OCR!")
                continue
            # Valida se o PDF convertido é realmente pesquisável
            if is_pdf_searchable(pdf_ocr_path):
                print(f"[VALIDAÇÃO] PDF '{pdf_ocr_path}' contém texto pesquisável.")
                log_conversao(pdf_name, "sucesso")
            else:
                print(f"⚠️ PDF '{pdf_ocr_path}' NÃO contém texto pesquisável após OCR!")
                log_ocr_error(pdf_name, "PDF convertido não contém texto pesquisável (qualidade ruim ou truncado)")
                log_conversao(pdf_name, "erro", "PDF convertido não contém texto pesquisável (qualidade ruim ou truncado)")
        else:
            print(f"[1] PDF '{pdf_name}' já convertido para pesquisável.")
            log_conversao(pdf_name, "sucesso")

        # Garante que o PDF OCR está na pasta extraido para extração
        if not os.path.exists(pdf_ocr_for_extract):
            shutil.copy2(pdf_ocr_path, pdf_ocr_for_extract)

        # Só extrai se ainda não existe na pasta extraido
        if not os.path.exists(csv_output_path):
            print(f"[2] Extraindo dados do PDF '{pdf_name}'...")
            from modules import extractor
            extractor.extract_to_csv(pdf_ocr_for_extract, csv_output_path)
        else:
            print(f"[2] Dados do PDF '{pdf_name}' já extraídos.")

        # Compara os dados extraídos com o PDF OCR gerado
        compara_dados(pdf_ocr_path, csv_output_path)

    print("✅ Processo finalizado!")

    # Verifica se o arquivo de comparação existe
    if not os.path.exists(RELATORIO_SISTEMA):
        print(f"Arquivo de comparação não encontrado: {RELATORIO_SISTEMA}")
        with open(RELATORIO_SISTEMA, "w", encoding="utf-8") as f:
            f.write("pagina,texto\n")  # Cabeçalho exemplo

if __name__ == "__main__":
    main()
