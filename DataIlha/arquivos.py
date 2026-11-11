import pandas as pd

# Ajuste sep/encoding se der erro (tentem sep=";" e encoding="latin-1")
df = pd.read_csv("Novo_Caged_MOV_Limpo.csv", nrows=200)
df.to_csv("amostra_200.csv", index=False)
with open("estrutura.txt", "w", encoding="utf-8") as f:
    f.write(str(df.dtypes) + "\n\n" + str(df.head(10).to_string()))