#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo '[1/4] Sintaxe Python e Bash'
.venv/bin/python -m compileall -q graphpath_v2 tests
bash -n scripts/validar_v2.sh
echo '[2/4] Testes unitários e regressão do MVP'
.venv/bin/python -m unittest discover -s tests -v
echo '[3/4] Testes ponta a ponta com Neo4j real'
RUN_GRAPH_E2E=1 .venv/bin/python -m unittest tests.test_v2_e2e -v
echo '[4/4] Status do laboratório'
.venv/bin/python -m graphpath_v2.cli status
echo '=== VALIDAÇÃO V2 APROVADA (Neo4j, sem exigir Ollama) ==='
echo 'Para testar GraphRAG: .venv/bin/python -m graphpath_v2.cli index && RUN_OLLAMA_E2E=1 .venv/bin/python -m unittest tests.test_v2_e2e -v'
