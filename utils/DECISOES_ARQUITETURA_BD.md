# Decisões de Arquitetura do Banco de Dados

## Contexto do Projeto

Projeto de extração e análise de dados da API pública do ObrasGov.br (Distrito Federal), com foco em análise de dados de projetos de investimento público.

---

## Decisão 1: PostgreSQL vs SQLite

### Análise Inicial
- **SQLite**: Suporta JSON como TEXT, mas sem indexação eficiente
- **PostgreSQL**: Tipo JSONB nativo, indexação GIN, operadores avançados

### Decisão Final: **PostgreSQL**

**Motivos:**
-  Melhor performance para análise de dados
-  Tipo JSONB com indexação eficiente
-  Queries SQL mais simples e poderosas
-  Escalabilidade (se dados crescerem)
-  Ideal para análises complexas no Jupyter

---

## Decisão 2: Estrutura Inicial (JSONB vs Normalizada)

### Primeira Proposta: Armazenar Arrays como JSONB

**Estrutura:**
```sql
projetos_investimento (
    id, nome, ...,
    executores JSONB,  -- [{"nome": "IFPI", "codigo": 26431}]
    tomadores JSONB,
    repassadores JSONB,
    ...
)
```

**Vantagens:**
- Simples de implementar
- Mantém estrutura exatamente como vem da API
- Menos tabelas

**Desvantagens:**
-  Dados duplicados (IFPI aparece N vezes)
-  Queries complexas para análise
-  Difícil responder: "Quais projetos o executor X tem?"
-  Performance inferior para agregações

### Mudança de Decisão: **Estrutura Normalizada**

**Motivo da Mudança:**
> "Esses dados de tomadores, executores, repassadores, eixos, tipos e subtipos e fonte de recursos, serão os principais gráficos, pois eles que possuem maior importância para a sociedade no geral"

**Análises prioritárias:**
- TOP 10 executores com mais projetos
- Valor total por repassador
- Distribuição por eixo/tipo
- Gráficos de fontes de recurso

**Decisão Final: Estrutura 100% Normalizada**

---

## Decisão 3: Estrutura Final do Banco

### Arquitetura Normalizada (14 tabelas)

#### 1. Tabela Principal
**`projetos_investimento`**: Dados únicos de cada projeto

#### 2. Tabelas de Entidades (6 tabelas)
- `executores`: Instituições que executam obras
- `tomadores`: Instituições que tomam recursos
- `repassadores`: Órgãos que repassam recursos
- `eixos`: Classificação macro (Administrativo, Social, etc)
- `tipos`: Tipo específico dentro de um eixo (Educação, Saúde)
- `subtipos`: Subtipo específico (Instituições Federais, etc)

#### 3. Tabelas de Relacionamento Many-to-Many (6 tabelas)
- `projeto_executor`
- `projeto_tomador`
- `projeto_repassador`
- `projeto_eixo`
- `projeto_tipo`
- `projeto_subtipo`

#### 4. Tabela Especial One-to-Many
**`fontes_recurso`**: Cada projeto pode ter múltiplas fontes com valores específicos

---

## Decisão 4: Tipos de Dados dos Campos

### Campos Analisados Individualmente

#### 4.1. `idUnico`
**Dados reais:** `"21103.22-77"` (11 caracteres)

**Decisões:**
-  Proposta inicial: `String(50)` - muito espaço desperdiçado
-  **Decisão final: `String(20)`** - dobro do tamanho real, margem segura

---

#### 4.2. `nome`
**Dados reais:** Máximo 181 caracteres

**Decisões:**
-  Proposta inicial: `String(500)` - excesso de espaço
-  Ajuste intermediário: `String(250)` - ainda poderia truncar nomes longos
-  **Decisão final: `String(350)`** - margem de segurança de 93% sobre o máximo

---

#### 4.3. `cep`
**Dados reais:** `"64.501-936"` (10 caracteres fixos)

**Decisões:**
-  Proposta inicial: `String(20)` - desperdício
-  **Decisão final: `String(10)` nullable** - tamanho exato, muitos valores NULL

**Discussão importante:**
- Optamos por armazenar **com formatação** (pontos e hífens)
- Mantém dados exatamente como vêm da API
- Alternativa seria remover formatação e usar `String(8)`, mas decidimos pela fidelidade aos dados originais

---

#### 4.4. `endereco`, `descricao`, `funcaoSocial`, `metaGlobal`
**Dados reais:** Variáveis, até 200+ caracteres, alguns com múltiplos parágrafos

**Decisões:**
-  Considerar `String(300)` com limite
-  **Decisão final: `Text` nullable** - sem limite, aceita qualquer tamanho

**Motivo:** Campo `metaGlobal` pode ser curto ("Construção de UBS") ou extremamente longo (1500+ caracteres com justificativas detalhadas)

---

#### 4.5. Campos de Data
**Dados reais:** `"2023-08-25"` (formato ISO, apenas data, sem hora)

**Decisão: `Date` (não `DateTime`)**

**Campos:**
- `data_inicial_prevista`: `Date` nullable
- `data_final_prevista`: `Date` nullable
- `data_inicial_efetiva`: `Date` nullable
- `data_final_efetiva`: `Date` nullable
- `data_cadastro`: `Date` nullable
- `data_situacao`: `Date` nullable

**Motivo:** API não retorna hora, apenas data. `Date` é ideal para análises temporais (agrupar por ano/mês, calcular durações).

---

#### 4.6. Campos Categóricos
**Campos:** `especie`, `natureza`, `situacao`

**Dados reais:** Valores curtos ("Construção", "Obra", "Cadastrada")

**Decisão: `String(100)` nullable**

**Motivo:** São campos categóricos com valores previsíveis e curtos.

---

#### 4.7. `uf`
**Dados reais:** `"PI"`, `"DF"` (sempre 2 caracteres)

**Decisão: `String(2)` indexado**

**Motivo crítico:** Campo essencial para filtros e análises por região. Indexação garante queries rápidas.

---

#### 4.8. `qdtEmpregosGerados` e `populacaoBeneficiada`
**Dados reais:** Vêm como **STRING** na API: `"30"`, `"2000"`

**Decisões:**
-  **NÃO converter para Integer no banco**
-  **Decisão: `String(50)` nullable**

**Motivo estratégico:**
- Armazenar exatamente como vem da API (fidelidade aos dados)
- Conversão para Integer será feita **apenas na análise** (Jupyter/SQL):

```python
# Na análise
df['qdt_empregos_gerados'] = pd.to_numeric(df['qdt_empregos_gerados'], errors='coerce')
```

```sql
-- Em queries SQL
SELECT CAST(qdt_empregos_gerados AS INTEGER) as empregos_int
FROM projetos_investimento
WHERE qdt_empregos_gerados IS NOT NULL;
```

---

#### 4.9. `isModeladaPorBim`
**Dados reais:** `true`, `false`

**Decisão: `Boolean`**

**Motivo:** Valor booleano puro, PostgreSQL tem tipo BOOLEAN nativo.

---

#### 4.10. Campos de Arrays (executores, tomadores, etc)

**Dados reais:**
```json
"executores": [{"nome": "IFPI", "codigo": 26431}]
"fontesDeRecurso": [{"origem": "Federal", "valorInvestimentoPrevisto": 1567428.79}]
```

**Decisão Inicial: `JSON` (JSONB no PostgreSQL)**

**Decisão Final: Normalização em Tabelas Separadas**

**Discussão crítica:**

*"Um executor pode ter diversas obras, correto? Não seria interessante armazenar uma linha, com quais obras cada executor tem?"*

**Comparação:**

| Aspecto | JSONB | Normalizado |
|---------|-------|-------------|
| Duplicação |  IFPI aparece N vezes |  IFPI aparece 1 vez |
| Query "Projetos do executor X" |  Complexa |  Simples |
| Performance análise |  Lenta |  Rápida |
| Implementação |  Simples |  Complexa |
| Gráficos/Agregações |  Difícil |  Trivial |

**Exemplo de diferença:**

```sql
-- JSONB (complexo)
SELECT
    jsonb_array_elements(executores)->>'nome' as executor,
    COUNT(*) as total
FROM projetos_investimento
GROUP BY executor;

-- Normalizado (simples)
SELECT e.nome, COUNT(*) as total
FROM executores e
JOIN projeto_executor pe ON e.id = pe.executor_id
GROUP BY e.nome;
```

**Decisão Final: Normalizado**, pois análise de dados é **prioridade máxima**.

---

## Decisão 5: Campos de Auditoria

### `id`, `created_at`, `updated_at`

**Discussão:**
> "Com essa estratégia da normalização, precisaremos do campo 32 até 34?"

#### Campo `id` (Integer PK autoincrement)
**Decisão:  OBRIGATÓRIO**

**Motivo:**
- Usado como Foreign Key em todas as tabelas de relacionamento
- Mais rápido que usar `id_unico` (string) como FK
- Auto-incremento facilita inserções
- Performance superior em JOINs

#### Campos `created_at` e `updated_at`
**Decisão:  Apenas em `projetos_investimento`**

**Motivos:**
-  Rastrear quando dados foram sincronizados
-  Identificar projetos desatualizados
-  Debugging e auditoria
-  Custo praticamente zero

**Tabelas que NÃO têm timestamp:**
-  Entidades (executores, tomadores, etc): dados de cadastro básico, raramente mudam
-  Tabelas de relacionamento: são inseridos/deletados, não atualizados
-  Fontes de recurso: geralmente estáticos por projeto

---

## Decisão 6: Relacionamentos SQLAlchemy

### Relationships Bidirecionais

```python
# Em ProjetoInvestimento
executores = relationship("Executor", secondary="projeto_executor", back_populates="projetos")

# Em Executor
projetos = relationship("ProjetoInvestimento", secondary="projeto_executor", back_populates="executores")
```

**Vantagens:**
-  Acesso bidirecional: `projeto.executores` e `executor.projetos`
-  ORM gerencia automaticamente os relacionamentos
-  Facilita queries e navegação entre entidades

### Cascade Delete

```python
fontes_recurso = relationship("FonteRecurso", back_populates="projeto", cascade="all, delete-orphan")
```

**Decisão:** Apenas em `fontes_recurso`

**Motivo:** Se projeto é deletado, suas fontes devem ser deletadas também (dependência forte).

**Outras tabelas:** Sem cascade, pois entidades (executores, tomadores, etc) são independentes e podem existir sem projetos.

---

## Decisão 7: Índices

### Campos Indexados

1. **`projetos_investimento.id`**: PK (índice automático)
2. **`projetos_investimento.id_unico`**: Único, indexado (buscas frequentes)
3. **`projetos_investimento.uf`**: Indexado (filtros por região)
4. **`executores.codigo`**: Único, indexado
5. **`tomadores.codigo`**: Único, indexado
6. **`repassadores.codigo`**: Único, indexado

**Motivo:** Campos usados em WHERE, JOIN e GROUP BY precisam de índices para performance.

---

## Decisão 8: Hierarquia de Classificação

### Estrutura Hierárquica

```
Eixo (Administrativo)
  └── Tipo (Educação)
      └── Subtipo (Instituições Federais de Ensino Superior)
```

### Implementação

```python
class Tipo(Base):
    eixo_id = Column(Integer, ForeignKey("eixos.id"))
    eixo = relationship("Eixo", back_populates="tipos")

class Subtipo(Base):
    tipo_id = Column(Integer, ForeignKey("tipos.id"))
    tipo = relationship("Tipo", back_populates="subtipos")
```

**Decisão:** Foreign Keys diretas (tipo → eixo, subtipo → tipo)

**Vantagem:** Reflete a hierarquia real dos dados, permite queries como:

```sql
-- Projetos por eixo, incluindo tipos e subtipos
SELECT e.descricao as eixo, t.descricao as tipo, COUNT(*) as total
FROM eixos e
JOIN tipos t ON t.eixo_id = e.id
JOIN projeto_tipo pt ON pt.tipo_id = t.id
GROUP BY e.descricao, t.descricao;
```

---

## Resumo das Decisões Finais

### Arquitetura
-  PostgreSQL (não SQLite)
-  Estrutura 100% normalizada (não JSONB)
-  14 tabelas relacionadas

### Tipos de Dados
-  Strings com tamanhos ajustados aos dados reais
-  Text para campos variáveis/longos
-  Date (não DateTime) para datas
-  Campos numéricos armazenados como String (conversão na análise)

### Performance
-  Índices em campos de busca/filtro
-  Foreign Keys otimizadas (Integer, não String)
-  Relationships bidirecionais

### Auditoria
-  id, created_at, updated_at apenas na tabela principal

---

## Benefícios da Arquitetura Final

### Para Análise de Dados
 Queries SQL simples e rápidas
 Agregações triviais (COUNT, SUM, AVG)
 Gráficos fáceis de gerar
 Pandas trabalha nativamente com dados relacionais

### Para Manutenção
 Sem duplicação de dados
 Consistência garantida por FKs
 Fácil adicionar novos campos
 Estrutura clara e organizada

### Para Performance
 Índices otimizados
 JOINs eficientes
 Queries rápidas mesmo com milhares de registros

---

## Exemplo de Query Complexa (Simples com Normalização)

```sql
-- TOP 10 executores com maior valor total de investimento
SELECT
    e.nome as executor,
    COUNT(DISTINCT p.id) as total_projetos,
    SUM(fr.valor_investimento_previsto) as investimento_total
FROM executores e
JOIN projeto_executor pe ON e.id = pe.executor_id
JOIN projetos_investimento p ON p.id = pe.projeto_id
JOIN fontes_recurso fr ON fr.projeto_id = p.id
WHERE p.uf = 'DF'
GROUP BY e.nome
ORDER BY investimento_total DESC
LIMIT 10;
```

**Com JSONB, essa query seria muito mais complexa e lenta.**

---

## Conclusão

A arquitetura final foi desenhada especificamente para **análise de dados**, priorizando:
- Performance em queries analíticas
- Facilidade de criar visualizações
- Consistência e integridade dos dados
- Escalabilidade para crescimento futuro

Todas as decisões foram baseadas em análise dos dados reais da API e nas necessidades do projeto.
