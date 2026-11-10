"""CLI de preparação e consulta (sem sobrescrever o MVP existente)."""
import argparse
import json
from .config import load_config
from .graph import GraphStore
from .ollama import OllamaClient
from .graphrag import index_documents, ask


def main():
    parser = argparse.ArgumentParser(description="GraphPath AI v0.2")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("seed-expanded", help="Cria 32 nós e 60 relações fictícias, sem tocar no grafo original")
    sub.add_parser("status", help="Verifica a conexão ao Neo4j")
    indexer = sub.add_parser("index", help="Gera embeddings e índice vetorial")
    indexer.add_argument("--scenario", choices=["base", "expanded", "both"], default="both")
    query = sub.add_parser("ask", help="Pergunta ao GraphRAG")
    query.add_argument("question")
    query.add_argument("--scenario", choices=["base", "expanded"], default="base")
    args = parser.parse_args()
    settings = load_config()
    store = GraphStore(settings)
    try:
        if args.action == "seed-expanded":
            print(json.dumps(store.seed_expanded(), ensure_ascii=False))
            print("Projeção criada:", store.ensure_gds("expanded"))
        elif args.action == "status":
            print(json.dumps({"neo4j": store.health(), "base": len(store.graph("base")["nodes"]),
                              "expanded": len(store.graph("expanded")["nodes"])}, ensure_ascii=False))
        elif args.action == "index":
            scenarios = ("base", "expanded") if args.scenario == "both" else (args.scenario,)
            print(json.dumps(index_documents(store, OllamaClient(settings), settings, scenarios), ensure_ascii=False))
        else:
            print(json.dumps(ask(store, OllamaClient(settings), settings, args.question, args.scenario),
                             indent=2, ensure_ascii=False))
    finally:
        store.close()


if __name__ == "__main__":
    main()
