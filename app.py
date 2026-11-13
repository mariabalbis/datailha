from pathlib import Path

import json

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

BASE = Path(__file__).parent
st.set_page_config(page_title="DataIlha | Raio-X Industrial SC", page_icon="⚡", layout="wide")

# ----------------------------------------------------------------------------
# DESIGN: preto + roxo + gradientes
# ----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }
.stApp { background: radial-gradient(1100px 600px at 8% -10%, rgba(124,58,237,.30), transparent 60%),
         radial-gradient(900px 500px at 100% 0%, rgba(34,211,238,.10), transparent 55%), #07040F; color: #EDE9FE; }
.stApp p, .stApp label, .stApp span, .stApp li { color: #E4DCFB; }
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.6rem; max-width: 1400px; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0F0A1E 0%, #080512 100%);
         border-right: 1px solid rgba(168,85,247,.25); }
.hero { position: relative; padding: 30px 34px; border-radius: 22px; margin-bottom: 22px; overflow: hidden;
        background: linear-gradient(120deg, rgba(124,58,237,.35) 0%, rgba(17,10,36,.92) 45%, rgba(34,211,238,.14) 100%);
        border: 1px solid rgba(168,85,247,.40); box-shadow: 0 0 60px rgba(124,58,237,.20); }
.hero:after { content:""; position:absolute; inset:0; pointer-events:none; opacity:.35;
        background-image: linear-gradient(rgba(168,85,247,.12) 1px, transparent 1px), linear-gradient(90deg, rgba(168,85,247,.12) 1px, transparent 1px);
        background-size: 38px 38px; mask-image: linear-gradient(90deg, transparent, #000 80%); }
.hero .tag { display:inline-block; font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:#C4B5FD;
        border:1px solid rgba(196,181,253,.4); padding:4px 12px; border-radius:99px; margin-bottom:12px; }
.hero h1 { font-family:'Space Grotesk',sans-serif; font-size:38px; line-height:1.15; margin:0 0 8px 0;
        background: linear-gradient(90deg, #FFFFFF 0%, #C084FC 55%, #22D3EE 100%); -webkit-background-clip:text; color:transparent; }
.hero p { margin:0; color:#B8A9E8; font-size:15px; max-width:760px; position:relative; z-index:1; }
.kpi { background: linear-gradient(150deg, rgba(124,58,237,.22), rgba(12,8,24,.95) 70%);
       border:1px solid rgba(168,85,247,.38); border-radius:18px; padding:18px 20px; height:100%;
       box-shadow: 0 0 34px rgba(124,58,237,.14); }
.kpi .l { font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:#A99BD8; }
.kpi .v { font-family:'Space Grotesk',sans-serif; font-size:32px; font-weight:700; margin:6px 0 2px 0;
       background: linear-gradient(90deg,#E9D5FF,#A855F7 60%,#22D3EE); -webkit-background-clip:text; color:transparent; }
.kpi .s { font-size:12px; color:#9F90CF; }
h2, h3 { font-family:'Space Grotesk',sans-serif !important; color:#F3EEFF !important; }
.sec { font-family:'Space Grotesk',sans-serif; font-size:19px; font-weight:700; margin:26px 0 10px 0; color:#F3EEFF;
       padding-left:12px; border-left:4px solid; border-image: linear-gradient(180deg,#A855F7,#22D3EE) 1; }
button[data-baseweb="tab"] { color:#A99BD8; } button[data-baseweb="tab"][aria-selected="true"] { color:#E9D5FF; }
div[data-baseweb="tab-highlight"] { background: linear-gradient(90deg,#A855F7,#22D3EE) !important; }
.note { font-size:12px; color:#8F81C2; border-top:1px solid rgba(168,85,247,.2); margin-top:28px; padding-top:12px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <span class="tag">Datathon 2026 · Novo CAGED</span>
  <h1>Raio-X da Indústria de Santa Catarina</h1>
  <p>Onde a mão de obra industrial está em expansão ou sob pressão, e como renda e escolaridade ajudam a explicar esses movimentos.</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# DADOS
# ----------------------------------------------------------------------------
SECOES = {"A": "Agropecuária", "B": "Extrativas", "C": "Transformação", "D": "Eletricidade e gás",
          "E": "Água e resíduos", "F": "Construção", "G": "Comércio", "H": "Transporte", "I": "Alojamento e alimentação",
          "J": "Informação e comunicação", "K": "Finanças", "L": "Imobiliárias", "M": "Atividades técnicas",
          "N": "Serviços administrativos", "O": "Administração pública", "P": "Educação", "Q": "Saúde",
          "R": "Artes e lazer", "S": "Outros serviços"}


PARQUET = BASE / "base_compacta.parquet"


def _municipios():
    # Municípios: código IBGE de 7 dígitos -> 6 dígitos (padrão CAGED); remove linha de rodapé HTML
    mun = pd.read_csv(BASE / "Municipios_SC_limpo.csv", sep=",", encoding="utf-8-sig", dtype=str)
    mun.columns = mun.columns.str.strip()
    mun = mun[mun["Código [-]"].str.fullmatch(r"\d{7}", na=False)].copy()
    mun["k6"] = mun["Código [-]"].str[:6]
    col_pop = next(c for c in mun.columns if "estimada" in c.lower())
    mun["pop"] = pd.to_numeric(mun[col_pop], errors="coerce")
    nomes = dict(zip(mun["k6"], mun["Município [-]"]))
    pops = dict(zip(mun["Município [-]"], mun["pop"]))
    nome2k6 = dict(zip(mun["Município [-]"], mun["k6"]))

    return pops, nome2k6, nomes


def _processar_csv():
    cols = ["competênciamov", "município", "seção", "saldomovimentação", "cbo2002ocupação",
            "graudeinstrução", "salário"]
    df = pd.read_csv(BASE / "Novo_Caged_MOV_Limpo.csv", sep=";", decimal=",", encoding="utf-8-sig",
                     usecols=cols, dtype={"município": "string", "cbo2002ocupação": "string", "seção": "category"})
    df = df.rename(columns={"competênciamov": "comp", "município": "cod", "seção": "secao", "saldomovimentação": "saldo",
                            "cbo2002ocupação": "cbo", "graudeinstrução": "grau", "salário": "salario"})

    nomes = _municipios()[2]

    # Últimos 12 meses disponíveis
    meses = sorted(df["comp"].unique())[-12:]
    df = df[df["comp"].isin(meses)].copy()

    df["municipio"] = df["cod"].map(nomes).fillna("Ignorado").astype("category")
    df["adm"] = (df["saldo"] == 1).astype("int8")
    df["desl"] = (df["saldo"] == -1).astype("int8")
    df["saldo"] = df["saldo"].astype("int8")
    df["salario"] = df["salario"].where(df["salario"] > 0).astype("float32")
    tab = pd.read_csv(BASE / "cbo_macrofamilias.csv", dtype=str)  # gerada por gerar_macrofamilias_cbo.py
    df["macro"] = df["cbo"].str.zfill(6).map(dict(zip(tab["cbo"], tab["macrofamilia"]))).fillna("Não classificado").astype("category")
    df["escol"] = pd.Series(np.select([df["grau"].between(1, 5), df["grau"].isin([6, 7]),
                                       df["grau"].isin([8, 9, 10, 11, 80])],
                                      ["Fundamental", "Médio", "Superior+"], "Não identificado"), index=df.index).astype("category")
    df["mes"] = df["comp"].astype(str).str[4:] + "/" + df["comp"].astype(str).str[:4]
    df = df.drop(columns=["cod", "cbo", "grau"])
    return df


@st.cache_resource(show_spinner=False)
def carregar():
    pops, nome2k6, _ = _municipios()
    if PARQUET.exists():  # base compacta: dispensa o CSV de 413 MB
        df = pd.read_parquet(PARQUET)
    else:  # primeira execução com o CSV: gera a base compacta para as próximas
        df = _processar_csv()
        df.to_parquet(PARQUET, index=False)
    ordem = [f"{str(m)[4:]}/{str(m)[:4]}" for m in sorted(df["comp"].unique())]
    return df, pops, ordem, nome2k6


@st.cache_resource(show_spinner=False)
def carregar_geo():
    p = BASE / "sc_municipios.geojson"
    if not p.exists():
        return None
    g = json.loads(p.read_text(encoding="utf-8"))
    for f in g["features"]:
        f["properties"]["k6"] = str(f["properties"]["id"])[:6]  # IBGE 7 dígitos -> 6 (padrão CAGED)
    return g


ESC_SALDO = ["#F472B6", "#1E1240", "#22D3EE"]
ESC_RAZAO = ["#22D3EE", "#1E1240", "#F472B6"]

with st.spinner("Carregando o Novo CAGED (3,4 milhões de registros)..."):
    df, POPS, ORDEM, NOME2K6 = carregar()

# ----------------------------------------------------------------------------
# FILTROS
# ----------------------------------------------------------------------------
st.sidebar.markdown("### Filtros")
secoes_disp = [s for s in SECOES if s in set(df["secao"].astype(str))]
secoes_sel = st.sidebar.multiselect("Setor (seção CNAE)", secoes_disp, default=[s for s in "BCDE" if s in secoes_disp],
                                    format_func=lambda s: f"{s} · {SECOES[s]}")
mun_sel = st.sidebar.selectbox("Município", ["Todos"] + sorted(m for m in df["municipio"].cat.categories if m != "Ignorado"))
macro_sel = st.sidebar.selectbox("Macrofamília ocupacional", ["Todas"] + sorted(df["macro"].cat.categories))
p_ini, p_fim = st.sidebar.select_slider("Período", options=ORDEM, value=(ORDEM[0], ORDEM[-1]))
st.sidebar.caption("Padrão: núcleo industrial (B, C, D, E). Inclua F para ver a construção.")

d = df[df["secao"].isin(secoes_sel) & df["mes"].isin(ORDEM[ORDEM.index(p_ini):ORDEM.index(p_fim) + 1])]
if mun_sel != "Todos":
    d = d[d["municipio"] == mun_sel]
if macro_sel != "Todas":
    d = d[d["macro"] == macro_sel]
if d.empty:
    st.warning("Nenhum registro para esta combinação de filtros.")
    st.stop()


def n(x):
    return f"{x:,.0f}".replace(",", ".")


def rs(x):
    return "n/d" if pd.isna(x) else "R$ " + f"{x:,.0f}".replace(",", ".")


def estilo(fig, h=370):
    fig.update_layout(height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#D9CFF5"),
                      margin=dict(l=10, r=10, t=30, b=10), legend_title_text="", legend=dict(orientation="h", y=1.12),
                      colorway=["#A855F7", "#22D3EE", "#F472B6", "#818CF8"])
    fig.update_xaxes(gridcolor="rgba(168,85,247,.14)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(168,85,247,.14)", zeroline=False)
    return fig


# ----------------------------------------------------------------------------
# KPIs
# ----------------------------------------------------------------------------
saldo, adm, desl = int(d["saldo"].sum()), int(d["adm"].sum()), int(d["desl"].sum())
pop = POPS.get(mun_sel) if mun_sel != "Todos" else sum(v for v in POPS.values() if pd.notna(v))
s10k = saldo / pop * 10_000 if pop else float("nan")
razao = desl / adm if adm else float("nan")
sal_adm, sal_des = d.loc[d["adm"] == 1, "salario"].median(), d.loc[d["desl"] == 1, "salario"].median()


def kpi(l, v, s):
    return f'<div class="kpi"><div class="l">{l}</div><div class="v">{v}</div><div class="s">{s}</div></div>'


k = st.columns(4)
k[0].markdown(kpi("Saldo líquido", f"{saldo:+,}".replace(",", "."), f"{n(adm)} admissões · {n(desl)} desligamentos"), unsafe_allow_html=True)
k[1].markdown(kpi("Saldo por 10 mil hab.", "n/d" if pd.isna(s10k) else f"{s10k:+.1f}".replace(".", ","), "População estimada 2026"), unsafe_allow_html=True)
k[2].markdown(kpi("Desligamentos ÷ admissões", "n/d" if pd.isna(razao) else f"{razao:.2f}".replace(".", ","), "Acima de 1: saídas superam entradas"), unsafe_allow_html=True)
k[3].markdown(kpi("Salário mediano de admissão", rs(sal_adm), f"Desligados: {rs(sal_des)}"), unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# GRÁFICOS
# ----------------------------------------------------------------------------
st.markdown('<div class="sec">Evolução e ocupações</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    ev = d.groupby("mes", observed=True)[["adm", "desl", "saldo"]].sum().reindex([m for m in ORDEM if m in set(d["mes"])]).reset_index()
    ev = ev.rename(columns={"adm": "Admissões", "desl": "Desligamentos", "saldo": "Saldo"})
    fig = px.line(ev.melt("mes", var_name="Série", value_name="Movimentações"), x="mes", y="Movimentações", color="Série",
                  markers=True, category_orders={"mes": ORDEM}, title="Evolução mensal")
    st.plotly_chart(estilo(fig), width="stretch")
with c2:
    mc = d.groupby("macro", observed=True)["saldo"].sum().sort_values().reset_index()
    fig = px.bar(mc, x="saldo", y="macro", orientation="h", color="saldo", title="Saldo por macrofamília de CBO",
                 color_continuous_scale=["#4C1D95", "#A855F7", "#22D3EE"], labels={"saldo": "Saldo", "macro": ""})
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(estilo(fig), width="stretch")

st.markdown('<div class="sec">Renda e escolaridade</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)
with c3:
    sal = pd.concat([d[d["adm"] == 1].assign(Mov="Admitidos"), d[d["desl"] == 1].assign(Mov="Desligados")])
    sm = sal.groupby(["macro", "Mov"], observed=True)["salario"].median().reset_index()
    fig = px.bar(sm, x="salario", y="macro", color="Mov", barmode="group", title="Salário mediano: admitidos × desligados",
                 labels={"salario": "R$", "macro": ""})
    st.plotly_chart(estilo(fig), width="stretch")
with c4:
    es = sal.groupby(["escol", "Mov"], observed=True).size().reset_index(name="q")
    es["%"] = es["q"] / es.groupby("Mov")["q"].transform("sum") * 100
    fig = px.bar(es, x="escol", y="%", color="Mov", barmode="group", title="Escolaridade: admitidos × desligados (%)",
                 category_orders={"escol": ["Fundamental", "Médio", "Superior+", "Não identificado"]}, labels={"escol": ""})
    st.plotly_chart(estilo(fig), width="stretch")

# ----------------------------------------------------------------------------
# RANKINGS
# ----------------------------------------------------------------------------
st.markdown('<div class="sec">Onde está a pressão</div>', unsafe_allow_html=True)
t0, t1, t2, t3 = st.tabs(["Mapa de SC", "Municípios em expansão", "Municípios em retração", "Setores (CNAE)"])


def ranking(chave):
    g = d.groupby(chave, observed=True).agg(saldo=("saldo", "sum"), adm=("adm", "sum"), desl=("desl", "sum")).reset_index()
    g["razao"] = (g["desl"] / g["adm"].replace(0, np.nan)).round(2)
    sa = d[d["adm"] == 1].groupby(chave, observed=True)["salario"].median().rename("sal")
    return g.merge(sa, on=chave, how="left")


cfg = {"saldo": st.column_config.NumberColumn("Saldo", format="%d"),
       "adm": st.column_config.NumberColumn("Admissões", format="%d"),
       "desl": st.column_config.NumberColumn("Desligamentos", format="%d"),
       "razao": st.column_config.NumberColumn("Deslig. ÷ adm.", format="%.2f"),
       "sal": st.column_config.NumberColumn("Salário mediano adm.", format="R$ %.0f"),
       "s10k": st.column_config.NumberColumn("Saldo / 10 mil hab.", format="%.1f")}
rm = ranking("municipio")
rm = rm[rm["municipio"] != "Ignorado"]
rm["s10k"] = rm["saldo"] / rm["municipio"].map(POPS) * 10_000
rm["k6"] = rm["municipio"].map(NOME2K6)
rm = rm.rename(columns={"municipio": "Município"})
with t0:
    geo = carregar_geo()
    if geo is None:
        st.info("Coloque o arquivo sc_municipios.geojson na mesma pasta do app.py para ver o mapa.")
    else:
        metrica = st.radio("Indicador", ["Saldo por 10 mil hab.", "Saldo líquido", "Deslig. ÷ adm."], horizontal=True)
        col, esc = {"Saldo por 10 mil hab.": ("s10k", ESC_SALDO), "Saldo líquido": ("saldo", ESC_SALDO),
                    "Deslig. ÷ adm.": ("razao", ESC_RAZAO)}[metrica]
        if col == "razao":
            faixa = (0.6, 1.4)
        else:
            lim = max(abs(rm[col].quantile(.05)), abs(rm[col].quantile(.95)), 1)
            faixa = (-lim, lim)
        fig = px.choropleth_map(rm, geojson=geo, locations="k6", featureidkey="properties.k6", color=col,
                                color_continuous_scale=esc, range_color=faixa, hover_name="Município",
                                hover_data={"k6": False, "saldo": ":,", "adm": ":,", "desl": ":,", "razao": ":.2f", "s10k": ":.1f"},
                                map_style="carto-darkmatter", zoom=6.2, center={"lat": -27.3, "lon": -50.6}, opacity=0.9)
        fig = estilo(fig, 580)
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), coloraxis_colorbar=dict(title=metrica, len=0.6))
        st.plotly_chart(fig, width="stretch")
        st.caption("Rosa: retração ou pressão; ciano: expansão. Municípios sem movimentação nos filtros ficam sem cor. "
                   "A malha tem 293 dos 295 municípios (faltam os mais recentes).")
with t1:
    st.dataframe(rm.sort_values("saldo", ascending=False).head(15).drop(columns="k6"), hide_index=True, width="stretch", column_config=cfg)
with t2:
    st.dataframe(rm.sort_values("saldo").head(15).drop(columns="k6"), hide_index=True, width="stretch", column_config=cfg)
with t3:
    rs_ = ranking("secao")
    rs_["Setor"] = rs_["secao"].astype(str).map(lambda s: f"{s} · {SECOES.get(s, s)}")
    fig = px.bar(rs_.sort_values("saldo"), x="saldo", y="Setor", orientation="h", color="razao", title="Saldo por setor (cor = deslig. ÷ adm.)",
                 color_continuous_scale=["#22D3EE", "#A855F7", "#F472B6"], labels={"saldo": "Saldo", "Setor": "", "razao": "Deslig. ÷ adm."})
    st.plotly_chart(estilo(fig, 340), width="stretch")

st.markdown('<div class="note">Fonte: Novo CAGED (MTE), últimos 12 meses disponíveis, e IBGE. Saldo positivo não equivale a vagas abertas, '
            'e a razão desligamentos ÷ admissões não é taxa de rotatividade. A escolaridade mostra quem foi movimentado, '
            'não o que a vaga exige. Macrofamílias de CBO: taxonomia de 12 grupos gerada com apoio de IA sobre as descrições oficiais (cbo_macrofamilias.csv).</div>', unsafe_allow_html=True)
