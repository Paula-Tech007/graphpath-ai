# GraphPath AI — Evolução v0.2 / Matrix Security Lab

> Extensão do MVP. Preserva o banner oficial `assets/graphpath-matrix.png`, o grafo original GP-EXT/GP-DB e todos os scripts já publicados. O cenário ampliado é 100% fictício.

## O que esta atualização acrescenta

| Item do roadmap | Implementação | Critério de validação |
|---|---|---|
| Testes ponta a ponta | `tests/test_v2_e2e.py` | `RUN_GRAPH_E2E=1` com Neo4j real |
| Ollama portável | `graphpath_v2/ollama.py` | HTTP local ou ponte PowerShell no WSL; resposta real via Qwen |
| Embeddings / GraphRAG | `graphpath_v2/graphrag.py` | Geração com embeddinggemma, índice vetorial Neo4j, recuperação de fontes e resposta Qwen |
| API e interface | `graphpath_v2/api.py` e `static/index.html` | Dashboard local, endpoints documentados em `/docs`, dois cenários |
| Cenário ampliado | `graphpath_v2/sample_data.py` | 32 nós e 60 relações fictícias, separados do MVP de 6 nós |

O GraphRAG recupera documentos de ativos com suas relações no contexto e gera uma resposta ancorada em evidências. **Não é um sistema de detecção automática de vulnerabilidades, ataque ou risco.** Os resultados de IA exigem revisão humana.

## 1. Atualizar o ambiente (Ubuntu / WSL2)

Na pasta do repositório existente:

```bash
cd ~/projetos/graphpath-ai
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-v2.txt
```

O `.venv` não é enviado ao GitHub. A senha `NEO4J_PASSWORD` permanece em `.env` e o projeto usa a mesma instância Neo4j configurada pelo MVP.

Para Ollama instalado **no Windows**, a ponte Windows via `powershell.exe` pode ser usada sem abrir porta para a rede. Para Ollama no Linux, basta `OLLAMA_TRANSPORT=http`. O padrão `auto` tenta primeiro o HTTP local, depois a ponte do Windows (quando disponível).

Configuração opcional em `.env` (sem remover a senha atual):

```dotenv
NEO4J_URI=bolt://127.0.0.1:7687
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_TRANSPORT=auto
OLLAMA_MODEL=qwen3:4b-instruct
EMBEDDING_MODEL=embeddinggemma:latest
```

Verifique que os modelos constam em `ollama list` **na instalação em que o Ollama roda**. Se ainda não instalados: `ollama pull embeddinggemma` e `ollama pull qwen3:4b-instruct`. Os modelos não são enviados ao GitHub.

## 2. Preparar os dois cenários

```bash
./scripts/preparar_laboratorio.sh
python -m graphpath_v2.cli seed-expanded
```

O primeiro comando prepara o grafo original. O segundo cria 32 novos nós + 60 relações fictícias com labels e tipos `Lab*`, sem apagar ou alterar os 6 nós antigos. Os comandos são idempotentes.

## 3. Testes (executar uma vez)

```bash
./scripts/validar_v2.sh
```

O script executa os seis testes anteriores + novos testes unitários, depois testes reais Neo4j/GDS e verifica o status. Os testes opcionais de LLM **não** fazem parte dessa primeira verificação.

Para validar também a busca semântica e geração (pode demorar, pois carrega modelos locais):

```bash
python -m graphpath_v2.cli index
RUN_GRAPH_E2E=1 RUN_OLLAMA_E2E=1 python -m unittest tests.test_v2_e2e -v
python -m graphpath_v2.cli ask 'Quais caminhos chegam ao GP-DB?' --scenario base
```

O primeiro comando precisa do modelo `embeddinggemma` em execução no Ollama. O indexador salva embeddings no Neo4j com `GraphEvidence`; usa índice vetorial cosine e associa fontes pelo identificador. O relatório deve distinguir relacionamentos modelados de incidentes reais.

## 4. Iniciar o painel

```bash
./scripts/iniciar_painel.sh
```

Abra **http://127.0.0.1:8000** no navegador do Windows. O servidor está ligado apenas a `127.0.0.1`; não exponha a interface diretamente na internet.

O painel mostra os nós, relações, caminhos modelados, centralidade do GDS e perguntas GraphRAG. O código da interface usa JavaScript nativo, sem CDN, e reaproveita o banner original do projeto.

## 5. Contratos da API

- `GET /api/health`
- `GET /api/graph?scenario=base|expanded`
- `GET /api/paths?scenario=base&source=GP-EXT&target=GP-DB`
- `GET /api/centrality?scenario=expanded`
- `POST /api/graphrag/ask`, JSON `{ "scenario": "base", "question": "Quais são as dependências?" }`

OpenAPI: **http://127.0.0.1:8000/docs**. Não há endpoint para executar Cypher arbitrário e não há escrita do banco pela API. Para indexar, use a CLI local.

## 6. Segurança e limitações

- Dados totalmente fictícios. Não copie dados corporativos/CTI ou credenciais para o laboratório.
- `.env`, senhas e tokens permanecem fora do repositório.
- A aplicação é demonstrativa; não implante em produção sem autenticação, revisão de permissões, rate limiting e observabilidade.
- As verificações do modelo são opcionais; testes do modelo requerem Neo4j + Ollama reais.
- A busca por similaridade é aproximada, e respostas do Qwen não são evidências novas.
- A projeção GDS é em memória; após reinício, recrie-a usando o CLI ou preparação original.
- O código do MVP original é mantido para comparação e regressão.

## Publicação

Para executar a validação completa de todos os cinco itens em uma única sequência, use `./scripts/concluir_v2.sh`. Esse script só marcará o roadmap se **todas** as verificações (inclusive Qwen/embeddinggemma reais) forem aprovadas. Em caso de falha, corrija apenas a etapa indicada e execute novamente. Opcionalmente, depois de validar os dois cenários e Ollama no seu computador, marque os cinco itens do roadmap com `python scripts/fechar_roadmap_v2.py`, confira `git diff`, faça commit e `git push origin main`. A alteração fica no **mesmo repositório** `Paula-Tech007/graphpath-ai`.
