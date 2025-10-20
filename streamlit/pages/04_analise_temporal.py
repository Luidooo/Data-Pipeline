import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from analysis import DataLoader, Analisador, Visualizador, Normalizador
import pandas as pd

st.set_page_config(page_title="Análise Temporal", page_icon="📊", layout="wide")

st.title("Análise Temporal dos Projetos")

st.markdown("""
Esta página apresenta a evolução dos projetos ao longo do tempo,
incluindo análises de cadastros por ano e tendências temporais.
""")

@st.cache_data
def load_data():
    loader = DataLoader()
    df = loader.load_projetos()
    df = Normalizador.normalizar_completo(df)
    return df

@st.cache_data
def load_projetos_por_ano():
    loader = DataLoader()
    return loader.load_projetos_por_ano()

with st.spinner("Carregando dados..."):
    df = load_data()
    df_ano = load_projetos_por_ano()

st.header("Evolução de Cadastros por Ano")

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

st.divider()

st.header("Análise por Período")

if 'ano_cadastro' in df.columns:
    anos_disponiveis = sorted(df['ano_cadastro'].dropna().unique())

    if len(anos_disponiveis) > 0:
        col1, col2 = st.columns(2)

        with col1:
            ano_inicio = st.selectbox("Ano Início", anos_disponiveis, index=0)

        with col2:
            ano_fim = st.selectbox("Ano Fim", anos_disponiveis, index=len(anos_disponiveis)-1)

        df_filtrado = df[(df['ano_cadastro'] >= ano_inicio) & (df['ano_cadastro'] <= ano_fim)]

        st.subheader(f"Período: {int(ano_inicio)} - {int(ano_fim)}")

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

        st.divider()

        st.subheader("Distribuição por Situação no Período")

        if 'situacao' in df_filtrado.columns:
            situacao_periodo = df_filtrado['situacao'].value_counts().reset_index()
            situacao_periodo.columns = ['situacao', 'total']

            col1, col2 = st.columns([2, 1])

            with col1:
                fig_situacao = Visualizador.plot_distribuicao_situacao(situacao_periodo, tipo='plotly')
                st.plotly_chart(fig_situacao, use_container_width=True)

            with col2:
                st.dataframe(situacao_periodo, use_container_width=True, hide_index=True)

st.divider()

st.header("Análise de Meses")

if 'mes_cadastro' in df.columns:
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
        st.subheader("Cadastros por Mês (Todos os anos)")
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
