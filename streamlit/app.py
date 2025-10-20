import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis import DataLoader, Normalizador, Analisador, Visualizador

st.set_page_config(
    page_title="Dashboard ObrasGov DF",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("Navegação")
st.sidebar.markdown("---")

st.title("Dashboard ObrasGov - Distrito Federal")

@st.cache_data
def load_all_data():
    loader = DataLoader()
    df = loader.load_projetos()
    df = Normalizador.normalizar_completo(df)
    return df

@st.cache_data
def load_executores_data(n):
    loader = DataLoader()
    return loader.load_top_executores(n=n)

@st.cache_data
def load_repassadores_data():
    loader = DataLoader()
    return loader.load_valores_por_repassador()

@st.cache_data
def load_temporal_data():
    loader = DataLoader()
    return loader.load_projetos_por_ano()

st.markdown(f'<div id="visao_geral"></div>', unsafe_allow_html=True)
st.header("Visão Geral")

with st.spinner("Carregando dados..."):
    df = load_all_data()
    diagnostico = Normalizador.diagnosticar_problemas(df)
    analise = Analisador.analise_completa(df)

st.subheader("Resumo do Dataset")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Registros", diagnostico['total_linhas'])

with col2:
    st.metric("Total de Colunas", diagnostico['total_colunas'])

with col3:
    st.metric("Duplicatas", diagnostico['duplicatas'])

with col4:
    st.metric("Memória (MB)", f"{diagnostico['memoria_mb']:.2f}")

st.subheader("Qualidade dos Dados")

if diagnostico['colunas_com_nulos']:
    nulos_data = []
    for col, info in diagnostico['colunas_com_nulos'].items():
        nulos_data.append({
            'Coluna': col,
            'Total Nulos': info['total_nulos'],
            'Percentual': f"{info['percentual']}%"
        })

    df_nulos = pd.DataFrame(nulos_data).sort_values('Total Nulos', ascending=False)
    st.dataframe(df_nulos, use_container_width=True, hide_index=True)
else:
    st.success("Nenhum valor nulo encontrado!")

st.subheader("Distribuição por Situação")

situacao_df = Analisador.analise_situacao(df)
if not situacao_df.empty:
    col1, col2 = st.columns([2, 1])

    with col1:
        fig = Visualizador.plot_distribuicao_situacao(situacao_df, tipo='plotly')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.dataframe(situacao_df, use_container_width=True, hide_index=True)

st.markdown("---")

st.markdown(f'<div id="executores"></div>', unsafe_allow_html=True)
st.header("Executores")

st.markdown("Executores são as instituições responsáveis pela execução dos projetos de investimento.")

n_executores = st.slider("Número de executores para exibir", min_value=5, max_value=31, value=10, step=1)

with st.spinner("Carregando dados de executores..."):
    df_top_executores = load_executores_data(n_executores)

col1, col2 = st.columns([3, 1])

with col1:
    fig = Visualizador.plot_top_executores(df_top_executores, n=n_executores, tipo='plotly')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Ranking")
    st.dataframe(
        df_top_executores[['nome', 'total_projetos']].head(10),
        use_container_width=True,
        hide_index=True
    )

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Executores", len(df_top_executores))

with col2:
    st.metric("Executor com Mais Projetos", df_top_executores.iloc[0]['total_projetos'])

with col3:
    st.metric("Média de Projetos", f"{df_top_executores['total_projetos'].mean():.1f}")

with col4:
    st.metric("Mediana de Projetos", f"{df_top_executores['total_projetos'].median():.0f}")

busca_executor = st.text_input("Buscar executor:", key="busca_executor")

if busca_executor:
    df_filtrado = df_top_executores[df_top_executores['nome'].str.contains(busca_executor, case=False, na=False)]

    if not df_filtrado.empty:
        st.success(f"Encontrado {len(df_filtrado)} executor(es)")
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhum executor encontrado com esse nome")

st.markdown("---")

st.markdown(f'<div id="repassadores"></div>', unsafe_allow_html=True)
st.header("Repassadores")

st.markdown("Repassadores são os órgãos responsáveis por repassar recursos para os projetos.")

with st.spinner("Carregando dados de repassadores..."):
    df_repassadores = load_repassadores_data()

n_repassadores = st.slider("Número de repassadores para exibir", min_value=5, max_value=25, value=10, step=1)

df_top_repassadores = df_repassadores.head(n_repassadores)

col1, col2 = st.columns([3, 1])

with col1:
    fig = Visualizador.plot_valores_repassadores(df_top_repassadores, n=n_repassadores, tipo='plotly')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Ranking")
    df_display = df_top_repassadores[['nome', 'valor_total']].copy()
    df_display['valor_total'] = df_display['valor_total'].apply(lambda x: f"R$ {x:,.2f}" if pd.notna(x) else "N/A")
    st.dataframe(df_display.head(10), use_container_width=True, hide_index=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Repassadores", len(df_repassadores))

with col2:
    valor_total = df_repassadores['valor_total'].sum()
    st.metric("Valor Total", f"R$ {valor_total:,.2f}")

with col3:
    st.metric("Média de Valor", f"R$ {df_repassadores['valor_total'].mean():,.2f}")

with col4:
    st.metric("Total de Projetos", df_repassadores['total_projetos'].sum())

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 5 por Valor")
    top5_valor = df_repassadores.nlargest(5, 'valor_total')[['nome', 'valor_total', 'total_projetos']]
    st.dataframe(top5_valor, use_container_width=True, hide_index=True)

with col2:
    st.subheader("Top 5 por Quantidade de Projetos")
    top5_projetos = df_repassadores.nlargest(5, 'total_projetos')[['nome', 'total_projetos', 'valor_total']]
    st.dataframe(top5_projetos, use_container_width=True, hide_index=True)

busca_repassador = st.text_input("Buscar repassador:", key="busca_repassador")

if busca_repassador:
    df_filtrado = df_repassadores[df_repassadores['nome'].str.contains(busca_repassador, case=False, na=False)]

    if not df_filtrado.empty:
        st.success(f"Encontrado {len(df_filtrado)} repassador(es)")
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhum repassador encontrado com esse nome")

st.markdown("---")

st.markdown(f'<div id="temporal"></div>', unsafe_allow_html=True)
st.header("Análise Temporal")

st.markdown("Esta seção apresenta a evolução dos projetos ao longo do tempo.")

with st.spinner("Carregando dados temporais..."):
    df_ano = load_temporal_data()

st.subheader("Evolução de Cadastros por Ano")

if not df_ano.empty:
    fig = Visualizador.plot_timeline_projetos(df_ano, tipo='plotly')
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Dados por Ano")
        df_ano_display = df_ano.copy()
        df_ano_display['ano'] = df_ano_display['ano'].astype(int)
        st.dataframe(df_ano_display, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("Estatísticas")
        st.metric("Ano com Mais Cadastros", int(df_ano.loc[df_ano['total_projetos'].idxmax(), 'ano']))
        st.metric("Total no Pico", int(df_ano['total_projetos'].max()))
        st.metric("Média por Ano", f"{df_ano['total_projetos'].mean():.1f}")
else:
    st.warning("Não há dados temporais disponíveis")

if 'ano_cadastro' in df.columns:
    anos_disponiveis = sorted(df['ano_cadastro'].dropna().unique())

    if len(anos_disponiveis) > 0:
        st.subheader("Análise por Período")

        col1, col2 = st.columns(2)

        with col1:
            ano_inicio = st.selectbox("Ano Início", anos_disponiveis, index=0)

        with col2:
            ano_fim = st.selectbox("Ano Fim", anos_disponiveis, index=len(anos_disponiveis)-1)

        df_filtrado = df[(df['ano_cadastro'] >= ano_inicio) & (df['ano_cadastro'] <= ano_fim)]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total de Projetos", len(df_filtrado))

        with col2:
            if 'situacao' in df_filtrado.columns:
                cadastrados = len(df_filtrado[df_filtrado['situacao'] == 'Cadastrada'])
                st.metric("Cadastrados", cadastrados)

        with col3:
            if 'situacao' in df_filtrado.columns:
                concluidos = len(df_filtrado[df_filtrado['situacao'] == 'Concluída'])
                st.metric("Concluídos", concluidos)

if 'mes_cadastro' in df.columns:
    st.subheader("Análise de Meses")

    df_mes = df.groupby('mes_cadastro').size().reset_index(name='total_projetos')
    df_mes = df_mes.sort_values('mes_cadastro')

    meses_map = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    df_mes['mes_nome'] = df_mes['mes_cadastro'].map(meses_map)

    col1, col2 = st.columns([3, 1])

    with col1:
        import plotly.express as px
        fig_mes = px.bar(
            df_mes,
            x='mes_nome',
            y='total_projetos',
            title='Distribuição de Cadastros por Mês',
            labels={'mes_nome': 'Mês', 'total_projetos': 'Total de Projetos'}
        )
        st.plotly_chart(fig_mes, use_container_width=True)

    with col2:
        st.subheader("Top 3 Meses")
        top_meses = df_mes.nlargest(3, 'total_projetos')[['mes_nome', 'total_projetos']]
        st.dataframe(top_meses, use_container_width=True, hide_index=True)

st.markdown("---")

st.markdown("""
### Tecnologias Utilizadas

- **Backend**: FastAPI + PostgreSQL
- **Análise**: Pandas, NumPy
- **Visualização**: Plotly, Matplotlib, Seaborn
- **Dashboard**: Streamlit
- **Containerização**: Docker
""")

st.sidebar.markdown('[Visão Geral](#visao_geral)')
st.sidebar.markdown('[Executores](#executores)')
st.sidebar.markdown('[Repassadores](#repassadores)')
st.sidebar.markdown('[Análise Temporal](#temporal)')