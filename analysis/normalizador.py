import pandas as pd
import numpy as np
from typing import Dict, Any


class Normalizador:

    @staticmethod
    def diagnosticar_problemas(df: pd.DataFrame) -> Dict[str, Any]:
        diagnostico = {
            'total_linhas': len(df),
            'total_colunas': len(df.columns),
            'duplicatas': df.duplicated().sum(),
            'colunas_com_nulos': {},
            'tipos_de_dados': df.dtypes.to_dict(),
            'memoria_mb': df.memory_usage(deep=True).sum() / 1024**2
        }

        for col in df.columns:
            nulos = df[col].isnull().sum()
            if nulos > 0:
                diagnostico['colunas_com_nulos'][col] = {
                    'total_nulos': int(nulos),
                    'percentual': round(nulos / len(df) * 100, 2)
                }

        return diagnostico

    @staticmethod
    def converter_tipos_numericos(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if 'qdt_empregos_gerados' in df.columns:
            df['qdt_empregos_gerados'] = pd.to_numeric(
                df['qdt_empregos_gerados'],
                errors='coerce'
            ).astype('Int64')

        if 'populacao_beneficiada' in df.columns:
            df['populacao_beneficiada'] = pd.to_numeric(
                df['populacao_beneficiada'],
                errors='coerce'
            ).astype('Int64')

        return df

    @staticmethod
    def normalizar_datas(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        colunas_data = [
            'data_inicial_prevista',
            'data_final_prevista',
            'data_inicial_efetiva',
            'data_final_efetiva',
            'data_cadastro',
            'data_situacao',
            'created_at',
            'updated_at'
        ]

        for col in colunas_data:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        return df

    @staticmethod
    def tratar_nulos(df: pd.DataFrame, estrategia: str = 'manter') -> pd.DataFrame:
        df = df.copy()

        if estrategia == 'remover_linhas':
            df = df.dropna(how='all')
        elif estrategia == 'remover_colunas':
            threshold = len(df) * 0.5
            df = df.dropna(axis=1, thresh=threshold)
        elif estrategia == 'preencher_zero':
            df = df.fillna(0)

        return df

    @staticmethod
    def remover_duplicatas(df: pd.DataFrame, subset: list = None) -> pd.DataFrame:
        if subset:
            return df.drop_duplicates(subset=subset, keep='first')
        return df.drop_duplicates(keep='first')

    @staticmethod
    def criar_features(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if 'data_inicial_prevista' in df.columns and 'data_final_prevista' in df.columns:
            df['duracao_prevista_dias'] = (
                df['data_final_prevista'] - df['data_inicial_prevista']
            ).dt.days

        if 'data_inicial_efetiva' in df.columns and 'data_final_efetiva' in df.columns:
            df['duracao_efetiva_dias'] = (
                df['data_final_efetiva'] - df['data_inicial_efetiva']
            ).dt.days

        if 'data_cadastro' in df.columns:
            df['ano_cadastro'] = df['data_cadastro'].dt.year
            df['mes_cadastro'] = df['data_cadastro'].dt.month

        return df

    @staticmethod
    def normalizar_completo(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df = Normalizador.normalizar_datas(df)
        df = Normalizador.converter_tipos_numericos(df)
        df = Normalizador.remover_duplicatas(df, subset=['id_unico'])
        df = Normalizador.criar_features(df)

        return df
