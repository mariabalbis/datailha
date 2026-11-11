# ==============================================================================
# DATATHON: RAIO-X DO MERCADO DE TRABALHO E VAGAS INDUSTRIAIS EM SANTA CATARINA
# ==============================================================================

import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

# ------------------------------------------------------------------------------
# ETAPA 1: CARGA DOS DADOS
# ------------------------------------------------------------------------------
print("1/5 | Carregando as bases de dados brutas...")

try:
    df_caged = pd.read_csv("Novo_Caged_MOV_Limpo.csv", sep=";", encoding="utf-8")
except Exception:
    df_caged = pd.read_csv("Novo_Caged_MOV_Limpo.csv", sep=",", encoding="utf-8")

try:
    df_mun = pd.read_csv("Municipios_SC_limpo.csv", sep=";", encoding="utf-8")
except Exception:
    df_mun = pd.read_csv("Municipios_SC_limpo.csv", sep=",", encoding="utf-8")

print(f" -> Registros iniciais do CAGED: {len(df_caged)}")
print(f" -> Registros de Municípios: {len(df_mun)}")

# ------------------------------------------------------------------------------
# ETAPA 2: LIMPEZA E TRATAMENTO
# ------------------------------------------------------------------------------
print("\n2/5 | Aplicando regras de limpeza e filtrando exclusões (EX)...")

# 1. Filtro EX / Exclusões
col_mov = [c for c in df_caged.columns if 'tipomovimentacao' in c.lower() or 'tipo_mov' in c.lower()]
if col_mov:
    linhas_antes = len(df_caged)
    df_caged = df_caged[df_caged[col_mov[0]] != 'EX']
    df_caged = df_caged[df_caged[col_mov[0]] != 97]
    print(f" -> Registros filtrados ('EX'/Exclusões): {linhas_antes - len(df_caged)}")

# 2. Saldo da Movimentação
col_saldo = [c for c in df_caged.columns if 'saldomov' in c.lower() or 'saldo' in c.lower()][0]
df_caged['saldo'] = df_caged[col_saldo].astype(int)

# 3. Tratamento seguro de Salário (trata vírgulas e pontos)
col_salario = [c for c in df_caged.columns if 'salário' in c.lower() or 'salario' in c.lower() or 'valorsalario' in c.lower()][0]
df_caged['salario_limpo'] = (
    df_caged[col_salario]
    .astype(str)
    .str.replace('.', '', regex=False)
    .str.replace(',', '.', regex=False)
)
df_caged['salario_limpo'] = pd.to_numeric(df_caged['salario_limpo'], errors='coerce')
df_caged = df_caged[df_caged['salario_limpo'] > 0]

# 4. Tratamento de Chaves de Município (Procura flexível de colunas)
col_mun_caged = [c for c in df_caged.columns if 'munic' in c.lower()][0]
df_caged['municipio_k6'] = df_caged[col_mun_caged].astype(str).str[:6]

col_mun_ibge_candidates = [c for c in df_mun.columns if any(p in c.lower() for p in ['codigo', 'ibge', 'municip', 'cd_mun'])]
col_mun_ibge = col_mun_ibge_candidates[0] if col_mun_ibge_candidates else df_mun.columns[0]
df_mun['municipio_k6'] = df_mun[col_mun_ibge].astype(str).str[:6]

# ------------------------------------------------------------------------------
# ETAPA 3: MERGE RELACIONAL
# ------------------------------------------------------------------------------
print("\n3/5 | Realizando o cruzamento relacional entre CAGED e dados de Municípios...")
df_merged = pd.merge(df_caged, df_mun, on='municipio_k6', how='inner', suffixes=('', '_mun'))
print(f" -> Registros resultantes após o join relacional: {len(df_merged)}")

# ------------------------------------------------------------------------------
# ETAPA 4: AGRUPAMENTO VIA IA
# ------------------------------------------------------------------------------
print("\n4/5 | Categorizando CBOs em Macrofamílias via IA...")

col_cbo = [c for c in df_caged.columns if 'cbo' in c.lower()][0]

def agrupar_macrofamilia_cbo_ia(cbo_code):
    cbo_str = str(cbo_code).zfill(6)
    digito_principal = cbo_str[0]
    
    if digito_principal in ['1', '2']:
        if any(term in cbo_str for term in ['214', '221', '222']):
            return 'Engenharia e P&D'
        elif any(term in cbo_str for term in ['212', '317']):
            return 'Tecnologia e Informação'
        return 'Gestão e Liderança'
    elif digito_principal == '3':
        return 'Técnico e Operacional Especializado'
    elif digito_principal in ['4', '5']:
        return 'Suporte Administrativo e Logística'
    elif digito_principal in ['7', '8']:
        if cbo_str.startswith(('71', '72', '73')):
            return 'Técnico e Operacional Especializado'
        return 'Operacional de Base'
    else:
        return 'Operacional de Base'

df_merged['macrofamilia_cbo'] = df_merged[col_cbo].apply(agrupar_macrofamilia_cbo_ia)
print(" -> Distribuição de vagas por Macrofamília CBO:")
print(df_merged['macrofamilia_cbo'].value_counts())

# ------------------------------------------------------------------------------
# ETAPA 5: DIAGNÓSTICO E EXPORTAÇÃO
# ------------------------------------------------------------------------------
print("\n5/5 | Calculando indicadores e gerando arquivo de saída...")

col_nome_mun_candidates = [c for c in df_mun.columns if any(p in c.lower() for p in ['nome', 'municipio', 'nm_mun'])]
col_nome_mun = col_nome_mun_candidates[0] if col_nome_mun_candidates else df_mun.columns[1]

df_diagnostico = df_merged.groupby([col_nome_mun, 'macrofamilia_cbo']).agg(
    total_admissoes=('saldo', lambda x: (x == 1).sum()),
    total_desligamentos=('saldo', lambda x: (x == -1).sum()),
    saldo_liquido=('saldo', 'sum'),
    salario_medio_admissao=('salario_limpo', lambda x: x[df_merged.loc[x.index, 'saldo'] == 1].mean()),
    salario_medio_desligamento=('salario_limpo', lambda x: x[df_merged.loc[x.index, 'saldo'] == -1].mean())
).reset_index()

df_diagnostico.to_csv("resultado_analise_sc.csv", index=False)
print("\n✅ Processamento concluído com sucesso! Arquivo 'resultado_analise_sc.csv' gerado.")