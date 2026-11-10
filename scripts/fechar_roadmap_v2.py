"""Marca roadmap como concluído somente após validação explícita do laboratório."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
readme = root / 'README.md'
text = readme.read_text(encoding='utf-8')
changes = [
    'Testes de integração de ponta a ponta',
    'Integração Ollama portável entre sistemas',
    'Embeddings e busca semântica (GraphRAG)',
    'API Python e interface interativa de grafos',
    'Cenários ampliados com dados fictícios',
]
for item in changes:
    old = '- [ ] ' + item
    if old in text:
        text = text.replace(old, '- [x] ' + item, 1)
    elif '- [x] ' + item not in text:
        raise SystemExit('Roadmap não encontrado: ' + item)
addition = """
## `>_` Evolução v0.2 — API, GraphRAG e grafo ampliado

A versão 0.2 acrescenta cenário fictício com **32 nós e 60 relações**, API local em FastAPI, painel interativo Matrix e GraphRAG usando **embeddinggemma + Qwen** no Ollama. O cenário original **6 nós / 5 relações** continua isolado e validado.

**[Instruções, limites de segurança e validação da v0.2](docs/EVOLUCAO_V2.md)**

> O GraphRAG realiza recuperação semântica sobre evidências modeladas, não identifica vulnerabilidades reais automaticamente.

"""
if "Evolução v0.2 — API, GraphRAG" not in text:
    marker = "## `>_` Escopo e responsabilidade"
    if marker not in text:
        raise SystemExit("Seção de escopo não encontrada. Atualização interrompida")
    text = text.replace(marker, addition + marker)
readme.write_text(text, encoding='utf-8')
print('Cinco itens do roadmap marcados. Confira git diff antes do push.')
