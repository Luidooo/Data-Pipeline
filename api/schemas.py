from typing import List, Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel, ConfigDict


class ExecutorAPI(BaseModel):
    nome: str
    codigo: int


class TomadorAPI(BaseModel):
    nome: str
    codigo: int


class RepassadorAPI(BaseModel):
    nome: str
    codigo: int


class EixoAPI(BaseModel):
    id: int
    descricao: str


class TipoAPI(BaseModel):
    id: int
    descricao: str
    idEixo: int


class SubtipoAPI(BaseModel):
    id: int
    descricao: str
    idTipo: int


class FonteRecursoAPI(BaseModel):
    origem: str
    valorInvestimentoPrevisto: Optional[float] = None


class ProjetoInvestimentoAPI(BaseModel):
    idUnico: str
    nome: str
    cep: Optional[str] = None
    endereco: Optional[str] = None
    descricao: Optional[str] = None
    funcaoSocial: Optional[str] = None
    metaGlobal: Optional[str] = None

    dataInicialPrevista: Optional[str] = None
    dataFinalPrevista: Optional[str] = None
    dataInicialEfetiva: Optional[str] = None
    dataFinalEfetiva: Optional[str] = None
    dataCadastro: Optional[str] = None
    dataSituacao: Optional[str] = None

    especie: Optional[str] = None
    natureza: Optional[str] = None
    naturezaOutras: Optional[str] = None
    situacao: Optional[str] = None

    descPlanoNacionalPoliticaVinculado: Optional[str] = None
    uf: Optional[str] = None

    qdtEmpregosGerados: Optional[str] = None
    descPopulacaoBeneficiada: Optional[str] = None
    populacaoBeneficiada: Optional[str] = None

    observacoesPertinentes: Optional[str] = None
    isModeladaPorBim: Optional[bool] = None

    tomadores: List[TomadorAPI] = []
    executores: List[ExecutorAPI] = []
    repassadores: List[RepassadorAPI] = []
    eixos: List[EixoAPI] = []
    tipos: List[TipoAPI] = []
    subTipos: List[SubtipoAPI] = []
    fontesDeRecurso: List[FonteRecursoAPI] = []


class APIResponse(BaseModel):
    content: List[ProjetoInvestimentoAPI]
    pageable: Optional[dict] = None
    totalPages: Optional[int] = None
    totalElements: Optional[int] = None
    last: Optional[bool] = None
    number: Optional[int] = None
    size: Optional[int] = None


class SyncResponse(BaseModel):
    message: str
    total_projetos: int
    total_executores: int
    total_tomadores: int
    total_repassadores: int
    sync_time: str


class ProjetoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    id_unico: str
    nome: str
    uf: Optional[str]
    situacao: Optional[str]
    data_cadastro: Optional[date]
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime
