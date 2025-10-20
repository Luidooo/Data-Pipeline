import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional


class Visualizador:

    @staticmethod
    def plot_top_executores(df: pd.DataFrame, n: int = 10, tipo: str = 'plotly'):
        if tipo == 'plotly':
            fig = px.bar(
                df.head(n),
                x='total_projetos',
                y='nome',
                orientation='h',
                title=f'Top {n} Executores por Número de Projetos',
                labels={'total_projetos': 'Total de Projetos', 'nome': 'Executor'}
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            return fig
        else:
            plt.figure(figsize=(12, 6))
            sns.barplot(data=df.head(n), y='nome', x='total_projetos', palette='viridis')
            plt.title(f'Top {n} Executores por Número de Projetos')
            plt.xlabel('Total de Projetos')
            plt.ylabel('Executor')
            return plt.gcf()

    @staticmethod
    def plot_distribuicao_situacao(df: pd.DataFrame, tipo: str = 'plotly'):
        if tipo == 'plotly':
            fig = px.pie(
                df,
                values='total',
                names='situacao',
                title='Distribuição de Projetos por Situação',
                hole=0.3
            )
            return fig
        else:
            plt.figure(figsize=(10, 6))
            plt.pie(df['total'], labels=df['situacao'], autopct='%1.1f%%', startangle=90)
            plt.title('Distribuição de Projetos por Situação')
            return plt.gcf()

    @staticmethod
    def plot_valores_repassadores(df: pd.DataFrame, n: int = 10, tipo: str = 'plotly'):
        if tipo == 'plotly':
            fig = px.bar(
                df.head(n),
                x='valor_total',
                y='nome',
                orientation='h',
                title=f'Top {n} Repassadores por Valor Total',
                labels={'valor_total': 'Valor Total (R$)', 'nome': 'Repassador'}
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            return fig
        else:
            plt.figure(figsize=(12, 6))
            sns.barplot(data=df.head(n), y='nome', x='valor_total', palette='magma')
            plt.title(f'Top {n} Repassadores por Valor Total')
            plt.xlabel('Valor Total (R$)')
            plt.ylabel('Repassador')
            plt.ticklabel_format(style='plain', axis='x')
            return plt.gcf()

    @staticmethod
    def plot_timeline_projetos(df: pd.DataFrame, tipo: str = 'plotly'):
        if tipo == 'plotly':
            fig = px.line(
                df,
                x='ano',
                y='total_projetos',
                title='Evolução de Cadastros de Projetos por Ano',
                labels={'ano': 'Ano', 'total_projetos': 'Total de Projetos'},
                markers=True
            )
            return fig
        else:
            plt.figure(figsize=(12, 6))
            plt.plot(df['ano'], df['total_projetos'], marker='o', linewidth=2)
            plt.title('Evolução de Cadastros de Projetos por Ano')
            plt.xlabel('Ano')
            plt.ylabel('Total de Projetos')
            plt.grid(True, alpha=0.3)
            return plt.gcf()

    @staticmethod
    def plot_histograma(df: pd.DataFrame, coluna: str, bins: int = 30, tipo: str = 'plotly'):
        if tipo == 'plotly':
            fig = px.histogram(
                df,
                x=coluna,
                nbins=bins,
                title=f'Distribuição de {coluna}',
                labels={coluna: coluna}
            )
            return fig
        else:
            plt.figure(figsize=(10, 6))
            plt.hist(df[coluna].dropna(), bins=bins, edgecolor='black', alpha=0.7)
            plt.title(f'Distribuição de {coluna}')
            plt.xlabel(coluna)
            plt.ylabel('Frequência')
            plt.grid(True, alpha=0.3)
            return plt.gcf()

    @staticmethod
    def plot_boxplot(df: pd.DataFrame, coluna: str, tipo: str = 'plotly'):
        if tipo == 'plotly':
            fig = px.box(
                df,
                y=coluna,
                title=f'Boxplot de {coluna}',
                labels={coluna: coluna}
            )
            return fig
        else:
            plt.figure(figsize=(10, 6))
            sns.boxplot(y=df[coluna].dropna())
            plt.title(f'Boxplot de {coluna}')
            plt.ylabel(coluna)
            return plt.gcf()

    @staticmethod
    def plot_correlacao(df: pd.DataFrame, tipo: str = 'plotly'):
        corr = df.select_dtypes(include=['number']).corr()

        if tipo == 'plotly':
            fig = px.imshow(
                corr,
                text_auto=True,
                aspect='auto',
                title='Matriz de Correlação',
                color_continuous_scale='RdBu_r'
            )
            return fig
        else:
            plt.figure(figsize=(12, 10))
            sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, square=True)
            plt.title('Matriz de Correlação')
            return plt.gcf()

    @staticmethod
    def configurar_estilo_matplotlib():
        sns.set_style("whitegrid")
        sns.set_palette("husl")
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 10
