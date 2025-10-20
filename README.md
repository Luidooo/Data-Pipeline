# Data Pipeline - ObrasGov Distrito Federal

Pipeline ETL completo para extração, processamento, análise e visualização de dados de projetos de investimento público do Distrito Federal, consumidos da API ObrasGov.br.

## Visão Geral

Sistema completo de análise de dados públicos com:
- **Backend**: API REST com FastAPI + PostgreSQL
- **ETL**: Pipeline automatizado de extração, transformação e carga
- **Análise**: Classes especializadas para processamento de dados
- **Visualização**: Dashboard Streamlit + Jupyter Notebook interativo
- **Infraestrutura**: Docker Compose com healthchecks

> **Ambiente Testado**: Este projeto foi desenvolvido e testado em Linux. Caso tenha algum problema em Ambiente Windows, tente configurar wls (ou mudar pro linux rs)

## Inicialização Rápida

### Opção 1: Script Automatizado (Recomendado)

```bash
./utils/start.sh
```

O script irá:
- Verificar dependências (Docker, Docker Compose)
- Criar arquivo `.env` automaticamente se não existir
- Verificar disponibilidade das portas necessárias
- Parar containers antigos (se houver)
- Iniciar todos os containers com rebuild
- Aguardar a inicialização completa da API
- Exibir URLs de acesso aos serviços

### Opção 2: Comandos Manuais

Caso prefira executar manualmente:

```bash
# 1. Criar arquivo .env
cp .env.example .env

# 2. Subir containers
docker compose up -d --build

# 3. Aguardar inicialização (5 minutos na primeira vez)
# Acompanhar logs:
docker compose logs -f
```

## Serviços Disponíveis

Após a inicialização completa:

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **FastAPI** | http://localhost:8000 | API REST |
| **FastAPI Docs** | http://localhost:8000/docs | Swagger UI |
| **Streamlit** | http://localhost:8501 | Dashboard interativo |
| **JupyterLab** | http://localhost:8888 | Notebook (tema dark) |
| **PostgreSQL** | localhost:5455 | Banco de dados |

## Arquitetura do Projeto

```
Data-Pipeline/
├── api/
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   └── services/
│       ├── obrasgov_client.py
│       └── data_processor.py
├── analysis/
│   ├── data_loader.py
│   ├── normalizador.py
│   ├── analisador.py
│   ├── visualizador.py
│   └── db_connector.py
├── streamlit/
│   ├── app.py
│   └── Dockerfile
├── notebooks/
│   ├── analise_obrasgov_df.ipynb
│   ├── jupyter_config.py
│   ├── start.sh
│   └── Dockerfile
├── utils/ #randon things
├── requirements.txt
├── .env.example
├── docker-compose.yml
└── README.md
```

## Características

### Backend
- API REST com FastAPI e documentação automática (Swagger)
- Banco de dados PostgreSQL normalizado (3NF)
- Sincronização automática agendada (APScheduler - diária às 8h)
- Cliente HTTP assíncrono com retry e backoff exponencial
- Rate limiting (1s entre requisições)
- Healthchecks 

### Pipeline ETL
- **Extract**: Paginação automática da API ObrasGov
- **Transform**: Normalização, validação e deduplicação
- **Load**: Relacionamentos FK + tratamento de duplicatas

### Análise de Dados
- Classes reutilizáveis(para usar no stramlit e no jupyter notebook)
  - DataLoader
  - Normalizador
  - Analisador
  - Visualizador
- Diagnóstico de qualidade de dados
- Análises estatísticas completas
- Gráficos interativos (Plotly) e estáticos (Matplotlib/Seaborn)

### Visualização
- Dashboard Streamlit com 5 seções (Dados, Executores, Repassadores, Temporal)
- Jupyter Notebook com todas as análises executáveis

### Infraestrutura
- Docker Compose com 4 containers isolados
- Healthchecks garantem inicialização correta
- Volume persistente para dados
- Rede isolada para comunicação entre containers

## Pré-requisitos

- Docker e Docker Compose v2
- Python 3.11+ (somente para desenvolvimento local)
- Portas disponíveis: 5455, 8000, 8501, 8888
- Sistema operacional: Linux (testado)

## Configuração do .env

O script `start.sh` cria automaticamente o arquivo `.env` a partir do `.env.example`. Caso queira configurar manualmente:

```bash
POSTGRES_USER=obrasgov_user
POSTGRES_PASSWORD=obrasgov_pass
POSTGRES_DB=obrasgov_db
POSTGRES_PORT=5455

OBRASGOV_API_BASE_URL=https://api.obrasgov.gestao.gov.br/obrasgov/api
OBRASGOV_API_TIMEOUT=60
OBRASGOV_DELAY_BETWEEN_REQUESTS=1

SYNC_SCHEDULE_HOUR=11 #11h utc = 8h da manhã em bsb
SYNC_SCHEDULE_MINUTE=0
```

## Uso

### Dashboard Streamlit

Acesse http://localhost:8501

Seções disponíveis:
- **Visão Geral**: Métricas, qualidade dos dados, distribuição por situação
- **Executores**: Top N executores, ranking, busca
- **Repassadores**: Análise por valor, top 5, busca
- **Análise Temporal**: Evolução anual, distribuição mensal

### Jupyter Notebook

Acesse http://localhost:8888

O notebook `analise_obrasgov_df.ipynb` já estará disponível com:
- Todas as análises do Streamlit
- Gráficos interativos Plotly
- Código executável célula por célula
- Documentação da arquitetura
- (Tema dark por padrão rs)

> Caso o script para executar todas as células falhe,use: `Run → Run All Cells`

### API REST

#### Health Check
```bash
curl http://localhost:8000/health
```

Resposta:
```json
{
  "status": "ok",
  "database": "connected",
  "timestamp": "2025-10-20T12:00:00"
}
```

#### Readiness Check
```bash
curl http://localhost:8000/ready
```

Retorna 200 quando banco está populado, 503 caso contrário.

#### Sincronizar Projetos (Manual)
```bash
curl -X POST "http://localhost:8000/sync?uf=DF"
```

Resposta:
```json
{
  "message": "Sincronização concluída com sucesso para DF",
  "total_projetos": 100,
  "total_executores": 31,
  "total_tomadores": 20,
  "total_repassadores": 25,
  "sync_time": "0:00:27.039667"
}
```

#### Listar Projetos
```bash
curl "http://localhost:8000/projetos?skip=0&limit=10&uf=DF"
```

Parâmetros:
- `skip`: Paginação (default: 0)
- `limit`: Registros por página (default: 100)
- `uf`: Filtro por estado (opcional)

#### Buscar Projeto Específico
```bash
curl "http://localhost:8000/projetos/21103.22-77"
```

## Estrutura do Banco de Dados

### Modelo Relacional (3NF)

```
projetos_investimento (principal)
    ├── executor_id → executores(id)
    ├── tomador_id → tomadores(id)
    └── repassador_id → repassadores(id)
```

### Tabelas

1. **projetos_investimento**
   - Dados principais dos projetos
   - Campos: id, id_unico (UK), uf, situacao, data_cadastro, etc.
   - FKs: executor_id, tomador_id, repassador_id

2. **executores**
   - Instituições executoras
   - Campos: id, nome, codigo, created_at

3. **tomadores**
   - Tomadores de recursos
   - Campos: id, nome, codigo, created_at

4. **repassadores**
   - Órgãos repassadores
   - Campos: id, nome, codigo, created_at

## Análise de Dados

### Classes Disponíveis

#### DataLoader
Carrega dados do PostgreSQL com queries otimizadas:
```python
from analysis import DataLoader

loader = DataLoader()
df = loader.load_projetos()
df_executores = loader.load_top_executores(n=10)
df_repassadores = loader.load_valores_por_repassador()
df_temporal = loader.load_projetos_por_ano()
```

#### Normalizador
Limpa e normaliza dados:
```python
from analysis import Normalizador

df_limpo = Normalizador.normalizar_completo(df)
diagnostico = Normalizador.diagnosticar_problemas(df)
```

#### Analisador
Gera estatísticas e métricas:
```python
from analysis import Analisador

analise = Analisador.analise_completa(df)
situacao_df = Analisador.analise_situacao(df)
```

#### Visualizador
Cria gráficos interativos:
```python
from analysis import Visualizador

fig = Visualizador.plot_top_executores(df_executores, n=10, tipo='plotly')
fig.show()
```

## Sincronização Automática

A API executa sync automático:
- **Horário**: 8h da manhã de Brasilia
- **Frequência**: Diária
- **Configurável**: Variáveis `SYNC_SCHEDULE_HOUR` e `SYNC_SCHEDULE_MINUTE` no `.env`

O sync também é executado automaticamente no startup da API.

## Arquitetura e Fluxo de Dados

### Fluxo de Inicialização

```
1. docker-compose up
2. Postgres inicia → healthcheck (pg_isready)
3. API inicia → cosome api gov e faz o sync inicial de dados → banco polpulado → healthcheck (/ready)
4. Streamlit inicia (depende de API healthy)
5. Jupyter inicia (depende de API healthy)
```


## Comandos Úteis

### Gerenciamento de Containers

```bash
docker compose up -d                    # Iniciar todos
docker compose up -d --build           # Rebuild e iniciar
docker compose down                     # Parar (mantém dados)
docker compose down -v                  # Parar e apagar volumes
docker compose ps                       # Status dos containers
docker compose logs -f                  # Logs em tempo real
docker compose logs -f api             # Logs apenas da API
docker compose restart streamlit       # Reiniciar serviço específico
```

## Implementações Destacadas

### Cliente API Robusto
- Paginação transparente com async generator
- Rate limiting inteligente (1s delay)
- Retry automático com backoff exponencial
- Timeout configurável

### Pipeline ETL Completo
- Extração assíncrona eficiente
- Normalização e validação de dados
- Deduplicação automática
- Tratamento de erros robusto

### Análise Modular
- Classes reutilizáveis
- Separação de responsabilidades
- Cache inteligente (Streamlit)
- Visualizações interativas

### Infraestrutura Profissional
- Healthchecks garantem ordem correta
- Volume persistente para dados
- Rede isolada Docker
- Configuração via .env

## Testes Realizados

- Sistema completo rodando em 4 containers Docker
- Healthchecks funcionando corretamente
- Sincronização de 100+ projetos do DF
- Todos os endpoints REST funcionando
- Dashboard Streamlit com 5 seções
- Jupyter Notebook com todas as análises
- Gráficos Plotly interativos
- Banco normalizado 3NF com relacionamentos
- Deduplicação automática implementada
- Documentação completa da arquitetura

## Correções e Melhorias Implementadas

Durante o desenvolvimento, as seguintes correções foram necessárias:

1. **BigInteger para códigos**: Códigos de executores/tomadores/repassadores podem ter mais de 10 dígitos, então foram alterados de `Integer` para `BigInteger`

2. **Campo BIM opcional**: O campo `isModeladaPorBim` pode vir como `null` da API externa, alterado de `bool` para `Optional[bool]`

3. **Deduplicação de relacionamentos**: API externa pode retornar duplicados, implementada deduplicação antes de inserir no banco

4. **SQLAlchemy text()**: A partir do SQLAlchemy 2.0, queries SQL literais precisam usar `text()` wrapper

5. **sync_time como string**: O campo `sync_time` retorna um `timedelta`, convertido para string na resposta da API

6. **Healthcheck /ready**: Implementado endpoint que verifica se banco está populado antes de liberar Streamlit e Jupyter

7. **Sync condicional**: Adicionado para evitar re-sync desnecessário quando banco já possui dados

