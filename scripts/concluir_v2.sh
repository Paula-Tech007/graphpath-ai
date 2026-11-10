#!/usr/bin/env bash
# Execução final sob controle do usuário: prepara, testa, indexa, valida GraphRAG e marca o roadmap.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo 'ERRO: arquivo .env ausente. Configure o Neo4j do MVP primeiro.'
  exit 1
fi

if [ -d .venv ] && [ -x .venv/bin/python ]; then
  PYTHON=.venv/bin/python
else
  PYTHON=python3
fi

printf '\n[1/6] Cenário fictício ampliado (preserva GP_*)\n'
"$PYTHON" -m graphpath_v2.cli seed-expanded
printf '\n[2/6] Regressão e testes novos\n'
"$PYTHON" -m unittest discover -s tests -v
printf '\n[3/6] Neo4j real / Graph Data Science\n'
RUN_GRAPH_E2E=1 "$PYTHON" -m unittest tests.test_v2_e2e -v
printf '\n[4/6] Embeddings / índice vetorial no Neo4j\n'
"$PYTHON" -m graphpath_v2.cli index
printf '\n[5/6] GraphRAG real + Qwen (pode demorar)\n'
RUN_GRAPH_E2E=1 RUN_OLLAMA_E2E=1 "$PYTHON" -m unittest tests.test_v2_e2e -v
printf '\n[6/6] API real e painel\n'
"$PYTHON" - <<'PY'
from fastapi.testclient import TestClient
from graphpath_v2.api import app
with TestClient(app) as client:
    for url, key, expected in [
        ('/api/health', 'ok', True),
        ('/api/graph?scenario=base', 'scenario', 'base'),
        ('/api/graph?scenario=expanded', 'scenario', 'expanded')
    ]:
        result=client.get(url)
        assert result.status_code == 200, (url, result.status_code, result.text[:200])
        assert result.json()[key] == expected, (url, result.json())
    graph=client.get('/api/graph?scenario=expanded').json()
    assert (len(graph['nodes']), len(graph['edges'])) == (32,60)
    paths=client.get('/api/paths?scenario=base&source=GP-EXT&target=GP-DB').json()
    assert len(paths['paths'])==2
    ranking=client.get('/api/centrality?scenario=expanded')
    assert ranking.status_code==200 and len(ranking.json()['centrality'])==32
    assert client.get('/').status_code==200
    print('API / dashboard / dois cenários: OK')
PY

"$PYTHON" scripts/fechar_roadmap_v2.py
printf '\n=== VALIDACAO COMPLETA; ROADMAP ATUALIZADO LOCALMENTE ===\n'
printf 'Confira: git status --short && git diff -- README.md\n'
printf 'Depois publique com: git add README.md graphpath_v2 tests scripts docs requirements-v2.txt .github/workflows/ci-v2.yml && git diff --cached --check && git commit -m "feat: GraphPath AI v0.2 API GraphRAG and expanded lab" && git push origin main\n'
