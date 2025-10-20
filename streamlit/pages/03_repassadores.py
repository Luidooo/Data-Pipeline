import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from analysis import DataLoader, Visualizador

st.set_page_config(page_title="Repassadores", page_icon="📊", layout="wide")

st.title("Análise de Repassadores")

st.markdown("""
Repassadores são os órgãos responsáveis por repassar recursos para os projetos.
Esta página apresenta análises sobre os valores repassados e a participação de cada órgão.
""")

@st.cache_data
def load_valores_repassadores():
    loader = DataLoader()
    return loader.load_valores_por_repassador()

@st.cache_data
def load_all_repassadores():
    loader = DataLoader()
    return loader.load_repassadores()

with st.spinner("Carregando dados..."):
    df_valores = load_valores_repassadores()
    df_all = load_all_repassadores()

st.header("Top Repassadores por Valor Total")

n = st.slider("Selecione o número de repassadores", min_value=5, max_value=25, value=10, step=1)

df_top = df_valores.head(n)

col1, col2 = st.columns([3, 1])

with col1:
    fig = Visualizador.plot_valores_repassadores(df_top, n=n, tipo='plotly')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Ranking")
    df_display = df_top[['nome', 'valor_total']].copy()
    df_display['valor_total'] = df_display['valor_total'].apply(lambda x: f"R$ {x:,.2f}" if pd.notna(x) else "N/A")
    st.dataframe(df_display.head(10), use_container_width=True, hide_index=True)

import pandas as pd

st.divider()

st.header("Estatísticas dos Repassadores")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Repassadores", len(df_all))

with col2:
    valor_total = df_valores['valor_total'].sum()
    st.metric("Valor Total", f"R$ {valor_total:,.2f}")

with col3:
    st.metric("Média de Valor", f"R$ {df_valores['valor_total'].mean():,.2f}")

with col4:
    st.metric("Total de Projetos", df_valores['total_projetos'].sum())

st.divider()

st.header("Distribuição de Valores")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 5 por Valor")
    top5_valor = df_valores.nlargest(5, 'valor_total')[['nome', 'valor_total', 'total_projetos']]
    st.dataframe(top5_valor, use_container_width=True, hide_index=True)

with col2:
    st.subheader("Top 5 por Quantidade de Projetos")
    top5_projetos = df_valores.nlargest(5, 'total_projetos')[['nome', 'total_projetos', 'valor_total']]
    st.dataframe(top5_projetos, use_container_width=True, hide_index=True)

st.divider()

st.header("Tabela Completa de Repassadores")

df_display_full = df_valores.copy()
df_display_full.index = range(1, len(df_display_full) + 1)

st.dataframe(
    df_display_full,
    use_container_width=True,
    column_config={
        "nome": st.column_config.TextColumn("Nome do Repassador", width="large"),
        "codigo": st.column_config.NumberColumn("Código", format="%d"),
        "total_projetos": st.column_config.NumberColumn("Total de Projetos", format="%d"),
        "valor_total": st.column_config.NumberColumn("Valor Total", format="R$ %.2f")
    }
)

st.divider()

st.header("Buscar Repassador")

busca = st.text_input("Digite o nome do repassador para buscar")

if busca:
    df_filtrado = df_valores[df_valores['nome'].str.contains(busca, case=False, na=False)]

    if not df_filtrado.empty:
        st.success(f"Encontrado {len(df_filtrado)} repassador(es)")
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhum repassador encontrado com esse nome")
