import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Dashboard ObrasGov DF",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Dashboard ObrasGov - Distrito Federal")

st.markdown("""
## Bem-vindo ao Dashboard de Projetos de Investimento

Este dashboard apresenta análises dos projetos de investimento público do Distrito Federal,
consumidos da API do ObrasGov.br.

### Navegação

Use o menu lateral para acessar diferentes análises:

- **Visão Geral**: Estatísticas gerais e resumo dos dados
- **Executores**: Análise dos principais executores de projetos
- **Repassadores**: Análise dos órgãos repassadores e valores
- **Análise Temporal**: Evolução dos projetos ao longo do tempo

### Atualização dos Dados

Os dados são sincronizados automaticamente todos os dias às 8h (horário de Brasília)
através da API FastAPI que consome o ObrasGov.br.

### Sobre os Dados

- **Fonte**: API ObrasGov.br
- **Base de dados**: PostgreSQL
- **Total de projetos**: 100 projetos do DF
- **Estrutura**: 14 tabelas normalizadas
""")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total de Projetos",
        value="100"
    )

with col2:
    st.metric(
        label="Executores",
        value="31"
    )

with col3:
    st.metric(
        label="Repassadores",
        value="25"
    )

st.divider()

st.info("Selecione uma página no menu lateral para começar a análise")

st.markdown("""
---
### Tecnologias Utilizadas

- **Backend**: FastAPI + PostgreSQL
- **Análise**: Pandas, NumPy
- **Visualização**: Plotly, Matplotlib, Seaborn
- **Dashboard**: Streamlit
- **Containerização**: Docker
""")
