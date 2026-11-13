"""Gera cbo_macrofamilias.csv: taxonomia de 12 macrofamílias aplicada às ocupações CBO
presentes no Novo CAGED. Regras definidas com apoio de LLM sobre as descrições oficiais
do dicionário (aba cbo2002ocupação): chefia > palavras-chave > prefixo do código."""
import re
import sys
import unicodedata
import pandas as pd
from openpyxl import load_workbook

CAGED = "Novo_Caged_MOV_Limpo.csv"
DICIONARIO = sys.argv[1] if len(sys.argv) > 1 else "Dicionario_de_dados.xlsx"

PROD, MANU, ELET, ENG = "Produção e Operação Industrial", "Manutenção e Reparação", "Eletroeletrônica e Automação", "Engenharia e P&D"
TEC, QUAL, LOG, TI = "Técnicos Industriais", "Qualidade, Segurança e Ambiente", "Logística e Cadeia de Suprimentos", "Tecnologia da Informação"
ADM, GEST, CONS = "Administração e Suporte", "Gestão e Liderança", "Construção Civil"
SERV, AGRO, OUT = "Comércio e Serviços", "Agropecuária e Florestal", "Não classificado"

CHEFIA = r"^(supervisor|mestre|encarregado|gerente|chefe|diretor|coordenador|lider)"
# Padrões sem acento: as descrições do dicionário vêm sem acentuação
KEYWORDS = [
    (QUAL, r"seguranca do trabalho|qualidade|meio ambiente|ambiental|higiene ocupacional"),
    (LOG, r"almoxarif|armazen|estoquista|logist|expedi|empilhadeira|conferente|despachante|caminhao|carreteiro|planejamento (e controle )?(da |de )?producao"),
    (TI, r"programador|analista de sistemas|desenvolvedor|informatica|analista de suporte"),
    (ELET, r"eletric|eletron|eletrotecn|automacao|instrumentista|telecomunica"),
    (MANU, r"manuten|\breparador|mecanico de"),
]
SEM_PALAVRA_CHAVE = ("22", "23", "25", "26", "27", "32", "33", "36", "37")  # serviços/saúde/educação: vale o código


def sem_acento(t: str) -> str:
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower().strip()


def classificar(cod: str, desc: str):
    d = sem_acento(desc or "")
    c1, c2, c3, c4 = cod[0], cod[:2], cod[:3], cod[:4]
    if c1 == "1" or re.search(CHEFIA, d):
        return GEST, "chefia"
    if d and c2 not in SEM_PALAVRA_CHAVE and c1 != "5":
        for fam, rx in KEYWORDS:
            if re.search(rx, d) and not (d.startswith("engenheiro") and fam in (ELET, MANU)):
                return fam, "palavra-chave"
    if c3 in ("212", "317"):
        return TI, "codigo"
    if c2 == "20" or c3 in ("211", "213", "214", "216", "217"):
        return ENG, "codigo"
    if c3 in ("253", "254", "354") or c2 in ("22", "23", "26", "27", "32", "33", "36", "37") or c1 == "5":
        return SERV, "codigo"
    if c2 in ("24", "25", "35") or c1 == "4":
        return ADM, "codigo"
    if c3 == "215" or c2 == "34":
        return LOG, "codigo"
    if c2 in ("30", "31", "39"):
        return TEC, "codigo"
    if c1 == "6":
        return AGRO, "codigo"
    if c2 == "71":
        return (PROD, "codigo") if re.search(r"miner|extra|poco|pedreira|detona|garimp|perfurador|rocha", d) else (CONS, "codigo")
    if c3 == "782":
        return SERV, "codigo"
    if c3 == "783" or c4 in ("7825", "7841"):
        return LOG, "codigo"
    if c1 in ("7", "8"):
        return PROD, "codigo"
    if c1 == "9":
        return MANU, "codigo"
    return OUT, "sem regra"


if __name__ == "__main__":
    cb = pd.read_csv(CAGED, sep=";", usecols=["cbo2002ocupação"], dtype=str)["cbo2002ocupação"].dropna().str.zfill(6).unique()
    ws = load_workbook(DICIONARIO, read_only=True)["cbo2002ocupação"]
    dic = {str(r[0]).zfill(6): r[1] for r in ws.iter_rows(values_only=True) if r[0] and str(r[0]).strip().isdigit()}
    linhas = []
    for cod in sorted(cb):
        fam, metodo = classificar(cod, dic.get(cod, ""))
        linhas.append({"cbo": cod, "descricao": dic.get(cod, ""), "macrofamilia": fam, "metodo": metodo,
                       "revisar": int(cod not in dic or fam == OUT)})
    out = pd.DataFrame(linhas)
    out.to_csv("cbo_macrofamilias.csv", index=False, encoding="utf-8-sig")
    print(out["macrofamilia"].value_counts().to_string(), f"\nA revisar: {out['revisar'].sum()} de {len(out)}")
