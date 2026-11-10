# GraphPath AI

### Graph-Based Cybersecurity Analysis with Local Generative AI

Projeto de análise de conectividade, caminhos de acesso e
centralidade em infraestruturas simuladas, combinando
Neo4j, Graph Data Science, Python e inteligência artificial local.

## Objetivo

Demonstrar como bancos de dados de grafos e algoritmos
de análise estrutural podem apoiar investigações de segurança
cibernética e a interpretação de relações entre ativos.

O projeto utiliza exclusivamente dados fictícios.

## Arquitetura

Entrada: infraestrutura simulada
        |
        v
Neo4j - Nós e relacionamentos
        |
        v
Cypher - Consultas de caminhos
        |
        v
Graph Data Science - Centralidade
        |
        v
Python - Extração de evidências
        |
        v
Ollama / Qwen3:4B - IA Generativa
        |
        v
Relatórios técnicos

## Tecnologias

- Python 3
- Neo4j 2026.10.2
- Neo4j Graph Data Science
- Cypher
- Docker e Docker Compose
- Ollama
- Qwen3:4B-Instruct
- unittest

## Funcionalidades implementadas

- Modelagem de identidades e ativos em grafos.
- Consultas de caminhos por Cypher.
- Cálculo de Betweenness Centrality.
- Simulação não destrutiva de remoção de nós.
- Extração automatizada de evidências.
- Geração de texto com inteligência artificial local.
- Consolidação de relatório técnico.
- Testes automatizados de consistência.

## Resultados do laboratório

Cenário inicial:

- 6 nós
- 5 relacionamentos
- 2 caminhos entre GP-EXT e GP-DB
- GP-WEB com centralidade 3.0
- GP-APP e GP-JUMP com centralidade 1.0
- 0 caminhos restantes ao excluir GP-WEB da análise

O GP-WEB foi identificado como ponto obrigatório de passagem
entre a identidade externa e o banco crítico simulado.

Centralidade elevada não comprova vulnerabilidade.

## Testes

Os seis testes de consistência foram aprovados:

    python3 -m unittest discover -s tests -v

Os testes atuais utilizam evidências salvas.
Testes completos de integração ainda serão desenvolvidos.

## Arquivos principais

- compose.yaml: infraestrutura Neo4j
- seed.cypher: criação do cenário fictício
- gds.cypher: projeção e análise de centralidade
- impacto.cypher: simulação de impacto
- integrar_ia.py: primeira integração com IA
- gerar_relatorio_limitado.py: geração limitada com Ollama
- consolidar_relatorio.py: consolidação técnica
- evidencias.txt: resultados do cenário fictício
- relatorio_tecnico.md: relatório consolidado
- tests/: testes automatizados

## Segurança

O projeto não deve armazenar credenciais no GitHub.

O arquivo .env é excluído pelo .gitignore.

Todos os exemplos devem utilizar informações fictícias,
sem dados reais de clientes ou organizações.

## Limitações atuais

- Cenário inicial de pequena escala.
- Testes baseados em resultados previamente coletados.
- Integração Ollama dependente de Windows e WSL.
- Scripts com caminhos locais que serão refatorados.
- Projeção GDS armazenada em memória.
- Relatórios de IA sujeitos a validação técnica.

## Próximas melhorias

- Refatorar configuração e caminhos locais.
- Criar testes de integração.
- Expandir o grafo para cenários mais complexos.
- Implementar embeddings e busca semântica.
- Desenvolver uma API de análise.
- Criar visualização interativa dos grafos.

## Status

MVP em desenvolvimento.

Infraestrutura, consultas, algoritmo GDS,
geração local com IA e testes iniciais validados.

## Licença

A definir antes da publicação pública.

## Como executar o laboratorio

### Pre-requisitos

- Docker Desktop com Docker Compose
- Linux ou WSL2 com Docker acessivel
- Python 3.10 ou superior
- Git

### 1. Preparar o ambiente

No diretorio raiz do projeto:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e defina uma senha forte
para NEO4J_PASSWORD.

Nao publique esse arquivo nem compartilhe sua senha.

### 2. Iniciar o laboratorio

```bash
./scripts/preparar_laboratorio.sh
```

O script inicia o Neo4j, aguarda sua disponibilidade,
carrega os dados ficticios e prepara a projecao GDS.

### 3. Coletar evidencias

```bash
./scripts/coletar_evidencias.sh
```

O comando executa consultas ao banco,
calcula a centralidade, simula o impacto
e produz um relatorio tecnico.

### 4. Validar a integracao

```bash
./scripts/verificar_integracao.sh
```

### 5. Executar os testes

```bash
python3 -m unittest discover -s tests -v
```

### Interface Neo4j

A interface local fica disponivel em:

http://localhost:7474

Usuario: neo4j

Senha: definida no arquivo .env durante a
primeira inicializacao do banco.

### Inteligencia artificial local

A integracao de IA foi validada com Ollama
e Qwen3:4B-Instruct no Windows, via WSL2.

O modelo precisa estar instalado e acessivel.
Os scripts atuais dessa integracao dependem
do PowerShell do Windows.

A geracao com IA e opcional para executar
as analises de grafos e os testes principais.

### Observacoes

O projeto utiliza dados totalmente ficticios.

As analises demonstram conectividade estrutural,
nao exploracao real de vulnerabilidades.

A senha definida na primeira inicializacao
do Neo4j permanece associada ao volume de dados.
Alterar o .env posteriormente nao altera
automaticamente a senha existente.
