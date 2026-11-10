"""API somente local. Não contém endpoints de Cypher arbitrário nem mutações remotas."""
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .config import ROOT, load_config
from .graph import GraphStore
from .graphrag import ask
from .ollama import OllamaClient

app = FastAPI(title="GraphPath AI", version="0.2.0", docs_url="/docs", redoc_url=None)
app.mount("/assets", StaticFiles(directory=ROOT / "assets"), name="assets")
log = logging.getLogger("graphpath")


def _store():
    return GraphStore(load_config())


def _run(method, *args, **kwargs):
    store = None
    try:
        store = _store()
        return getattr(store, method)(*args, **kwargs)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    except Exception as exc:
        log.warning("Neo4j indisponível ou consulta falhou: %s", type(exc).__name__)
        raise HTTPException(503, detail="Neo4j indisponível ou consulta falhou; confira o laboratório") from exc
    finally:
        if store is not None:
            store.close()


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(Path(__file__).resolve().parent / "static" / "index.html")


@app.get("/api/health")
def health():
    return {"ok": _run("health"), "version": "0.2.0"}


@app.get("/api/graph")
def graph(scenario: str = Query("base", pattern="^(base|expanded)$")):
    return _run("graph", scenario)


@app.get("/api/paths")
def paths(scenario: str = Query("base", pattern="^(base|expanded)$"),
          source: str = Query("GP-EXT", min_length=1, max_length=64, pattern=r"^[A-Z0-9-]+$"),
          target: str = Query("GP-DB", min_length=1, max_length=64, pattern=r"^[A-Z0-9-]+$")):
    return {"scenario": scenario, "source": source, "target": target,
            "paths": _run("paths", scenario, source, target)}


@app.get("/api/centrality")
def centrality(scenario: str = Query("base", pattern="^(base|expanded)$")):
    return {"scenario": scenario, "centrality": _run("centrality", scenario)}


class Question(BaseModel):
    question: str = Field(min_length=5, max_length=500)
    scenario: str = Field(default="base", pattern="^(base|expanded)$")


@app.post("/api/graphrag/ask")
def graphrag_query(req: Question):
    store = None
    try:
        settings = load_config()
        store = GraphStore(settings)
        return ask(store, OllamaClient(settings), settings, req.question, req.scenario)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    except Exception as exc:
        log.warning("GraphRAG indisponível: %s", type(exc).__name__)
        raise HTTPException(503, detail="GraphRAG não está pronto; confira Ollama, modelo e índice vetorial") from exc
    finally:
        if store is not None:
            store.close()
