"""Configuração local. Nunca imprime credenciais."""
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_config():
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env", override=False)
    return Settings(
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", ""),
        ollama_url=os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/"),
        ollama_transport=os.getenv("OLLAMA_TRANSPORT", "auto").lower(),
        ollama_model=os.getenv("OLLAMA_MODEL", "qwen3:4b-instruct"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "embeddinggemma:latest"),
    )


@dataclass(frozen=True)
class Settings:
    neo4j_uri: str = "bolt://127.0.0.1:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""
    ollama_url: str = "http://127.0.0.1:11434"
    ollama_transport: str = "auto"  # auto | http | windows
    ollama_model: str = "qwen3:4b-instruct"
    embedding_model: str = "embeddinggemma:latest"

    def __post_init__(self):
        if self.ollama_transport not in {"auto", "http", "windows"}:
            raise ValueError("OLLAMA_TRANSPORT precisa ser auto, http ou windows")
        if not self.ollama_url.startswith(("http://127.0.0.1:", "http://localhost:")):
            raise ValueError("Por segurança, OLLAMA_URL deve apontar para localhost")

    def db_auth(self):
        if not self.neo4j_password or self.neo4j_password == "substitua-por-uma-senha-forte":
            raise RuntimeError("Defina NEO4J_PASSWORD no arquivo .env (não publique esse arquivo)")
        return self.neo4j_user, self.neo4j_password
