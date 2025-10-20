import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from analysis import DataLoader, Normalizador, Analisador, Visualizador

st.set_page_config(page_title="Visão Geral", page_icon="📊", layout="wide")

st.title("Visão Geral dos Dados")

@st.cache_data
def load_data():
    loader = DataLoader()
    df = loader.load_projetos()
    df = Normalizador.normalizar_completo(df)
    return df

@st.cache_data
def get_diagnostico(df):
    return Normalizador.diagnosticar_problemas(df)

@st.cache_data
def get_analise_completa(df):
    return Analisador.analise_completa(df)

with st.spinner("Carregando dados..."):
    df = load_data()
    diagnostico = get_diagnostico(df)
    analise = get_analise_completa(df)

st.header("Resumo do Dataset")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Registros", diagnostico['total_linhas'])

with col2:
    st.metric("Total de Colunas", diagnostico['total_colunas'])

with col3:
    st.metric("Duplicatas", diagnostico['duplicatas'])

with col4:
    st.metric("Memória (MB)", f"{diagnostico['memoria_mb']:.2f}")

st.divider()

st.header("Qualidade dos Dados")

if diagnostico['colunas_com_nulos']:
    st.subheader("Colunas com Valores Nulos")

    nulos_data = []
    for col, info in diagnostico['colunas_com_nulos'].items():
        nulos_data.append({
            'Coluna': col,
            'Total Nulos': info['total_nulos'],
            'Percentual': f"{info['percentual']}%"
        })

    import pandas as pd
    df_nulos = pd.DataFrame(nulos_data).sort_values('Total Nulos', ascending=False)
    st.dataframe(df_nulos, use_container_width=True, hide_index=True)
else:
    st.success("Nenhum valor nulo encontrado!")

st.divider()

st.header("Distribuição por Situação")

situacao_df = Analisador.analise_situacao(df)
if not situacao_df.empty:
    col1, col2 = st.columns([2, 1])

    with col1:
        fig = Visualizador.plot_distribuicao_situacao(situacao_df, tipo='plotly')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.dataframe(situacao_df, use_container_width=True, hide_index=True)

st.divider()

st.header("Estatísticas Descritivas")

tab1, tab2 = st.tabs(["Visão Geral", "Detalhes por Coluna"])

with tab1:
    stats = Analisador.estatisticas_descritivas(df)
    st.dataframe(stats, use_container_width=True)

with tab2:
    colunas = df.columns.tolist()
    coluna_selecionada = st.selectbox("Selecione uma coluna", colunas)

    st.subheader(f"Informações sobre: {coluna_selecionada}")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Tipo de dados:** {df[coluna_selecionada].dtype}")
        st.write(f"**Valores únicos:** {df[coluna_selecionada].nunique()}")
        st.write(f"**Valores nulos:** {df[coluna_selecionada].isnull().sum()}")

    with col2:
        if df[coluna_selecionada].dtype in ['int64', 'float64', 'Int64']:
            st.write(f"**Média:** {df[coluna_selecionada].mean():.2f}")
            st.write(f"**Mediana:** {df[coluna_selecionada].median():.2f}")
            st.write(f"**Desvio Padrão:** {df[coluna_selecionada].std():.2f}")

st.divider()

st.header("Análise de Empregos e População")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Empregos Gerados")
    empregos = analise['empregos']
    if 'erro' not in empregos:
        st.metric("Total com dados", empregos['total'])
        st.metric("Média", f"{empregos['media']:.2f}")
        st.metric("Mediana", f"{empregos['mediana']:.2f}")
        st.metric("Soma Total", f"{empregos['soma_total']:.0f}")
    else:
        st.warning(empregos['erro'])

with col2:
    st.subheader("População Beneficiada")
    populacao = analise['populacao']
    if 'erro' not in populacao:
        st.metric("Total com dados", populacao['total'])
        st.metric("Média", f"{populacao['media']:.2f}")
        st.metric("Mediana", f"{populacao['mediana']:.2f}")
        st.metric("Soma Total", f"{populacao['soma_total']:.0f}")
    else:
        st.warning(populacao['erro'])
