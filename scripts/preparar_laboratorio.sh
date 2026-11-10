#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== GRAPHPATH AI - PREPARACAO ==="

if [ ! -f .env ]; then
    echo "ERRO: configure o arquivo .env primeiro."
    exit 1
fi

consultar() {
    printf '%s\n' "$1" |
    docker compose exec -T neo4j sh -c \
    'cypher-shell -u neo4j -p "${NEO4J_AUTH#*/}"'
}

echo "[1/4] Validando Docker Compose..."
docker compose config --quiet

echo "[2/4] Iniciando Neo4j..."
docker compose up -d

echo "Aguardando banco ficar disponivel..."

pronto=0
for tentativa in $(seq 1 45); do
    if consultar "RETURN 1 AS ok;" >/dev/null 2>&1; then
        pronto=1
        break
    fi
    sleep 2
done

if [ "$pronto" -ne 1 ]; then
    echo "ERRO: Neo4j nao respondeu."
    exit 1
fi

echo "[3/4] Carregando dados ficticios..."
docker compose exec -T neo4j sh -c \
'cypher-shell -u neo4j -p "${NEO4J_AUTH#*/}"' \
< seed.cypher

echo "[4/4] Verificando projecao GDS..."

if consultar \
"RETURN gds.graph.exists('graphpath-ai') AS existe;" \
| tail -n 1 | grep -qi '^true$'; then
    echo "Projecao GDS ja existe."
else
    echo "Criando projecao GDS..."

    consultar "
    CALL gds.graph.project(
      'graphpath-ai',
      ['Identity', 'Asset'],
      ['HAS_ACCESS', 'CAN_REACH']
    )
    YIELD graphName, nodeCount, relationshipCount
    RETURN graphName, nodeCount, relationshipCount;
    "
fi

echo ""
echo "=== LABORATORIO PREPARADO ==="
