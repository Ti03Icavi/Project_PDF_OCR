import os
import datetime
import time
import locale

# Define o locale para português (ajuste conforme seu sistema)
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')  # Linux/macOS
except:
    locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')  # Windows

# Caminho base
BASE_DIR = r"I:\Recepcao\Recep01\Meu Scanner\DIGITALIZAÇÃO "

def obter_caminho_dia_atual():
    hoje = datetime.datetime.now()
    ano = str(hoje.year)
    mes = f"{hoje.month:02d}. {hoje.strftime('%B')}"  # Ex: "09. setembro"
    dia = f"{hoje.day:02d}.{hoje.month:02d}"           # Ex: "29.09"
    caminho = os.path.join(BASE_DIR ano, "Scaner de Notas", mes, dia)
    return caminho

def verificar_arquivos(caminho, arquivos_anteriores):
    if os.path.exists(caminho):
        arquivos = os.listdir(caminho)
        novos_arquivos = [f for f in arquivos if f not in arquivos_anteriores]
        if novos_arquivos:
            print(f"📂 Novos arquivos encontrados em: {caminho}")
            for arquivo in novos_arquivos:
                print(f" - {arquivo}")
            return arquivos
        else:
            print(f"⏳ Nenhum novo arquivo em: {caminho}")
            return arquivos_anteriores
    else:
        print(f"❌ Pasta não encontrada: {caminho}")
        return arquivos_anteriores

def monitorar_pastas(intervalo_segundos=60):
    caminho_atual = ""
    arquivos_anteriores = []
    while True:
        novo_caminho = obter_caminho_dia_atual()
        if novo_caminho != caminho_atual:
            print(f"\n📅 Mudança detectada. Nova pasta do dia: {novo_caminho}")
            caminho_atual = novo_caminho
            arquivos_anteriores = []

        arquivos_anteriores = verificar_arquivos(caminho_atual, arquivos_anteriores)
        time.sleep(intervalo_segundos)

if __name__ == "__main__":
    monitorar_pastas()
