# 📊 Datathon: Raio-X do Mercado de Trabalho e Vagas Industriais em Santa Catarina

Projeto desenvolvido para a **Semana Acadêmica** pelas turmas de Ciência de Dados e Inteligência Artificial. A solução atua como uma consultoria analítica para a indústria catarinense, mapeando dinâmicas de contratação, escassez de mão de obra (apagão) e áreas de expansão acelerada no estado.

---

## 🎯 Pergunta Central de Negócio

> **“Quais regiões e setores industriais de Santa Catarina estão enfrentando apagão de mão de obra ou expansão acelerada, e como os indicadores de renda e escolaridade explicam esses gargalos?”**

---

## 💡 Principais Achados e Diagnóstico de Mercado

Nossa análise combinou os microdados do **Novo CAGED** com dados demográficos municipais do **IBGE**, aplicando categorização avançada via **IA Generativa** sobre as ocupações (CBOs).

### 1. Polos de Expansão Acelerada
* **Regiões em Destaque:** Norte e Grande Florianópolis.
* **Comportamento:** Alto volume de saldo positivo por 10.000 habitantes, impulsionado pelos setores eletroeletrônico, de tecnologia e metalmecânico.
* **Fator Explicativo:** A atração de talentos exige infraestrutura local e competitividade salarial para absorver a rápida expansão.

### 2. Sinais de Apagão de Mão de Obra
* **Gargalo de Qualificação (Norte e Oeste):** Alta demanda por funções de *Técnicos Especializados* e *Engenharia/P&D*, com escassez de candidatos que preencham os requisitos de alta escolaridade.
* **Apagão por Desatratividade de Renda (Vale do Itajaí):** Elevada taxa de rotatividade (*turnover*) em cargos operacionais de base da indústria têxtil, explicada por compressão salarial e desparidade frente ao custo de vida regional.

---

## 🛠️ Arquitetura da Solução e Pipeline de Dados

O projeto foi construído em Python e segue a seguinte estrutura de processamento:

```
[ Microdados Novo CAGED ] + [ Municipios SC ]
            │
            ├──> 1. Limpeza e Tratamento (Remoção de EX / Exclusões)
            ├──> 2. Enriquecimento via IA Generativa (Agrupamento de 200+ CBOs em Macrofamílias)
            ├──> 3. Modelagem de Métricas (Saldo/10k Hab, Turnover, Gap Salarial)
            └──> 4. Dashboard Interativo (Streamlit) & Pitch Executivo
```

---

## 📈 Métricas e Indicadores Chave (KPIs)

1. **Saldo Normalizado por 10.000 Habitantes (`saldo_por_10k_hab`):** Permite comparar o impacto real da geração de vagas entre municípios de portes diferentes.
2. **Taxa de Rotatividade Ocupacional (`taxa_turnover`):** Volume total de movimentações (admissões + desligamentos) sobre o total da população/força de trabalho.
3. **Variação de Renda e Instrução:** Correlação entre a média de salário de admissão versus desligamento e o percentual de trabalhadores com ensino superior ou técnico.

---

## 🚀 Recomendações Estratégicas para a Indústria

* **Curto Prazo:** Readequação de pisos salariais e benefícios flexíveis nas regiões com alto *turnover* operacional (combate à desatratividade).
* **Médio Prazo:** Implementação de programas regionais de formação técnica acelerada (parcerias FIESC/SENAI/Universidades) focados nas macrofamílias de maior escassez.
* **Longo Prazo:** Políticas conjuntas entre setor privado e gestão pública para atração de talentos e incentivos habitacionais nos polos de expansão vertiginosa.

---

## 📂 Estrutura do Repositório

```text
├── data/
│   ├── Novo_Caged_MOV_Limpo.csv    # Base de movimentações tratada
│   └── Municipios_SC_limpo.csv     # Base demográfica dos municípios de SC
├── notebooks/
│   └── pipeline_analise_caged.ipynb # Pipeline completo de ETL e agrupamento via IA
├── app/
│   └── dashboard.py                 # Código do Painel Interativo (Streamlit)
├── presentation/
│   └── pitch_executivo.pdf          # Slides de suporte ao Pitch de 3 minutos
├── README.md                        # Documentação do projeto
└── requirements.txt                 # Dependências do projeto
```

---

## ⚙️ Como Executar o Projeto

### Pré-requisitos
* Python 3.9+
* Pip instalado

### Passo a Passo

1. **Clonar o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/datathon-saude-industria-sc.git
   cd datathon-saude-industria-sc
   ```

2. **Instalar as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Executar o Dashboard Interativo:**
   ```bash
   streamlit run app/dashboard.py
   ```

---

## 👥 Equipe de Desenvolvimento

| Integrante | Fase | Papel Principal |
|--- |--- |--- |
| **Maria Balbis ** | 2ª Fase | Liderança Técnica / Modelagem de Dados & Pipelines |
| **Nicolas Urban ** | 2ª Fase | Engenharia de Prompts (IA Generativa) & Storytelling |
| **Bernardo Bernardes ** | 2ª Fase | Ingestão, Limpeza e Tratamento de Dados |
| **Ryan ** | 2ª Fase | Visualização de Dados e Design do Dashboard |

---
*Projeto desenvolvido para o Datathon da Semana Acadêmica - Bacharelado em Ciência de Dados e Inteligência Artificial.*
