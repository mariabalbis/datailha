import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da página e layout do Streamlit
st.set_page_config(
    page_title="Raio-X do Mercado de Trabalho Industrial - SC",
    page_icon="🏭",
    layout="wide"
)

st.markdown("""
    <style>
    .main-title { font-size: 26px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
    .sub-title { font-size: 15px; color: #4B5563; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏭 Raio-X do Mercado de Trabalho e Vagas Industriais em SC</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Painel Operacional de Inteligência Territorial e Diagnóstico de Apagão de Mão de Obra</div>', unsafe_allow_html=True)

# 2. Ingestão e Processamento com Cache para Alta Performance
@st.cache_data
def carregar_dados():
    # Carga dos arquivos brutos
    try:
        df = pd.read_csv("Novo_Caged_MOV_Limpo.csv", sep=";", encoding="utf-8")
    except Exception:
        try:
            df = pd.read_csv("Novo_Caged_MOV_Limpo.csv", sep=",", encoding="utf-8")
        except Exception:
            df = pd.read_csv("amostra_200.csv", sep=",", encoding="utf-8")
            
    try:
        df_mun = pd.read_csv("Municipios_SC_limpo.csv", sep=";", encoding="utf-8")
    except Exception:
        df_mun = pd.read_csv("Municipios_SC_limpo.csv", sep=",", encoding="utf-8")

    # 1. Filtro do tipo de movimentação (Remoção de 'EX' / 97)
    col_mov = [c for c in df.columns if 'tipomov' in c.lower() or 'tipo_mov' in c.lower()]
    if col_mov:
        df = df[df[col_mov[0]] != 'EX']
        df = df[df[col_mov[0]] != 97]

    # 2. Definição do Saldo de Movimentação
    col_saldo = [c for c in df.columns if 'saldomov' in c.lower() or 'saldo' in c.lower()][0]
    df['saldo'] = df[col_saldo].astype(int)

    # 3. Tratamento robusto para Salário (trata pontos e vírgulas sem falhar)
    col_salario = [c for c in df.columns if 'salário' in c.lower() or 'salario' in c.lower() or 'valorsalario' in c.lower()][0]
    df['salario_limpo'] = (
        df[col_salario]
        .astype(str)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
    )
    df['salario_limpo'] = pd.to_numeric(df['salario_limpo'], errors='coerce')
    df = df[df['salario_limpo'] > 0]

    # 4. Busca flexível pelas chaves de Município para o Join
    col_mun_caged = [c for c in df.columns if 'munic' in c.lower()][0]
    df['municipio_k6'] = df[col_mun_caged].astype(str).str[:6]

    col_mun_ibge_candidates = [c for c in df_mun.columns if any(p in c.lower() for p in ['codigo', 'ibge', 'municip', 'cd_mun'])]
    col_mun_ibge = col_mun_ibge_candidates[0] if col_mun_ibge_candidates else df_mun.columns[0]
    df_mun['municipio_k6'] = df_mun[col_mun_ibge].astype(str).str[:6]

    # Merge relacional
    df_merged = pd.merge(df, df_mun, on='municipio_k6', how='inner', suffixes=('', '_mun'))

    # 5. Agrupamento em Macrofamílias via IA
    col_cbo = [c for c in df.columns if 'cbo' in c.lower()][0]
    def agrupar_cbo(cbo_code):
        cbo_str = str(cbo_code).zfill(6)
        d = cbo_str[0]
        if d in ['1', '2']:
            if any(t in cbo_str for t in ['214', '221', '222']): return 'Engenharia e P&D'
            elif any(t in cbo_str for t in ['212', '317']): return 'Tecnologia e Informação'
            return 'Gestão e Liderança'
        elif d == '3': return 'Técnico e Operacional Especializado'
        elif d in ['4', '5']: return 'Suporte Administrativo e Logística'
        elif d in ['7', '8']:
            if cbo_str.startswith(('71', '72', '73')): return 'Técnico e Operacional Especializado'
            return 'Operacional de Base'
        else: return 'Operacional de Base'

    df_merged['macrofamilia_cbo'] = df_merged[col_cbo].apply(agrupar_cbo)
    return df_merged

with st.spinner("Carregando e processando base de dados do Novo CAGED SC..."):
    df_data = carregar_dados()

# 3. Sidebar (Filtros Interativos)
st.sidebar.header("🔍 Filtros de Análise")

# Identificar nome do município dinamicamente
col_nome_mun_candidates = [c for c in df_data.columns if any(p in c.lower() for p in ['nome', 'municipio', 'nm_mun'])]
col_nome_mun = col_nome_mun_candidates[0] if col_nome_mun_candidates else df_data.columns[1]

municipios_list = ["Todos"] + sorted(df_data[col_nome_mun].unique().tolist())
municipio_sel = st.sidebar.selectbox("Município de Santa Catarina:", municipios_list)

macrofamilias = ["Todas"] + sorted(df_data['macrofamilia_cbo'].unique().tolist())
macro_sel = st.sidebar.selectbox("Macrofamília Ocupacional (IA):", macrofamilias)

# Aplicação dinâmica dos filtros
df_filtered = df_data.copy()
if municipio_sel != "Todos":
    df_filtered = df_filtered[df_filtered[col_nome_mun] == municipio_sel]
if macro_sel != "Todas":
    df_filtered = df_filtered[df_filtered['macrofamilia_cbo'] == macro_sel]

# 4. KPIs Principais
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_admissoes = (df_filtered['saldo'] == 1).sum()
total_desligamentos = (df_filtered['saldo'] == -1).sum()
saldo_liquido = df_filtered['saldo'].sum()
salario_medio = df_filtered['salario_limpo'].mean() if len(df_filtered) > 0 else 0

kpi1.metric("🟢 Total de Admissões", f"{total_admissoes:,}".replace(",", "."))
kpi2.metric("🔴 Total de Desligamentos", f"{total_desligamentos:,}".replace(",", "."))
kpi3.metric("📊 Saldo Líquido", f"{saldo_liquido:,}".replace(",", "."), delta=int(saldo_liquido))
kpi4.metric("💵 Média Salarial", f"R$ {salario_medio:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))

st.markdown("---")

# 5. Painel Gráfico (Plotly Interativo)
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📌 Saldo de Vagas por Macrofamília CBO")
    df_macro = df_filtered.groupby('macrofamilia_cbo')['saldo'].sum().reset_index()
    fig_macro = px.bar(
        df_macro,
        y='macrofamilia_cbo',
        x='saldo',
        orientation='h',
        color='saldo',
        color_continuous_scale='Viridis',
        labels={'saldo': 'Saldo Líquido', 'macrofamilia_cbo': 'Macrofamília'}
    )
    fig_macro.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig_macro, use_container_width=True)

with col_right:
    st.subheader("⚖️ Comparativo Salarial: Admissão vs Desligamento")
    df_sal = df_filtered.groupby(['macrofamilia_cbo', 'saldo'])['salario_limpo'].mean().reset_index()
    df_sal['Movimentação'] = df_sal['saldo'].map({1: 'Admissão (+1)', -1: 'Desligamento (-1)'})
    
    fig_sal = px.bar(
        df_sal,
        x='salario_limpo',
        y='macrofamilia_cbo',
        color='Movimentação',
        barmode='group',
        color_discrete_map={'Admissão (+1)': '#10B981', 'Desligamento (-1)': '#EF4444'},
        labels={'salario_limpo': 'Salário Médio (R$)', 'macrofamilia_cbo': 'Macrofamília'}
    )
    fig_sal.update_layout(height=350)
    st.plotly_chart(fig_sal, use_container_width=True)

st.markdown("---")

# 6. Tabelas de Diagnóstico
st.subheader("🚨 Diagnóstico de Apagão de Mão de Obra e Ranking Geográfico")

tab1, tab2 = st.tabs(["Top Municípios em Expansão/Retração", "Visão Detalhada das Movimentações"])

with tab1:
    df_top_mun = df_filtered.groupby(col_nome_mun).agg(
        Saldo_Liquido=('saldo', 'sum'),
        Admissoes=('saldo', lambda x: (x == 1).sum()),
        Desligamentos=('saldo', lambda x: (x == -1).sum()),
        Salario_Medio=('salario_limpo', 'mean')
    ).sort_values(by='Saldo_Liquido', ascending=False).reset_index()
    
    st.dataframe(df_top_mun.head(15), use_container_width=True)

with tab2:
    st.dataframe(df_filtered.head(100), use_container_width=True)