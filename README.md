# Data Pipeline - ObrasGov API

API para extração, tratamento e armazenamento de dados de projetos de investimento público do Distrito Federal, consumidos da API do ObrasGov.br.

## Arquitetura do Projeto

```
Data-Pipeline/
├── api/
│   ├── __init__.py
│   ├── main.py              # Endpoints FastAPI
│   ├── config.py            # Configurações e variáveis de ambiente
│   ├── models.py            # Modelos SQLAlchemy (14 tabelas)
│   ├── schemas.py           # Schemas Pydantic para validação
│   ├── database.py          # Operações de banco de dados
│   └── services/
│       ├── __init__.py
│       ├── obrasgov_client.py   # Cliente HTTP para API externa
│       └── data_processor.py    # Processamento e normalização de dados
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── DECISOES_ARQUITETURA_BD.md
└── README.md
```

## Características

-  Estrutura de banco de dados **100% normalizada** (14 tabelas relacionadas)
-  Consumo assíncrono da API com retry e backoff exponencial
-  Tratamento robusto de erros e timeout
-  Sincronização automática agendada (scheduler)
-  Separação de responsabilidades (services pattern)
-  PostgreSQL com JSONB para análises avançadas
-  Documentação interativa (Swagger UI)

## Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- PostgreSQL 15 (via Docker)

## Instalação

### 1. Clonar o repositório

```bash
git clone <repo-url>
cd Data-Pipeline
```

### 2. Criar arquivo .env

```bash
cp .env.example .env
```

Edite o `.env` conforme necessário.

### 3. Subir os containers (PostgreSQL + API)

```bash
docker compose up -d --build
```

Isso irá:
- Criar o container PostgreSQL na porta 5432
- Criar o container da API na porta 8000
- Aguardar o PostgreSQL estar saudável antes de iniciar a API
- Criar automaticamente todas as 14 tabelas do banco

## Uso

### Verificar status dos containers

```bash
docker ps
```

Você deve ver:
- `obrasgov_postgres` - running (healthy)
- `obrasgov_api` - running

A API estará disponível em: `http://localhost:8000`

Documentação interativa: `http://localhost:8000/docs`

### Desenvolvimento local (sem Docker)

Se preferir rodar localmente sem Docker:

```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar apenas PostgreSQL via Docker
docker compose up -d postgres

# Rodar API localmente
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Endpoints Disponíveis

#### 1. Health Check
```bash
GET /health
```

Verifica status da API e conexão com banco de dados.

#### 2. Sincronizar Projetos
```bash
POST /sync?uf=DF
```

**Parâmetros:**
- `uf` (opcional): Estado a ser sincronizado (padrão: DF)

**Resposta:**
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

**Observações:**
- A API implementa deduplicação automática de relacionamentos
- Executores, tomadores e repassadores duplicados no mesmo projeto são ignorados
- O campo `isModeladaPorBim` aceita valores nulos da API externa
- Códigos de executores/tomadores/repassadores suportam BigInteger (valores > 2 bilhões)

#### 3. Listar Projetos
```bash
GET /projetos?skip=0&limit=100&uf=DF
```

**Parâmetros:**
- `skip` (opcional): Número de registros a pular (paginação)
- `limit` (opcional): Quantidade de registros (padrão: 100)
- `uf` (opcional): Filtrar por UF

#### 4. Buscar Projeto Específico
```bash
GET /projetos/{id_unico}
```

**Exemplo:**
```bash
GET /projetos/21103.22-77
```

## Sincronização Automática

A API está configurada para sincronizar automaticamente os dados:

- **Horário:** 2h da manhã (UTC)
- **Frequência:** Diária
- **Configurável:** Edite `SYNC_SCHEDULE_HOUR` e `SYNC_SCHEDULE_MINUTE` no `.env`

## Estrutura do Banco de Dados

### Tabelas Principais

1. **projetos_investimento** - Dados principais dos projetos (34 colunas)
2. **executores** - Instituições que executam obras
3. **tomadores** - Instituições que tomam recursos
4. **repassadores** - Órgãos que repassam recursos
5. **eixos** - Eixos de classificação
6. **tipos** - Tipos de projeto
7. **subtipos** - Subtipos de projeto
8. **fontes_recurso** - Fontes e valores de investimento
9-14. **Tabelas de relacionamento** (Many-to-Many)

Para detalhes completos sobre as decisões de arquitetura, consulte: [`DECISOES_ARQUITETURA_BD.md`](./DECISOES_ARQUITETURA_BD.md)

## Análise de Dados

### Exemplos de Queries SQL

#### TOP 10 Executores
```sql
SELECT e.nome, COUNT(*) as total_projetos
FROM executores e
JOIN projeto_executor pe ON e.id = pe.executor_id
GROUP BY e.nome
ORDER BY total_projetos DESC
LIMIT 10;
```

#### Valor Total por Repassador
```sql
SELECT r.nome, SUM(fr.valor_investimento_previsto) as total
FROM repassadores r
JOIN projeto_repassador pr ON r.id = pr.repassador_id
JOIN fontes_recurso fr ON pr.projeto_id = fr.projeto_id
GROUP BY r.nome;
```

#### Distribuição por Tipo
```sql
SELECT t.descricao, COUNT(*) as total
FROM tipos t
JOIN projeto_tipo pt ON t.id = pt.tipo_id
GROUP BY t.descricao;
```

### Integração com Pandas

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://obrasgov_user:obrasgov_pass@localhost:5432/obrasgov_db")

# Carregar dados
df = pd.read_sql("SELECT * FROM projetos_investimento", engine)

# Converter campos numéricos
df['empregos'] = pd.to_numeric(df['qdt_empregos_gerados'], errors='coerce')
df['populacao'] = pd.to_numeric(df['populacao_beneficiada'], errors='coerce')

# Análises
print(df.groupby('uf')['empregos'].sum())
```

## Troubleshooting

### Erro: "database does not exist"
```bash
docker compose down -v
docker compose up -d --build
```

### Erro: "port 5432 already in use"
Verifique containers PostgreSQL em execução:
```bash
docker ps -a | grep postgres
```

Pare o container conflitante:
```bash
docker stop <container_name>
docker rm <container_name>
```

Ou edite `POSTGRES_PORT` no `.env` e no `docker-compose.yml`

### Erro de timeout na API
Aumente `OBRASGOV_API_TIMEOUT` no `.env` e rebuilde o container:
```bash
docker compose up -d --build api
```

### Resetar banco de dados
```bash
docker compose down -v
docker compose up -d --build
```

### Ver logs da API
```bash
docker logs obrasgov_api -f
```

### Ver logs do PostgreSQL
```bash
docker logs obrasgov_postgres -f
```

### Acessar banco de dados
```bash
docker exec -it obrasgov_postgres psql -U obrasgov_user -d obrasgov_db
```

## Variáveis de Ambiente

Consulte `.env.example` para ver todas as configurações disponíveis:

- **Banco de Dados:** POSTGRES_*
- **API Externa:** OBRASGOV_API_*
- **Agendamento:** SYNC_SCHEDULE_*

## Comandos Docker Úteis

### Gerenciamento de Containers

```bash
# Iniciar containers
docker compose up -d

# Parar containers (mantém dados)
docker compose stop

# Parar e remover containers (mantém dados)
docker compose down

# Parar, remover containers E volumes (apaga dados)
docker compose down -v

# Rebuildar e iniciar
docker compose up -d --build

# Rebuildar apenas API
docker compose up -d --build api

# Ver status
docker compose ps
docker ps
```

### Monitoramento

```bash
# Logs em tempo real
docker compose logs -f

# Logs apenas da API
docker logs obrasgov_api -f

# Logs apenas do PostgreSQL
docker logs obrasgov_postgres -f

# Estatísticas de uso
docker stats
```

### Comandos SQL

```bash
# Acessar psql
docker exec -it obrasgov_postgres psql -U obrasgov_user -d obrasgov_db

# Executar query direto
docker exec obrasgov_postgres psql -U obrasgov_user -d obrasgov_db -c "SELECT COUNT(*) FROM projetos_investimento;"

# Listar tabelas
docker exec obrasgov_postgres psql -U obrasgov_user -d obrasgov_db -c "\dt"
```

## Desenvolvimento

### Estrutura de Services

O projeto segue o padrão de separação de responsabilidades:

- **`ObrasGovClient`**: Responsável apenas por consumir a API externa
- **`DataProcessor`**: Responsável por transformar e salvar dados
- **`main.py`**: Apenas orquestra os services e expõe endpoints

### Adicionar Novos Endpoints

1. Defina o schema de resposta em `schemas.py`
2. Adicione o endpoint em `main.py`
3. Se necessário, crie lógica no `services/`

## Testes Realizados

 API rodando em containers Docker
 Health check funcionando
 Sincronização de 100+ projetos do DF
 Endpoints de listagem e busca funcionando
 Banco de dados com 14 tabelas normalizadas
 Relacionamentos Many-to-Many funcionando
 Deduplicação automática implementada
 Documentação Swagger disponível

## Próximos Passos

- [ ] Sincronizar todos os projetos do DF (todas as páginas)
- [ ] Criar Jupyter Notebook para análise exploratória
- [ ] Implementar visualizações com Matplotlib/Seaborn
- [ ] Gerar relatório final com insights
- [ ] Implementar filtros avançados nos endpoints

## Correções e Melhorias Implementadas

Durante o desenvolvimento, as seguintes correções foram necessárias:

1. **BigInteger para códigos**: Códigos de executores/tomadores/repassadores podem ter mais de 10 dígitos (ex: 394676000107), por isso foram alterados de `Integer` para `BigInteger`

2. **Campo BIM opcional**: O campo `isModeladaPorBim` pode vir como `null` da API externa, então foi alterado de `bool` para `Optional[bool]`

3. **Deduplicação de relacionamentos**: A API externa pode retornar eixos/tipos/subtipos duplicados para o mesmo projeto, então implementamos deduplicação usando dicionários antes de inserir no banco

4. **SQLAlchemy text()**: A partir do SQLAlchemy 2.0, queries SQL literais precisam usar `text()` wrapper

5. **sync_time como string**: O campo `sync_time` retorna um `timedelta`, convertido para string na resposta da API

## Licença

MIT

## Contato

Dúvidas: @davi_aguiar_vieira ou @mateus_castro3 (Telegram)
