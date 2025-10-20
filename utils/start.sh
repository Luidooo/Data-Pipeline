#!/bin/bash

set -e

echo "=========================================="
echo "  Data Pipeline - ObrasGov DF"
echo "  Script de Inicialização"
echo "=========================================="
echo ""

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "ERRO: $1 não encontrado. Por favor, instale o $2"
        exit 1
    fi
}

echo "[1/6] Verificando dependências..."
check_command "docker" "Docker"

if ! docker compose version &> /dev/null; then
    echo "ERRO: docker compose não encontrado. Por favor, instale o Docker Compose v2"
    exit 1
fi

echo "  Docker: OK"
echo "  Docker Compose: OK"
echo ""

echo "[2/6] Verificando arquivo .env..."
if [ ! -f .env ]; then
    echo "  Arquivo .env não encontrado. Criando a partir de .env.example..."
    cp .env.example .env
    echo "  .env criado com sucesso!"
    echo "  ATENÇÃO: Revise as configurações em .env se necessário"
else
    echo "  .env encontrado: OK"
fi
echo ""

echo "[3/6] Verificando portas necessárias..."
PORTAS=(5455 8000 8501 8888)
PORTAS_EM_USO=()

for porta in "${PORTAS[@]}"; do
    if lsof -Pi :$porta -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        PORTAS_EM_USO+=($porta)
    fi
done

if [ ${#PORTAS_EM_USO[@]} -gt 0 ]; then
    echo "  AVISO: As seguintes portas estão em uso: ${PORTAS_EM_USO[*]}"
    echo "  Você pode precisar parar os containers antigos com: docker compose down"
    echo ""
    read -p "  Deseja continuar mesmo assim? (s/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "  Abortado pelo usuário."
        exit 1
    fi
else
    echo "  Portas 5455, 8000, 8501, 8888: Disponíveis"
fi
echo ""

echo "[4/6] Parando containers existentes (se houver)..."
docker compose down 2>/dev/null || true
echo ""

echo "[5/6] Iniciando containers com rebuild..."
echo "  Isso pode levar alguns minutos..."
docker compose up -d --build

echo ""
echo "[6/6] Aguardando inicialização completa..."
echo "  Aguardando PostgreSQL..."
sleep 5

echo "  Aguardando API e sync inicial de dados..."
echo "  (Pode levar até 5 minutos na primeira execução)"

MAX_WAIT=300
ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT ]; do
    if curl -f http://localhost:8000/ready >/dev/null 2>&1; then
        echo "  API pronta!"
        break
    fi
    sleep 10
    ELAPSED=$((ELAPSED + 10))
    echo "  Aguardando... (${ELAPSED}s/${MAX_WAIT}s)"
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
    echo ""
    echo "  AVISO: Timeout aguardando API. Verifique os logs:"
    echo "  docker compose logs -f api"
    exit 1
fi

echo ""
echo "=========================================="
echo "  INICIALIZAÇÃO CONCLUÍDA COM SUCESSO!"
echo "=========================================="
echo ""
echo "Serviços disponíveis:"
echo ""
echo "  FastAPI:         http://localhost:8000"
echo "  FastAPI Docs:    http://localhost:8000/docs"
echo "  Streamlit:       http://localhost:8501"
echo "  JupyterLab:      http://localhost:8888"
echo "  PostgreSQL:      localhost:5455"
echo ""
echo "Comandos úteis:"
echo "  docker compose ps              - Status dos containers"
echo "  docker compose logs -f         - Ver logs em tempo real"
echo "  docker compose logs -f api     - Ver logs apenas da API"
echo "  docker compose down            - Parar todos os containers"
echo "  docker compose down -v         - Parar e remover volumes"
echo ""
