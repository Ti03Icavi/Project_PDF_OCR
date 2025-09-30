import os
import pdfplumber
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from . import ocr

def has_text(pdf_path):
    """Verifica se o PDF já tem texto pesquisável"""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                return True
    return False

def check_pdf_and_process(pdf_in, pdf_out):
    """Decide se aplica OCR ou não usando um agente de IA"""
    print(f"[AGENTE] Inicializando IA para decisão do arquivo: {pdf_in}")
    llm = ChatOpenAI(model="gpt-4o-mini")

    prompt = ChatPromptTemplate.from_template("""
    Você é um agente que decide se um PDF precisa de OCR.
    O PDF já possui texto pesquisável? Responda apenas 'SIM' ou 'NÃO':
    Texto detectado no PDF: {has_text}
    """)

    text_detected = has_text(pdf_in)
    print(f"[AGENTE] Texto detectado: {text_detected}")

    chain = prompt | llm
    print("[AGENTE] Enviando prompt para IA...")
    decision = chain.invoke({"has_text": text_detected})
    print(f"[AGENTE] Resposta da IA: {decision.content}")

    if "NÃO" in str(decision.content).upper():
        print("🔎 PDF não possui texto → aplicando OCR...")
        ocr.to_searchable_pdf(pdf_in, pdf_out)
        # Verifica se o PDF OCR gerado é pesquisável
        try:
            with pdfplumber.open(pdf_out) as pdf:
                has_searchable_text = any(page.extract_text() for page in pdf.pages)
            if has_searchable_text:
                print(f"OCR concluído e texto pesquisável detectado: {pdf_out}")
            else:
                print(f"⚠️ OCR concluído, mas o PDF '{pdf_out}' ainda não contém texto pesquisável!")
        except Exception as e:
            print(f"Erro ao verificar PDF OCR: {e}")
        return pdf_out
    else:
        print("📄 PDF já possui texto → OCR não necessário.")
        return pdf_in
        print("📄 PDF já possui texto → OCR não necessário.")
        return pdf_in
