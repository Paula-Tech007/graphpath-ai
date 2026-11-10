from pathlib import Path
import base64
import subprocess

pasta = Path(__file__).resolve().parent
evidencias = pasta / "evidencias.txt"

if not evidencias.is_file():
    raise SystemExit("ERRO: evidencias.txt nao encontrado.")

dados = evidencias.read_text(encoding="utf-8")

prompt = (
    "Voce e um analista de seguranca cibernetica. "
    "Escreva um relatorio curto em portugues, "
    "com resumo, caminhos ate GP-DB, centralidade, "
    "impacto do GP-WEB e recomendacoes. "
    "Use somente os dados abaixo. "
    "Nao invente ataques nem vulnerabilidades. "
    "Os dados sao ficticios. "
    "Centralidade nao significa risco automaticamente.\n\n"
    + dados
)

arquivo = pasta / "prompt_ia_limitado.txt"
arquivo.write_text(prompt, encoding="utf-8")

caminho_windows = subprocess.run(
    ["wslpath", "-w", str(arquivo)],
    capture_output=True,
    text=True,
    check=True
).stdout.strip().replace("'", "''")

ps = """
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
Add-Type -AssemblyName System.Net.Http

$prompt = [IO.File]::ReadAllText(
    'CAMINHO_AQUI',
    [Text.Encoding]::UTF8
)

$body = @{
    model = 'qwen3:4b-instruct'
    prompt = $prompt
    stream = $false
    options = @{
        num_predict = 280
        num_ctx = 2048
        temperature = 0
    }
} | ConvertTo-Json -Depth 5

$handler = New-Object System.Net.Http.HttpClientHandler
$handler.UseProxy = $false
$client = New-Object System.Net.Http.HttpClient($handler)
$client.Timeout = [TimeSpan]::FromSeconds(180)

$content = New-Object System.Net.Http.StringContent(
    $body,
    [Text.Encoding]::UTF8,
    'application/json'
)

try {
    $res = $client.PostAsync(
        'http://127.0.0.1:11434/api/generate',
        $content
    ).GetAwaiter().GetResult()

    $res.EnsureSuccessStatusCode() | Out-Null

    $json = $res.Content.ReadAsStringAsync().GetAwaiter().GetResult()
    $obj = $json | ConvertFrom-Json

    if (-not $obj.response) {
        throw 'Ollama nao retornou texto.'
    }

    [Console]::Write($obj.response)
}
finally {
    $client.Dispose()
    $handler.Dispose()
}
""".replace("CAMINHO_AQUI", caminho_windows)

comando = base64.b64encode(
    ps.encode("utf-16le")
).decode("ascii")

print("Enviando evidencias ao Qwen com limite de geracao...", flush=True)

try:
    resultado = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-EncodedCommand",
            comando
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=210
    )
except subprocess.TimeoutExpired:
    raise SystemExit(
        "Tempo limite atingido. Evidencias preservadas."
    )

if resultado.returncode != 0:
    raise SystemExit(
        "Falha ao gerar relatorio:\n" + resultado.stderr
    )

relatorio = resultado.stdout.strip()

if not relatorio:
    raise SystemExit("O Qwen retornou resposta vazia.")

destino = pasta / "relatorio_ia.md"
destino.write_text(relatorio + "\n", encoding="utf-8")

print("\n=== RELATORIO GRAPHPATH AI ===\n")
print(relatorio)
print("\nRelatorio salvo em relatorio_ia.md")
