from datetime import datetime
from sqlalchemy.orm import Session

from api import models, schemas


class DataProcessor:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_executor(self, executor_data: schemas.ExecutorAPI) -> models.Executor:
        executor = self.db.query(models.Executor).filter(
            models.Executor.codigo == executor_data.codigo
        ).first()
        if not executor:
            executor = models.Executor(nome=executor_data.nome, codigo=executor_data.codigo)
            self.db.add(executor)
        return executor

    def get_or_create_tomador(self, tomador_data: schemas.TomadorAPI) -> models.Tomador:
        tomador = self.db.query(models.Tomador).filter(
            models.Tomador.codigo == tomador_data.codigo
        ).first()
        if not tomador:
            tomador = models.Tomador(nome=tomador_data.nome, codigo=tomador_data.codigo)
            self.db.add(tomador)
        return tomador

    def get_or_create_repassador(self, repassador_data: schemas.RepassadorAPI) -> models.Repassador:
        repassador = self.db.query(models.Repassador).filter(
            models.Repassador.codigo == repassador_data.codigo
        ).first()
        if not repassador:
            repassador = models.Repassador(nome=repassador_data.nome, codigo=repassador_data.codigo)
            self.db.add(repassador)
        return repassador

    def get_or_create_eixo(self, eixo_data: schemas.EixoAPI) -> models.Eixo:
        eixo = self.db.query(models.Eixo).filter(models.Eixo.id == eixo_data.id).first()
        if not eixo:
            eixo = models.Eixo(id=eixo_data.id, descricao=eixo_data.descricao)
            self.db.add(eixo)
        return eixo

    def get_or_create_tipo(self, tipo_data: schemas.TipoAPI) -> models.Tipo:
        tipo = self.db.query(models.Tipo).filter(models.Tipo.id == tipo_data.id).first()
        if not tipo:
            tipo = models.Tipo(id=tipo_data.id, descricao=tipo_data.descricao, eixo_id=tipo_data.idEixo)
            self.db.add(tipo)
        return tipo

    def get_or_create_subtipo(self, subtipo_data: schemas.SubtipoAPI) -> models.Subtipo:
        subtipo = self.db.query(models.Subtipo).filter(models.Subtipo.id == subtipo_data.id).first()
        if not subtipo:
            subtipo = models.Subtipo(id=subtipo_data.id, descricao=subtipo_data.descricao, tipo_id=subtipo_data.idTipo)
            self.db.add(subtipo)
        return subtipo

    def parse_date(self, date_str: str | None):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            return None

    def process_projeto(self, projeto_data: schemas.ProjetoInvestimentoAPI):
        projeto = self.db.query(models.ProjetoInvestimento).filter(
            models.ProjetoInvestimento.id_unico == projeto_data.idUnico
        ).first()

        if projeto:
            projeto.updated_at = datetime.utcnow()
        else:
            projeto = models.ProjetoInvestimento(
                id_unico=projeto_data.idUnico,
                nome=projeto_data.nome,
                cep=projeto_data.cep,
                endereco=projeto_data.endereco,
                descricao=projeto_data.descricao,
                funcao_social=projeto_data.funcaoSocial,
                meta_global=projeto_data.metaGlobal,
                data_inicial_prevista=self.parse_date(projeto_data.dataInicialPrevista),
                data_final_prevista=self.parse_date(projeto_data.dataFinalPrevista),
                data_inicial_efetiva=self.parse_date(projeto_data.dataInicialEfetiva),
                data_final_efetiva=self.parse_date(projeto_data.dataFinalEfetiva),
                data_cadastro=self.parse_date(projeto_data.dataCadastro),
                data_situacao=self.parse_date(projeto_data.dataSituacao),
                especie=projeto_data.especie,
                natureza=projeto_data.natureza,
                natureza_outras=projeto_data.naturezaOutras,
                situacao=projeto_data.situacao,
                desc_plano_nacional_politica_vinculado=projeto_data.descPlanoNacionalPoliticaVinculado,
                uf=projeto_data.uf,
                qdt_empregos_gerados=projeto_data.qdtEmpregosGerados,
                desc_populacao_beneficiada=projeto_data.descPopulacaoBeneficiada,
                populacao_beneficiada=projeto_data.populacaoBeneficiada,
                observacoes_pertinentes=projeto_data.observacoesPertinentes,
                is_modelada_por_bim=projeto_data.isModeladaPorBim
            )
            self.db.add(projeto)

        self.db.flush()

        projeto.executores.clear()
        executores_unicos = {exec_data.codigo: exec_data for exec_data in projeto_data.executores}
        for executor_data in executores_unicos.values():
            executor = self.get_or_create_executor(executor_data)
            projeto.executores.append(executor)

        projeto.tomadores.clear()
        tomadores_unicos = {tom_data.codigo: tom_data for tom_data in projeto_data.tomadores}
        for tomador_data in tomadores_unicos.values():
            tomador = self.get_or_create_tomador(tomador_data)
            projeto.tomadores.append(tomador)

        projeto.repassadores.clear()
        repassadores_unicos = {rep_data.codigo: rep_data for rep_data in projeto_data.repassadores}
        for repassador_data in repassadores_unicos.values():
            repassador = self.get_or_create_repassador(repassador_data)
            projeto.repassadores.append(repassador)

        projeto.eixos.clear()
        eixos_unicos = {eixo_data.id: eixo_data for eixo_data in projeto_data.eixos}
        for eixo_data in eixos_unicos.values():
            eixo = self.get_or_create_eixo(eixo_data)
            projeto.eixos.append(eixo)

        projeto.tipos.clear()
        tipos_unicos = {tipo_data.id: tipo_data for tipo_data in projeto_data.tipos}
        for tipo_data in tipos_unicos.values():
            tipo = self.get_or_create_tipo(tipo_data)
            projeto.tipos.append(tipo)

        projeto.subtipos.clear()
        subtipos_unicos = {subtipo_data.id: subtipo_data for subtipo_data in projeto_data.subTipos}
        for subtipo_data in subtipos_unicos.values():
            subtipo = self.get_or_create_subtipo(subtipo_data)
            projeto.subtipos.append(subtipo)

        self.db.query(models.FonteRecurso).filter(models.FonteRecurso.projeto_id == projeto.id).delete()
        for fonte_data in projeto_data.fontesDeRecurso:
            fonte = models.FonteRecurso(
                projeto_id=projeto.id,
                origem=fonte_data.origem,
                valor_investimento_previsto=fonte_data.valorInvestimentoPrevisto
            )
            self.db.add(fonte)
