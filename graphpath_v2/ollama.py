"""Cliente Ollama sem dependência de serviços em nuvem.

Transportes: HTTP local e, quando necessário, ponte PowerShell para Ollama do Windows.
"""
import base64
import json
import shutil
import subprocess

import httpx
from .config import Settings


class OllamaUnavailable(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def _request_http(self, route: str, payload: dict | None, timeout: int):
        method = "POST" if payload is not None else "GET"
        with httpx.Client(timeout=timeout, trust_env=False) as client:
            r = client.request(method, self.settings.ollama_url + route, json=payload)
            r.raise_for_status()
            return r.json()

    def _request_windows(self, route: str, payload: dict | None, timeout: int):
        if not shutil.which("powershell.exe"):
            raise OllamaUnavailable("powershell.exe indisponível: configure HTTP local ou execute no WSL")
        # Serialização Base64 impede interpolação de prompts como código PowerShell.
        serialized = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8")
        encoded_data = base64.b64encode(serialized).decode("ascii")
        url = self.settings.ollama_url + route
        script = f"""
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Net.Http
[Console]::OutputEncoding=[Text.Encoding]::UTF8
$body=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{encoded_data}'))
$handler=New-Object Net.Http.HttpClientHandler
$handler.UseProxy=$false
$client=New-Object Net.Http.HttpClient($handler)
$client.Timeout=[TimeSpan]::FromSeconds({timeout})
try {{
  $uri='{url}'
  if ('{route}' -eq '/api/tags') {{
    $response=$client.GetAsync($uri).GetAwaiter().GetResult()
  }} else {{
    $content=New-Object Net.Http.StringContent($body,[Text.Encoding]::UTF8,'application/json')
    $response=$client.PostAsync($uri,$content).GetAwaiter().GetResult()
  }}
  $response.EnsureSuccessStatusCode() | Out-Null
  [Console]::Write($response.Content.ReadAsStringAsync().GetAwaiter().GetResult())
}} finally {{ $client.Dispose(); $handler.Dispose() }}
"""
        encoded_script = base64.b64encode(script.encode("utf-16le")).decode("ascii")
        run = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded_script],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout + 15
        )
        if run.returncode != 0:
            raise OllamaUnavailable("Falha no Ollama do Windows; confirme que o serviço está ativo")
        return json.loads(run.stdout.lstrip("\ufeff"))

    def request(self, route: str, payload: dict | None = None, timeout: int = 120):
        # Rotas permitidas, evitando uso indevido do cliente como proxy para outras URLs.
        if route not in {"/api/tags", "/api/embed", "/api/generate"}:
            raise ValueError("Rota Ollama não permitida")
        mode = self.settings.ollama_transport
        if mode == "windows":
            return self._request_windows(route, payload, timeout)
        try:
            return self._request_http(route, payload, timeout)
        except (httpx.HTTPError, OSError) as exc:
            if mode == "http":
                raise OllamaUnavailable("Ollama HTTP local indisponível") from exc
            return self._request_windows(route, payload, timeout)

    def embed(self, texts: list[str]):
        out = self.request("/api/embed", {"model": self.settings.embedding_model, "input": texts}, 150)
        vectors = out.get("embeddings", [])
        if len(vectors) != len(texts) or not vectors or not all(isinstance(v, list) and v for v in vectors):
            raise OllamaUnavailable("O Ollama não retornou embeddings válidos")
        d = len(vectors[0])
        if any(len(v) != d for v in vectors):
            raise OllamaUnavailable("Dimensões de embeddings inconsistentes")
        return vectors

    def generate(self, prompt: str):
        out = self.request("/api/generate", {
            "model": self.settings.ollama_model, "prompt": prompt, "stream": False,
            "options": {"num_predict": 350, "temperature": 0, "num_ctx": 4096}
        }, 210)
        answer = out.get("response", "").strip()
        if not answer:
            raise OllamaUnavailable("Resposta vazia do modelo")
        return answer
