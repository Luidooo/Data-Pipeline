import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from analysis import DataLoader, Visualizador

st.set_page_config(page_title="Executores", page_icon="📊", layout="wide")

st.title("Análise de Executores")

st.markdown("""
Executores são as instituições responsáveis pela execução dos projetos de investimento.
Esta página apresenta análises sobre os principais executores e sua participação nos projetos do DF.
""")

@st.cache_data
def load_top_executores(n):
    loader = DataLoader()
    return loader.load_top_executores(n=n)

@st.cache_data
def load_all_executores():
    loader = DataLoader()
    return loader.load_executores()

st.header("Top Executores por Número de Projetos")

n = st.slider("Selecione o número de executores", min_value=5, max_value=31, value=10, step=1)

with st.spinner("Carregando dados..."):
    df_top = load_top_executores(n)

col1, col2 = st.columns([3, 1])

with col1:
    fig = Visualizador.plot_top_executores(df_top, n=n, tipo='plotly')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Ranking")
    st.dataframe(
        df_top[['nome', 'total_projetos']].head(10),
        use_container_width=True,
        hide_index=True
    )

st.divider()

st.header("Estatísticas dos Executores")

df_all = load_all_executores()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Executores", len(df_all))

with col2:
    st.metric("Executor com Mais Projetos", df_top.iloc[0]['total_projetos'])

with col3:
    st.metric("Média de Projetos", f"{df_top['total_projetos'].mean():.1f}")

with col4:
    st.metric("Mediana de Projetos", f"{df_top['total_projetos'].median():.0f}")

st.divider()

st.header("Tabela Completa de Executores")

df_display = df_top.copy()
df_display.index = range(1, len(df_display) + 1)

st.dataframe(
    df_display,
    use_container_width=True,
    column_config={
        "nome": st.column_config.TextColumn("Nome do Executor", width="large"),
        "codigo": st.column_config.NumberColumn("Código", format="%d"),
        "total_projetos": st.column_config.NumberColumn("Total de Projetos", format="%d")
    }
)

st.divider()

st.header("Buscar Executor")

busca = st.text_input("Digite o nome do executor para buscar")

if busca:
    df_filtrado = df_top[df_top['nome'].str.contains(busca, case=False, na=False)]

    if not df_filtrado.empty:
        st.success(f"Encontrado {len(df_filtrado)} executor(es)")
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhum executor encontrado com esse nome")
