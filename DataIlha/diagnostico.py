import pandas as pd
import os

arquivo = "Novo_Caged_MOV_Limpo.csv"

print("ARQUIVO ENCONTRADO:", os.path.exists(arquivo))

df = pd.read_csv(
    arquivo,
    sep=None,
    engine="python",
    encoding="utf-8",
    nrows=5
)

print("\nCOLUNAS DO CAGED:")
print(df.columns.tolist())

print("\nPRIMEIROS REGISTROS:")
print(df.head().to_string())

print("\nCOLUNAS DOS MUNICÍPIOS:")
df_mun = pd.read_csv(
    "Municipios_SC_limpo.csv",
    sep=None,
    engine="python",
    encoding="utf-8",
    nrows=5
)

print(df_mun.columns.tolist())
print(df_mun.head().to_string())