import pandas as pd
import numpy as np
from typing import Dict, Any


class Analisador:

    @staticmethod
    def estatisticas_descritivas(df: pd.DataFrame) -> pd.DataFrame:
        return df.describe(include='all')

    @staticmethod
    def resumo_dataset(df: pd.DataFrame) -> Dict[str, Any]:
        return {
            'total_registros': len(df),
            'total_colunas': len(df.columns),
            'colunas': list(df.columns),
            'tipos_dados': df.dtypes.value_counts().to_dict(),
            'memoria_total_mb': round(df.memory_usage(deep=True).sum() / 1024**2, 2),
            'valores_nulos_total': int(df.isnull().sum().sum())
        }

    @staticmethod
    def analise_situacao(df: pd.DataFrame) -> pd.DataFrame:
        if 'situacao' not in df.columns:
            return pd.DataFrame()

        return df['situacao'].value_counts().reset_index().rename(
            columns={'index': 'situacao', 'situacao': 'total'}
        )

    @staticmethod
    def analise_temporal(df: pd.DataFrame) -> pd.DataFrame:
        if 'data_cadastro' not in df.columns:
            return pd.DataFrame()

        df_temp = df.copy()
        df_temp['ano'] = pd.to_datetime(df_temp['data_cadastro']).dt.year

        return df_temp.groupby('ano').size().reset_index(name='total_projetos')

    @staticmethod
    def analise_valores(df: pd.DataFrame, coluna_valor: str = 'populacao_beneficiada') -> Dict[str, Any]:
        if coluna_valor not in df.columns:
            return {}

        valores = pd.to_numeric(df[coluna_valor], errors='coerce').dropna()

        if len(valores) == 0:
            return {'erro': f'Nenhum valor válido em {coluna_valor}'}

        return {
            'total': int(len(valores)),
            'media': float(valores.mean()),
            'mediana': float(valores.median()),
            'minimo': float(valores.min()),
            'maximo': float(valores.max()),
            'desvio_padrao': float(valores.std()),
            'soma_total': float(valores.sum())
        }

    @staticmethod
    def analise_empregos(df: pd.DataFrame) -> Dict[str, Any]:
        return Analisador.analise_valores(df, 'qdt_empregos_gerados')

    @staticmethod
    def analise_populacao(df: pd.DataFrame) -> Dict[str, Any]:
        return Analisador.analise_valores(df, 'populacao_beneficiada')

    @staticmethod
    def correlacao_numerica(df: pd.DataFrame) -> pd.DataFrame:
        colunas_numericas = df.select_dtypes(include=[np.number]).columns
        if len(colunas_numericas) > 1:
            return df[colunas_numericas].corr()
        return pd.DataFrame()

    @staticmethod
    def top_n_por_coluna(df: pd.DataFrame, coluna: str, n: int = 10) -> pd.DataFrame:
        if coluna not in df.columns:
            return pd.DataFrame()

        return df[coluna].value_counts().head(n).reset_index().rename(
            columns={'index': coluna, coluna: 'total'}
        )

    @staticmethod
    def projetos_por_uf(df: pd.DataFrame) -> pd.DataFrame:
        if 'uf' not in df.columns:
            return pd.DataFrame()

        return df['uf'].value_counts().reset_index().rename(
            columns={'index': 'uf', 'uf': 'total_projetos'}
        )

    @staticmethod
    def analise_completa(df: pd.DataFrame) -> Dict[str, Any]:
        return {
            'resumo': Analisador.resumo_dataset(df),
            'situacao': Analisador.analise_situacao(df).to_dict('records'),
            'temporal': Analisador.analise_temporal(df).to_dict('records'),
            'empregos': Analisador.analise_empregos(df),
            'populacao': Analisador.analise_populacao(df)
        }
