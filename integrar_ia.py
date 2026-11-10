from pathlib import Path
import subprocess

PASTA = Path(__file__).resolve().parent

def consultar(cypher):
    comando = [
        "docker", "compose", "exec", "-T", "neo4j",
        "sh", "-c",
        'cypher-shell -u neo4j -p "${NEO4J_AUTH#*/}"'
    ]
    resultado = subprocess.run(
        comando,
        input=cypher.strip() + ";\n",
        text=True,
        capture_output=True,
        cwd=PASTA
    )
    if resultado.returncode != 0:
        raise RuntimeError(resultado.stderr)
    return resultado.stdout.strip()

print("Consultando caminhos no Neo4j...")

caminhos = consultar("""
MATCH (ext:Identity {id:'GP-EXT'})
      -[:HAS_ACCESS]->(web:Asset)
MATCH p=(web)-[:CAN_REACH*1..3]->
      (:Asset {id:'GP-DB'})
RETURN [ext.id] + [n IN nodes(p) | n.id]
       AS caminho
ORDER BY caminho
""")

print("Calculando centralidade com GDS...")

centralidade = consultar("""
CALL gds.betweenness.stream('graphpath-ai')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS ativo,
       score AS centralidade
ORDER BY centralidade DESC, ativo
""")

print("Analisando impacto do GP-WEB...")

impacto = consultar("""
MATCH p=(:Identity {id:'GP-EXT'})
  -[:HAS_ACCESS|CAN_REACH*1..4]->
  (:Asset {id:'GP-DB'})
WITH collect(p) AS caminhos
RETURN size(caminhos) AS caminhos_atuais,
       size([p IN caminhos
       WHERE none(n IN nodes(p)
       WHERE n.id='GP-WEB')])
       AS caminhos_sem_gp_web
""")

evidencias = (
    "CAMINHOS:\n" + caminhos +
    "\n\nCENTRALIDADE GDS:\n" + centralidade +
    "\n\nIMPACTO:\n" + impacto
)

(PASTA / "evidencias.txt").write_text(
    evidencias, encoding="utf-8"
)

prompt = """
Você é um analista de segurança cibernética.

Produza um relatório técnico em português com:
1. Resumo executivo.
2. Caminhos identificados até GP-DB.
3. Importância estrutural do GP-WEB.
4. Interpretação da centralidade.
5. Resultado da simulação de impacto.
6. Recomendações de segurança.

Utilize EXCLUSIVAMENTE as evidências fornecidas.
Não invente vulnerabilidades, ataques reais,
permissões ou indicadores de comprometimento.
Todos os dados são fictícios.
Centralidade não representa risco automaticamente.

EVIDÊNCIAS DO NEO4J:
""" + evidencias

arquivo = PASTA / "prompt_ia.txt"
arquivo.write_text(prompt, encoding="utf-8")

caminho_windows = subprocess.run(
    ["wslpath", "-w", str(arquivo)],
    capture_output=True,
    text=True,
    check=True
).stdout.strip().replace("'", "''")

comando_ps = (
    "[Console]::OutputEncoding="
    "[System.Text.Encoding]::UTF8;"
    "$OutputEncoding=[Console]::OutputEncoding;"
    f"$p=Get-Content -LiteralPath "
    f"'{caminho_windows}' -Raw -Encoding UTF8;"
    "& ollama run qwen3:4b-instruct $p"
)

print("Enviando evidências ao Qwen...")

resultado = subprocess.run(
    [
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        comando_ps
    ],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"
)

if resultado.returncode != 0:
    raise RuntimeError(resultado.stderr)

relatorio = resultado.stdout.strip()

if not relatorio:
    raise RuntimeError("O Qwen não retornou texto.")

(PASTA / "relatorio_ia.md").write_text(
    relatorio + "\n", encoding="utf-8"
)

print("\n=== RELATORIO GRAPHPATH AI ===\n")
print(relatorio)
print("\nRelatorio salvo em relatorio_ia.md")
