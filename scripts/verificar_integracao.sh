#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "================================="
echo " GRAPHPATH AI - VALIDACAO"
echo "================================="

if [ ! -f .env ]; then
    echo "ERRO: arquivo .env ausente."
    exit 1
fi

echo ""
echo "[1/5] Verificando Neo4j..."

if ! docker compose ps --status running \
    --services | grep -qx neo4j; then
    echo "ERRO: Neo4j nao esta em execucao."
    exit 1
fi

consultar() {
    docker compose exec -T neo4j sh -c \
    'cypher-shell -u neo4j -p "${NEO4J_AUTH#*/}"' \
    <<< "$1"
}

consultar "RETURN 1 AS conexao_ok;"

echo ""
echo "[2/5] Verificando Graph Data Science..."

consultar "RETURN gds.version() AS versao_gds;"

echo ""
echo "[3/5] Verificando dados do grafo..."

consultar "
MATCH (n)
RETURN count(n) AS total_nos;
"

consultar "
MATCH ()-[r]->()
RETURN count(r) AS total_relacionamentos;
"

echo ""
echo "[4/5] Verificando projecao GDS..."

consultar "
RETURN gds.graph.exists('graphpath-ai')
AS projecao_ativa;
"

echo ""
echo "[5/5] Executando testes Python..."

python3 -m unittest discover -s tests -v

echo ""
echo "================================="
echo " VALIDACAO FINALIZADA"
echo "================================="
