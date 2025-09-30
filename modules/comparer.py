import pandas as pd

def compare_with_system(extracted_csv, system_csv):
    try:
        df_extracted = pd.read_csv(extracted_csv)
        df_system = pd.read_csv(system_csv)

        # Exemplo simples: verificar linhas iguais
        diffs = df_extracted[~df_extracted.isin(df_system.to_dict(orient="list")).all(axis=1)]

        if not diffs.empty:
            print("⚠️ Diferenças encontradas:")
            print(diffs)
        else:
            print("✅ Nenhuma diferença encontrada.")
    except Exception as e:
        print(f"Erro na comparação: {e}")
