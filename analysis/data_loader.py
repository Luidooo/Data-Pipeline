import pandas as pd
from typing import Optional
from analysis.db_connector import DatabaseConnector


class DataLoader:
    def __init__(self):
        self.connector = DatabaseConnector()
        self.engine = self.connector.engine

    def load_table(self, table_name: str) -> pd.DataFrame:
        return pd.read_sql(f"SELECT * FROM {table_name}", self.engine)

    def execute_query(self, query: str, params: Optional[dict] = None) -> pd.DataFrame:
        return pd.read_sql(query, self.engine, params=params)

    def load_projetos(self) -> pd.DataFrame:
        return self.load_table("projetos_investimento")

    def load_executores(self) -> pd.DataFrame:
        return self.load_table("executores")

    def load_tomadores(self) -> pd.DataFrame:
        return self.load_table("tomadores")

    def load_repassadores(self) -> pd.DataFrame:
        return self.load_table("repassadores")

    def load_fontes_recurso(self) -> pd.DataFrame:
        return self.load_table("fontes_recurso")

    def load_top_executores(self, n: int = 10) -> pd.DataFrame:
        query = """
        SELECT
            e.nome,
            e.codigo,
            COUNT(*) as total_projetos
        FROM executores e
        JOIN projeto_executor pe ON e.id = pe.executor_id
        GROUP BY e.id, e.nome, e.codigo
        ORDER BY total_projetos DESC
        LIMIT %(n)s
        """
        return self.execute_query(query, params={'n': n})

    def load_top_tomadores(self, n: int = 10) -> pd.DataFrame:
        query = """
        SELECT
            t.nome,
            t.codigo,
            COUNT(*) as total_projetos
        FROM tomadores t
        JOIN projeto_tomador pt ON t.id = pt.tomador_id
        GROUP BY t.id, t.nome, t.codigo
        ORDER BY total_projetos DESC
        LIMIT %(n)s
        """
        return self.execute_query(query, params={'n': n})

    def load_valores_por_repassador(self) -> pd.DataFrame:
        query = """
        SELECT
            r.nome,
            r.codigo,
            COUNT(DISTINCT pr.projeto_id) as total_projetos,
            SUM(fr.valor_investimento_previsto) as valor_total
        FROM repassadores r
        JOIN projeto_repassador pr ON r.id = pr.repassador_id
        JOIN fontes_recurso fr ON pr.projeto_id = fr.projeto_id
        GROUP BY r.id, r.nome, r.codigo
        ORDER BY valor_total DESC
        """
        return self.execute_query(query)

    def load_distribuicao_situacao(self) -> pd.DataFrame:
        query = """
        SELECT
            situacao,
            COUNT(*) as total
        FROM projetos_investimento
        WHERE situacao IS NOT NULL
        GROUP BY situacao
        ORDER BY total DESC
        """
        return self.execute_query(query)

    def load_projetos_por_ano(self) -> pd.DataFrame:
        query = """
        SELECT
            EXTRACT(YEAR FROM data_cadastro) as ano,
            COUNT(*) as total_projetos
        FROM projetos_investimento
        WHERE data_cadastro IS NOT NULL
        GROUP BY ano
        ORDER BY ano
        """
        return self.execute_query(query)

    def load_projetos_completo(self) -> pd.DataFrame:
        query = """
        SELECT
            p.*,
            STRING_AGG(DISTINCT e.nome, ', ') as executores_nomes,
            STRING_AGG(DISTINCT t.nome, ', ') as tomadores_nomes,
            STRING_AGG(DISTINCT r.nome, ', ') as repassadores_nomes
        FROM projetos_investimento p
        LEFT JOIN projeto_executor pe ON p.id = pe.projeto_id
        LEFT JOIN executores e ON pe.executor_id = e.id
        LEFT JOIN projeto_tomador pt ON p.id = pt.tomador_id
        LEFT JOIN tomadores t ON pt.tomador_id = t.id
        LEFT JOIN projeto_repassador pr ON p.id = pr.repassador_id
        LEFT JOIN repassadores r ON pr.repassador_id = r.id
        GROUP BY p.id
        """
        return self.execute_query(query)
