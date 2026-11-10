from pathlib import Path
import ast
import re

pasta = Path(__file__).resolve().parent
texto = (pasta / "evidencias.txt").read_text(
    encoding="utf-8"
)

def secao(inicio, fim=None):
    parte = texto.split(inicio, 1)[1]
    return parte.split(fim, 1)[0] if fim else parte

bloco_caminhos = secao(
    "CAMINHOS:", "CENTRALIDADE GDS:"
)
bloco_gds = secao(
    "CENTRALIDADE GDS:", "IMPACTO:"
)
bloco_impacto = secao("IMPACTO:")

caminhos = [
    ast.literal_eval(linha.strip())
    for linha in bloco_caminhos.splitlines()
    if linha.strip().startswith("[")
]

centralidades = [
    (nome, float(valor))
    for nome, valor in re.findall(
        r'"([^"]+)",\s*([0-9.]+)', bloco_gds
    )
]

valores = re.search(
    r'(\d+)\s*,\s*(\d+)\s*$',
    bloco_impacto
)
if not valores:
    raise SystemExit("Falha ao interpretar impacto.")

atuais, sem_web = map(int, valores.groups())

if len(caminhos) != atuais:
    raise SystemExit("Quantidade de caminhos inconsistente.")

if sum("GP-WEB" not in p for p in caminhos) != sem_web:
    raise SystemExit("Impacto inconsistente com os caminhos.")

if not centralidades:
    raise SystemExit("Centralidades nao encontradas.")

rotas = "\n".join(
    f"{i}. {' -> '.join(caminho)}"
    for i, caminho in enumerate(caminhos, 1)
)

ranking = "\n".join(
    f"| {nome} | {valor:.1f} |"
    for nome, valor in centralidades
)

relatorio = f"""# GraphPath AI - Relatorio Tecnico

## 1. Resumo executivo

Analise de conectividade e centralidade de uma
infraestrutura ficticia modelada no Neo4j.

Foram identificados {atuais} caminhos entre
GP-EXT e GP-DB, considerando os relacionamentos
registrados no banco.

## 2. Caminhos identificados

{rotas}

## 3. Centralidade - Graph Data Science

Algoritmo utilizado: Betweenness Centrality.

| Ativo | Centralidade |
|---|---:|
{ranking}

A centralidade mede a participacao de um no
como intermediario em caminhos mais curtos.
Ela nao constitui, isoladamente, um indicador
de vulnerabilidade ou comprometimento.

## 4. Simulacao de impacto

- Caminhos originais: {atuais}
- Caminhos sem GP-WEB: {sem_web}

A simulacao excluiu GP-WEB da avaliacao
dos caminhos, sem modificar o banco de dados.

## 5. Interpretacao de seguranca

GP-WEB participa de todos os caminhos
identificados entre GP-EXT e GP-DB.

Nesse modelo, representa um ponto
obrigatorio de passagem e merece atencao
em uma eventual avaliacao de arquitetura.

## 6. Recomendacoes para avaliacao

- Revisar a segmentacao de rede.
- Validar as permissoes de acesso.
- Avaliar controles de acesso ao GP-WEB.
- Considerar caminhos alternativos autorizados.
- Monitorar alteracoes de conectividade.

Estas sao recomendacoes hipoteticas.
Nao representam falhas comprovadas.

## 7. Limitacoes

Os ativos e relacionamentos sao ficticios.

As conexoes representam possibilidades
modeladas, nao ataques efetivamente observados.

O resultado nao comprova explorabilidade,
incidentes reais ou indisponibilidade real.

## 8. Tecnologias demonstradas

- Neo4j e linguagem Cypher
- Graph Data Science
- Python
- Ollama e Qwen3:4B (integracao de IA
  validada em execucao anterior)

## 9. Rastreabilidade

Fonte: evidencias.txt

Consultas utilizadas:
seed.cypher, gds.cypher e impacto.cypher.

Este documento foi consolidado
automaticamente a partir das evidencias
e nao e uma nova resposta gerada pelo LLM.
"""

destino = pasta / "relatorio_tecnico.md"
destino.write_text(relatorio, encoding="utf-8")

print("Relatorio tecnico criado com sucesso!")
print("Caminhos:", atuais)
print("Sem GP-WEB:", sem_web)
print("Ativos com centralidade:", len(centralidades))
print("Arquivo:", destino)
