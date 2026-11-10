#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

temporario="$(mktemp "${PWD}/.evidencias.XXXXXX")"
trap 'rm -f "$temporario"' EXIT

echo "=== COLETANDO EVIDENCIAS REAIS DO GRAFO ==="

{
    echo "CAMINHOS:"

    docker compose exec -T neo4j sh -c \
    'cypher-shell -u neo4j -p "${NEO4J_AUTH#*/}"' <<'CYPHER_CAMINHOS'
MATCH (ext:Identity {id:'GP-EXT'})
      -[:HAS_ACCESS]->(web:Asset)
MATCH p=(web)-[:CAN_REACH*1..3]->
      (:Asset {id:'GP-DB'})
RETURN [ext.id] + [n IN nodes(p) | n.id]
       AS caminho
ORDER BY caminho;
CYPHER_CAMINHOS

    echo
    echo "CENTRALIDADE GDS:"

    docker compose exec -T neo4j sh -c \
    'cypher-shell -u neo4j -p "${NEO4J_AUTH#*/}"' <<'CYPHER_GDS'
CALL gds.betweenness.stream('graphpath-ai')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS ativo,
       score AS centralidade
ORDER BY centralidade DESC, ativo;
CYPHER_GDS

    echo
    echo "IMPACTO:"

    docker compose exec -T neo4j sh -c \
    'cypher-shell -u neo4j -p "${NEO4J_AUTH#*/}"' <<'CYPHER_IMPACTO'
MATCH p=(:Identity {id:'GP-EXT'})
  -[:HAS_ACCESS|CAN_REACH*1..4]->
  (:Asset {id:'GP-DB'})
WITH collect(p) AS caminhos
RETURN size(caminhos) AS caminhos_atuais,
       size([p IN caminhos
         WHERE none(n IN nodes(p)
         WHERE n.id='GP-WEB')])
       AS caminhos_sem_gp_web;
CYPHER_IMPACTO

} > "$temporario"

mv "$temporario" evidencias.txt

echo "Evidencias atualizadas."
echo "Gerando relatorio tecnico..."

python3 consolidar_relatorio.py

echo "Executando testes..."
python3 -m unittest discover -s tests -v

echo "=== COLETA E VALIDACAO CONCLUIDAS ==="
