# Arquitetura do Sistema - Data Pipeline ObrasGov DF

## Visão Geral da Arquitetura

```mermaid
flowchart LR
    API_OBRAS["API ObrasGov"]

    POSTGRES[("PostgreSQL
    Porta 5455")]

    FASTAPI["FastAPI
    Porta 8000
    ETL + Scheduler"]

    STREAMLIT["Streamlit
    Porta 8501
    Dashboard"]

    JUPYTER["JupyterLab
    Porta 8888
    Notebook"]

    API_OBRAS -->|"1. HTTP GET"| FASTAPI
    FASTAPI -->|"2. INSERT/UPDATE"| POSTGRES
    POSTGRES -->|"3. SQL Queries"| STREAMLIT
    POSTGRES -->|"3. SQL Queries"| JUPYTER

    FASTAPI -.->|"Sync 8h Brasília"| API_OBRAS

    classDef external fill:#e1f5ff,stroke:#01579b,stroke-width:3px
    classDef database fill:#e8f5e9,stroke:#1b5e20,stroke-width:3px
    classDef service fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef viz fill:#fff3e0,stroke:#e65100,stroke-width:2px

    class API_OBRAS external
    class POSTGRES database
    class FASTAPI service
    class STREAMLIT,JUPYTER viz
```

## Fluxo de Inicialização

```mermaid
sequenceDiagram
    participant User
    participant DockerCompose
    participant Postgres
    participant API
    participant Streamlit
    participant Jupyter
    participant ObrasGovAPI

    User->>DockerCompose: docker-compose up --build

    DockerCompose->>Postgres: Inicia container
    Postgres->>Postgres: Inicializa database
    Postgres->>Postgres: Healthcheck: pg_isready OK

    DockerCompose->>API: Inicia container (depends_on: postgres healthy)
    API->>API: init_db() - Cria tabelas
    API->>ObrasGovAPI: sync_projects(uf="DF")
    ObrasGovAPI-->>API: Retorna projetos (paginação)
    API->>Postgres: INSERT projetos, executores, etc.
    API->>API: Healthcheck: /ready OK

    DockerCompose->>Streamlit: Inicia container (depends_on: api healthy)
    Streamlit->>Postgres: Carrega dados
    Streamlit->>User: Dashboard disponível :8501

    DockerCompose->>Jupyter: Inicia container (depends_on: api healthy)
    Jupyter->>Jupyter: Configura tema dark
    Jupyter->>User: JupyterLab disponível :8888

    User->>API: Acessa /docs (Swagger)
    User->>Streamlit: Visualiza dashboard
    User->>Jupyter: Abre notebook
```

## Pipeline ETL Detalhado

```mermaid
flowchart TB
    subgraph Extract["EXTRACT"]
        E1["Paginação Automática"]
        E2["Rate Limiting 1s"]
        E3["Retry 3x + backoff"]
        E4["Parse JSON"]

        E1 --> E2 --> E3 --> E4
    end

    subgraph Transform["TRANSFORM"]
        T1["DataProcessor"]
        T2["Parse Datas"]
        T3["Get or Create Entidades"]
        T4["Deduplicação"]

        T1 --> T2 --> T3 --> T4

        T3 -.-> T3A["executores, tomadores, repassadores, eixos, tipos, subtipos"]
    end

    subgraph Load["LOAD"]
        L1["Check Duplicata por id_unico"]
        L2["INSERT ou UPDATE projeto"]
        L3["Clear + Append N:N"]
        L4["Delete + Insert fontes_recurso"]
        L5["Flush + Commit por página"]

        L1 --> L2 --> L3 --> L4 --> L5
    end

    subgraph Database["DATABASE"]
        DB1[("projetos_investimento")]
        DB2[("executores, tomadores, repassadores")]
        DB3[("eixos, tipos, subtipos")]
        DB4[("6 tabelas N:N")]
        DB5[("fontes_recurso")]

        DB1 -.-> DB4
        DB4 -.-> DB2
        DB4 -.-> DB3
        DB1 -.-> DB5
    end

    Extract --> Transform --> Load --> Database
```

## Estrutura do Banco de Dados

```mermaid
erDiagram
    PROJETOS_INVESTIMENTO ||--o{ PROJETO_EXECUTOR : ""
    PROJETO_EXECUTOR }o--|| EXECUTORES : ""

    PROJETOS_INVESTIMENTO ||--o{ PROJETO_TOMADOR : ""
    PROJETO_TOMADOR }o--|| TOMADORES : ""

    PROJETOS_INVESTIMENTO ||--o{ PROJETO_REPASSADOR : ""
    PROJETO_REPASSADOR }o--|| REPASSADORES : ""

    PROJETOS_INVESTIMENTO ||--o{ PROJETO_EIXO : ""
    PROJETO_EIXO }o--|| EIXOS : ""

    PROJETOS_INVESTIMENTO ||--o{ PROJETO_TIPO : ""
    PROJETO_TIPO }o--|| TIPOS : ""

    PROJETOS_INVESTIMENTO ||--o{ PROJETO_SUBTIPO : ""
    PROJETO_SUBTIPO }o--|| SUBTIPOS : ""

    PROJETOS_INVESTIMENTO ||--o{ FONTES_RECURSO : "projeto_id"

    EIXOS ||--o{ TIPOS : "eixo_id"
    TIPOS ||--o{ SUBTIPOS : "tipo_id"

    PROJETOS_INVESTIMENTO {
        int id PK
        string id_unico UK
        string nome
        string cep
        text endereco
        text descricao
        text funcao_social
        text meta_global
        date data_inicial_prevista
        date data_final_prevista
        date data_inicial_efetiva
        date data_final_efetiva
        date data_cadastro
        date data_situacao
        string especie
        string natureza
        string natureza_outras
        string situacao
        text desc_plano_nacional_politica_vinculado
        string uf
        string qdt_empregos_gerados
        text desc_populacao_beneficiada
        string populacao_beneficiada
        text observacoes_pertinentes
        boolean is_modelada_por_bim
        datetime created_at
        datetime updated_at
    }

    EXECUTORES {
        int id PK
        string nome
        bigint codigo UK
    }

    TOMADORES {
        int id PK
        string nome
        bigint codigo UK
    }

    REPASSADORES {
        int id PK
        string nome
        bigint codigo UK
    }

    EIXOS {
        int id PK
        string descricao
    }

    TIPOS {
        int id PK
        string descricao
        int eixo_id FK
    }

    SUBTIPOS {
        int id PK
        string descricao
        int tipo_id FK
    }

    FONTES_RECURSO {
        int id PK
        int projeto_id FK
        string origem
        float valor_investimento_previsto
    }

    PROJETO_EXECUTOR {
        int projeto_id PK_FK
        int executor_id PK_FK
    }

    PROJETO_TOMADOR {
        int projeto_id PK_FK
        int tomador_id PK_FK
    }

    PROJETO_REPASSADOR {
        int projeto_id PK_FK
        int repassador_id PK_FK
    }

    PROJETO_EIXO {
        int projeto_id PK_FK
        int eixo_id PK_FK
    }

    PROJETO_TIPO {
        int projeto_id PK_FK
        int tipo_id PK_FK
    }

    PROJETO_SUBTIPO {
        int projeto_id PK_FK
        int subtipo_id PK_FK
    }
```

## Componentes de Análise

```mermaid
graph LR
    subgraph AnalysisModule["Módulo analysis/"]
        DL["DataLoader - Conexão DB"]
        NORM["Normalizador - Limpeza"]
        ANAL["Analisador - Estatísticas"]
        VIS["Visualizador - Gráficos"]
    end

    subgraph Outputs["Outputs"]
        ST["Streamlit Dashboard"]
        JP["Jupyter Notebook"]
    end

    DL --> NORM
    NORM --> ANAL
    ANAL --> VIS
    VIS --> ST
    VIS --> JP

    DL -.->|SQL| DB[("PostgreSQL")]
```

## Stack Tecnológico

```mermaid
mindmap
  root((Data Pipeline ObrasGov DF))
    Backend
      FastAPI
      SQLAlchemy
      PostgreSQL
      APScheduler
      Pydantic
    Frontend
      Streamlit
      JupyterLab
    Visualização
      Plotly
      Matplotlib
      Seaborn
    Análise
      Pandas
      NumPy
    Infraestrutura
      Docker
      Docker Compose
      Healthchecks
    Cliente HTTP
      HTTPX
      Async/Await
      Rate Limiting
```

## Portas e Endpoints

| Serviço | Porta | URL | Descrição |
|---------|-------|-----|-----------|
| **PostgreSQL** | 5455:5432 | `postgresql://localhost:5455/obrasgov_db` | Banco de dados |
| **FastAPI** | 8000:8000 | `http://localhost:8000` | API REST |
| **FastAPI Docs** | 8000:8000 | `http://localhost:8000/docs` | Swagger UI |
| **Streamlit** | 8501:8501 | `http://localhost:8501` | Dashboard |
| **JupyterLab** | 8888:8888 | `http://localhost:8888` | Notebook |

## Endpoints da API

```mermaid
graph TD
    API["/"]

    API --> HEALTH["/health - GET"]
    API --> READY["/ready - GET"]
    API --> SYNC["/sync - POST"]
    API --> PROJETOS["/projetos - GET"]
    API --> PROJETO_ID["/projetos/{id} - GET"]

    HEALTH -.->|200| H_OK["Status: ok - Database: connected"]
    READY -.->|200| R_OK["Status: ready - Projects: count"]
    READY -.->|503| R_FAIL["Database not populated"]
    SYNC -.->|200| S_OK["Total projetos, executores, Sync time"]
    PROJETOS -.->|200| P_OK["Lista paginada - skip, limit, uf"]
    PROJETO_ID -.->|200| PI_OK["Projeto completo"]
    PROJETO_ID -.->|404| PI_FAIL["Projeto não encontrado"]
```

## Agendamento e Automação

```mermaid
gantt
    title Ciclo de Sincronização Automática
    dateFormat HH:mm
    axisFormat %H:%M

    section Sync Diário
    Sync Agendado 8h Brasília      :crit, 08:00, 30m

    section API
    API Running        :active, 00:00, 24h

    section Dashboards
    Streamlit Available :active, 00:00, 24h
    Jupyter Available   :active, 00:00, 24h
```

## Healthchecks e Dependências

```mermaid
graph TD
    START["docker-compose up"]

    START --> PG_START["Postgres inicia"]
    PG_START --> PG_HEALTH{"pg_isready?"}
    PG_HEALTH -->|5 retries| PG_HEALTH
    PG_HEALTH -->|OK Healthy| API_START["API inicia"]

    API_START --> API_SYNC["Sync inicial"]
    API_SYNC --> API_HEALTH{"/ready?"}
    API_HEALTH -->|503: DB vazio| API_HEALTH
    API_HEALTH -->|30 retries| API_HEALTH
    API_HEALTH -->|OK 200: DB populado| SERVICES["Streamlit + Jupyter iniciam"]

    SERVICES --> READY["Sistema Completo"]

    style READY fill:#4caf50,stroke:#2e7d32,stroke-width:3px,color:#fff
    style PG_HEALTH fill:#ff9800,stroke:#e65100
    style API_HEALTH fill:#ff9800,stroke:#e65100
```

---

**Documentação Técnica**
- Todos os containers estão na rede isolada `obrasgov_network`
- Healthchecks garantem ordem de inicialização
- Sync automático executa diariamente às 8h da manhã (Brasília)
- Volume persistente mantém dados do PostgreSQL
