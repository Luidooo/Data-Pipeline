from datetime import datetime, date
from sqlalchemy import Column, Integer, BigInteger, String, Float, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from api.config import Base


class ProjetoInvestimento(Base):
    __tablename__ = "projetos_investimento"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_unico = Column(String(20), unique=True, index=True, nullable=False)

    nome = Column(String(350), nullable=False)
    cep = Column(String(10), nullable=True)
    endereco = Column(Text, nullable=True)
    descricao = Column(Text, nullable=True)
    funcao_social = Column(Text, nullable=True)
    meta_global = Column(Text, nullable=True)

    data_inicial_prevista = Column(Date, nullable=True)
    data_final_prevista = Column(Date, nullable=True)
    data_inicial_efetiva = Column(Date, nullable=True)
    data_final_efetiva = Column(Date, nullable=True)
    data_cadastro = Column(Date, nullable=True)
    data_situacao = Column(Date, nullable=True)

    especie = Column(String(100), nullable=True)
    natureza = Column(String(100), nullable=True)
    natureza_outras = Column(String(200), nullable=True)
    situacao = Column(String(100), nullable=True)

    desc_plano_nacional_politica_vinculado = Column(Text, nullable=True)
    uf = Column(String(2), index=True, nullable=True)

    qdt_empregos_gerados = Column(String(50), nullable=True)
    desc_populacao_beneficiada = Column(Text, nullable=True)
    populacao_beneficiada = Column(String(50), nullable=True)

    observacoes_pertinentes = Column(Text, nullable=True)
    is_modelada_por_bim = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    executores = relationship("Executor", secondary="projeto_executor", back_populates="projetos")
    tomadores = relationship("Tomador", secondary="projeto_tomador", back_populates="projetos")
    repassadores = relationship("Repassador", secondary="projeto_repassador", back_populates="projetos")
    eixos = relationship("Eixo", secondary="projeto_eixo", back_populates="projetos")
    tipos = relationship("Tipo", secondary="projeto_tipo", back_populates="projetos")
    subtipos = relationship("Subtipo", secondary="projeto_subtipo", back_populates="projetos")
    fontes_recurso = relationship("FonteRecurso", back_populates="projeto", cascade="all, delete-orphan")


class Executor(Base):
    __tablename__ = "executores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(300), nullable=False)
    codigo = Column(BigInteger, unique=True, index=True, nullable=False)

    projetos = relationship("ProjetoInvestimento", secondary="projeto_executor", back_populates="executores")


class Tomador(Base):
    __tablename__ = "tomadores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(300), nullable=False)
    codigo = Column(BigInteger, unique=True, index=True, nullable=False)

    projetos = relationship("ProjetoInvestimento", secondary="projeto_tomador", back_populates="tomadores")


class Repassador(Base):
    __tablename__ = "repassadores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(300), nullable=False)
    codigo = Column(BigInteger, unique=True, index=True, nullable=False)

    projetos = relationship("ProjetoInvestimento", secondary="projeto_repassador", back_populates="repassadores")


class Eixo(Base):
    __tablename__ = "eixos"

    id = Column(Integer, primary_key=True)
    descricao = Column(String(200), nullable=False)

    projetos = relationship("ProjetoInvestimento", secondary="projeto_eixo", back_populates="eixos")
    tipos = relationship("Tipo", back_populates="eixo")


class Tipo(Base):
    __tablename__ = "tipos"

    id = Column(Integer, primary_key=True)
    descricao = Column(String(200), nullable=False)
    eixo_id = Column(Integer, ForeignKey("eixos.id"), nullable=False)

    eixo = relationship("Eixo", back_populates="tipos")
    projetos = relationship("ProjetoInvestimento", secondary="projeto_tipo", back_populates="tipos")
    subtipos = relationship("Subtipo", back_populates="tipo")


class Subtipo(Base):
    __tablename__ = "subtipos"

    id = Column(Integer, primary_key=True)
    descricao = Column(String(300), nullable=False)
    tipo_id = Column(Integer, ForeignKey("tipos.id"), nullable=False)

    tipo = relationship("Tipo", back_populates="subtipos")
    projetos = relationship("ProjetoInvestimento", secondary="projeto_subtipo", back_populates="subtipos")


class FonteRecurso(Base):
    __tablename__ = "fontes_recurso"

    id = Column(Integer, primary_key=True, autoincrement=True)
    projeto_id = Column(Integer, ForeignKey("projetos_investimento.id"), nullable=False)
    origem = Column(String(100), nullable=False)
    valor_investimento_previsto = Column(Float, nullable=True)

    projeto = relationship("ProjetoInvestimento", back_populates="fontes_recurso")


class ProjetoExecutor(Base):
    __tablename__ = "projeto_executor"

    projeto_id = Column(Integer, ForeignKey("projetos_investimento.id"), primary_key=True)
    executor_id = Column(Integer, ForeignKey("executores.id"), primary_key=True)


class ProjetoTomador(Base):
    __tablename__ = "projeto_tomador"

    projeto_id = Column(Integer, ForeignKey("projetos_investimento.id"), primary_key=True)
    tomador_id = Column(Integer, ForeignKey("tomadores.id"), primary_key=True)


class ProjetoRepassador(Base):
    __tablename__ = "projeto_repassador"

    projeto_id = Column(Integer, ForeignKey("projetos_investimento.id"), primary_key=True)
    repassador_id = Column(Integer, ForeignKey("repassadores.id"), primary_key=True)


class ProjetoEixo(Base):
    __tablename__ = "projeto_eixo"

    projeto_id = Column(Integer, ForeignKey("projetos_investimento.id"), primary_key=True)
    eixo_id = Column(Integer, ForeignKey("eixos.id"), primary_key=True)


class ProjetoTipo(Base):
    __tablename__ = "projeto_tipo"

    projeto_id = Column(Integer, ForeignKey("projetos_investimento.id"), primary_key=True)
    tipo_id = Column(Integer, ForeignKey("tipos.id"), primary_key=True)


class ProjetoSubtipo(Base):
    __tablename__ = "projeto_subtipo"

    projeto_id = Column(Integer, ForeignKey("projetos_investimento.id"), primary_key=True)
    subtipo_id = Column(Integer, ForeignKey("subtipos.id"), primary_key=True)
