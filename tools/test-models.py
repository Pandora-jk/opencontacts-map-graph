#!/usr/bin/env python3
"""
Quick connectivity test for all configured OpenClaw model providers.
Sends a minimal prompt to every model, reports pass/fail + latency.
"""

import asyncio
import json
import os
import time
from pathlib import Path

try:
    import aiohttp
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp", "-q", "--break-system-packages"])
    import aiohttp

PROMPT = "Reply with exactly one word: OK"


def load_env_file(env_path: str) -> None:
    path = Path(env_path).expanduser()
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


load_env_file("~/.openclaw/.env")

PROVIDERS = {
    "nvidia": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": os.getenv("OPENCLAW_NVIDIA_API_KEY"),
        "models": [
            "qwen/qwen3.5-397b-a17b",       # PRIMARY
            "qwen/qwen3-235b-a22b",          # fallback 1
            "z-ai/glm5",                     # fallback 2
            "nvidia/llama-3.1-nemotron-ultra-253b-v1",  # fallback 3
            "openai/gpt-oss-120b",           # fallback 4
            "mistralai/devstral-2-123b-instruct-2512",  # fallback 5
            "nvidia/llama-3.3-nemotron-super-49b-v1.5",
            "meta/llama-3.3-70b-instruct",
        ],
    },
    "zai": {
        "base_url": "https://api.z.ai/api/paas/v4",
        "api_key": os.getenv("OPENCLAW_ZAI_API_KEY"),
        "models": ["glm-4.7-Flash", "glm-4.5-flash", "glm-4.6v-flash"],
    },
    "google": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "api_key": os.getenv("OPENCLAW_GEMINI_API_KEY"),
        "models": ["gemini-2.5-flash"],
    },
    "cerebras": {
        "base_url": "https://api.cerebras.ai/v1",
        "api_key": os.getenv("OPENCLAW_CEREBRAS_API_KEY"),
        "models": ["gpt-oss-120b"],
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": os.getenv("OPENCLAW_GROQ_API_KEY"),
        "models": ["llama-3.3-70b-versatile"],
    },
    "chutes": {
        "base_url": "https://api.chutes.ai/v1",
        "api_key": os.getenv("OPENCLAW_CHUTES_API_KEY"),
        "models": ["deepseek-ai/DeepSeek-R1", "Qwen/Qwen3-235B-A22B"],
        "note": "NEEDS REAL API TOKEN (fingerprint provided is not the API key)",
    },
}

TIMEOUT = 90  # seconds — reasoning models can be slow


async def test_model(session, provider_name, base_url, api_key, model_id):
    label = f"{provider_name}/{model_id}"
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": 16,
        "temperature": 0,
    }
    t0 = time.monotonic()
    try:
        async with session.post(
            url, headers=headers, json=payload,
            timeout=aiohttp.ClientTimeout(total=TIMEOUT)
        ) as resp:
            elapsed = time.monotonic() - t0
            body = await resp.json(content_type=None)
            if resp.status == 200:
                msg = body["choices"][0]["message"]
                # Reasoning models may return content=None with reasoning_content
                reply = msg.get("content") or msg.get("reasoning_content") or msg.get("reasoning") or "(empty)"
                reply = reply.strip()[:40] if reply else "(empty)"
                return (label, "✅", f"{elapsed:.1f}s", reply)
            else:
                err = body.get("error", {})
                msg = err.get("message", str(body))[:80]
                return (label, "❌", f"{elapsed:.1f}s", f"HTTP {resp.status}: {msg}")
    except asyncio.TimeoutError:
        return (label, "⏱️", f"{TIMEOUT}s", "Timeout")
    except Exception as e:
        elapsed = time.monotonic() - t0
        return (label, "❌", f"{elapsed:.1f}s", str(e)[:80])


async def main():
    tasks = []
    connector = aiohttp.TCPConnector(limit=20)
    async with aiohttp.ClientSession(connector=connector) as session:
        for provider_name, cfg in PROVIDERS.items():
            if not cfg.get("api_key"):
                print(f"Skipping {provider_name}: missing API key in environment")
                continue
            for model_id in cfg.get("models", []):
                tasks.append(
                    test_model(session, provider_name, cfg["base_url"], cfg["api_key"], model_id)
                )
        print(f"Testing {len(tasks)} models (timeout {TIMEOUT}s each)...\n")
        results = await asyncio.gather(*tasks)

    # Sort: ✅ first, then ❌/⏱️
    results = sorted(results, key=lambda r: (0 if r[1] == "✅" else 1, r[0]))

    col1 = max(len(r[0]) for r in results) + 2
    print(f"{'MODEL':<{col1}} {'STATUS':<6} {'TIME':<8} RESPONSE/ERROR")
    print("─" * (col1 + 50))
    for label, status, elapsed, detail in results:
        print(f"{label:<{col1}} {status:<6} {elapsed:<8} {detail}")

    ok = sum(1 for r in results if r[1] == "✅")
    print(f"\n{ok}/{len(results)} models OK")


if __name__ == "__main__":
    asyncio.run(main())
