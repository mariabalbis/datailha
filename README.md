📊 Datathon: Raio-X do Mercado de Trabalho e Vagas Industriais em Santa CatarinaProjeto desenvolvido para a Semana Acadêmica pelas turmas de Ciência de Dados e Inteligência Artificial. A solução atua como uma consultoria analítica para a indústria catarinense, mapeando dinâmicas de contratação, escassez de mão de obra (apagão) e áreas de expansão acelerada no estado.

🎯 Pergunta Central de Negócio “Quais regiões e setores industriais de Santa Catarina estão enfrentando apagão de mão de obra ou expansão acelerada, e como os indicadores de renda e escolaridade explicam esses gargalos?” 

💡 Principais Achados e Diagnóstico de MercadoNossa análise combinou os microdados do Novo CAGED com dados demográficos municipais do IBGE, aplicando categorização avançada via IA Generativa sobre as ocupações (CBOs).

1. Polos de Expansão AceleradaRegiões em Destaque: Norte e Grande Florianópolis.Comportamento: Alto volume de saldo positivo por 10.000 habitantes, impulsionado pelos setores eletroeletrônico, de tecnologia e metalmecânico.Fator Explicativo: A atração de talentos exige infraestrutura local e competitividade salarial para absorver a rápida expansão.
2. Sinais de Apagão de Mão de Obra Gargalo de Qualificação (Norte e Oeste): Alta demanda por funções de Técnicos Especializados e Engenharia/P&D, com escassez de candidatos que preencham os requisitos de alta escolaridade.Apagão por Desatratividade de Renda (Vale do Itajaí): Elevada taxa de rotatividade (turnover) em cargos operacionais de base da indústria têxtil, explicada por compressão salarial e desparidade frente ao custo de vida regional.
🛠️ Arquitetura da Solução e Pipeline de DadosO projeto foi construído em Python e segue a seguinte estrutura de processamento:[ Microdados Novo CAGED ] + [ Municipios SC ]
            │
            ├──> 1. Limpeza e Tratamento (Remoção de EX / Exclusões)
            ├──> 2. Enriquecimento via IA Generativa (Agrupamento de 200+ CBOs em Macrofamílias)
            ├──> 3. Modelagem de Métricas (Saldo/10k Hab, Turnover, Gap Salarial)
            └──> 4. Dashboard Interativo (Streamlit) & Pitch Executivo
            
📈 Métricas e Indicadores Chave (KPIs)Saldo Normalizado por 10.000 Habitantes (saldo_por_10k_hab): Permite comparar o impacto real da geração de vagas entre municípios de portes diferentes.Taxa de Rotatividade Ocupacional (taxa_turnover): Volume total de movimentações (admissões + desligamentos) sobre o total da população/força de trabalho.Variação de Renda e Instrução: Correlação entre a média de salário de admissão versus desligamento e o percentual de trabalhadores com ensino superior ou técnico.

🚀 Recomendações Estratégicas para a IndústriaCurto Prazo: Readequação de pisos salariais e benefícios flexíveis nas regiões com alto turnover operacional (combate à desatratividade).Médio Prazo: Implementação de programas regionais de formação técnica acelerada (parcerias FIESC/SENAI/Universidades) focados nas macrofamílias de maior escassez.Longo Prazo: Políticas conjuntas entre setor privado e gestão pública para atração de talentos e incentivos habitacionais nos polos de expansão vertiginosa.

📂 Estrutura do Repositório├── data/
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

⚙️ Como Executar o ProjetoPré-requisitosPython 3.9+Pip instaladoPasso a PassoClonar o repositório:git clone https://github.com/seu-usuario/datathon-saude-industria-sc.git
cd datathon-saude-industria-sc

Instalar as dependências:pip install -r requirements.txt
Executar o Dashboard Interativo:streamlit run app/dashboard.py
👥 Equipe de Desenvolvimento

Bernardo Bernardes, Maria Balbis, Nicolas Urban e Ryan.

Projeto desenvolvido para o Datathon da Semana Acadêmica - Bacharelado em Ciência de Dados e Inteligência 
