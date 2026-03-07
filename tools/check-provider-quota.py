#!/usr/bin/env python3
"""
OpenClaw Provider Quota & Usage Tracker
----------------------------------------
Auto-discovers all providers from openclaw.json (models.providers) and
agents/main/agent/models.json. Queries live quota APIs where available,
falls back to session data for the rest.

Supported provider APIs:
  openrouter   -> /api/v1/auth/key  (usage, limits, tier)
  [others]     -> session data from sessions.json + JSONL request counts

Usage:
  python3 check-provider-quota.py            # print report + send to Telegram
  python3 check-provider-quota.py --stdout   # print report only, no Telegram send
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE              = Path.home() / ".openclaw"
CONFIG_PATH       = BASE / "openclaw.json"
MODELS_PATH       = BASE / "agents/main/agent/models.json"
AUTH_PROFILES_PATH= BASE / "agents/main/agent/auth-profiles.json"
SESSIONS_PATH     = BASE / "agents/main/sessions/sessions.json"
SESSIONS_DIR      = BASE / "agents/main/sessions"
OUTPUT_PATH       = BASE / "workspace/memory/provider-quota.json"

ONLY_STDOUT   = "--stdout" in sys.argv

# ── Helpers ────────────────────────────────────────────────────────────────────
def load_json(path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return default if default is not None else {}

def http_get(url, headers=None, timeout=10):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()[:300]
        except Exception:
            body = ""
        return {"_error": f"HTTP {e.code}", "_body": body}
    except Exception as e:
        return {"_error": str(e)}

def fmt_k(n):
    """Format token count: 1234 → '1.2k', 12345 → '12k'"""
    if n is None:
        return "?"
    if n < 1000:
        return str(n)
    if n < 10000:
        return f"{n/1000:.1f}k"
    return f"{n//1000}k"

def fmt_pct(used, total):
    if not total:
        return ""
    pct = round(used / total * 100)
    bar_filled = pct // 10
    bar = "█" * bar_filled + "░" * (10 - bar_filled)
    return f"{bar} {pct}%"

# ── Provider type detection ────────────────────────────────────────────────────
def detect_type(name, base_url):
    url  = (base_url or "").lower()
    name = (name or "").lower()
    if "openrouter.ai" in url:               return "openrouter"
    if "integrate.api.nvidia.com" in url:    return "nvidia"
    if "api.z.ai" in url or "zhipu" in url:  return "zai"
    if "googleapis.com" in url:              return "google"
    if "anthropic.com" in url:               return "anthropic"
    if "api.openai.com" in url:              return "openai"
    if "together" in url:                    return "together"
    if "groq.com" in url:                    return "groq"
    if "mistral.ai" in url:                  return "mistral"
    if "cohere.ai" in url or "cohere.com" in url: return "cohere"
    return name or "unknown"

# ── Per-provider API checkers ──────────────────────────────────────────────────
def check_openrouter(api_key, _base_url):
    data = http_get(
        "https://openrouter.ai/api/v1/auth/key",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    if "_error" in data:
        return {"status": "error", "error": data["_error"]}
    d = data.get("data", {})
    return {
        "status":           "ok",
        "is_free_tier":     d.get("is_free_tier"),
        "usage_daily":      d.get("usage_daily"),       # USD
        "usage_monthly":    d.get("usage_monthly"),     # USD
        "limit":            d.get("limit"),             # USD, null = unlimited
        "limit_remaining":  d.get("limit_remaining"),   # USD
        "limit_reset":      d.get("limit_reset"),       # ISO timestamp or null
        "expires_at":       d.get("expires_at"),
    }

# Map of provider type → checker function
CHECKERS = {
    "openrouter": check_openrouter,
    # Add more here as provider APIs become available, e.g.:
    # "anthropic": check_anthropic,
    # "groq":      check_groq,
}

# ── Session data reader ────────────────────────────────────────────────────────
def get_session_stats(provider_name):
    """Read token usage from sessions.json for a given provider."""
    sessions = load_json(SESSIONS_PATH, {})
    result = []
    for key, s in sessions.items():
        if not isinstance(s, dict):
            continue
        mp    = (s.get("modelProvider") or "").lower()
        model = (s.get("model") or "").lower()
        # Match by provider name appearing in modelProvider or model string
        if provider_name.lower() not in mp and provider_name.lower() not in model:
            continue
        inp   = s.get("inputTokens")  or 0
        out   = s.get("outputTokens") or 0
        ctx   = s.get("totalTokens")  or 0
        limit = s.get("contextTokens") or 0
        result.append({
            "key":           key,
            "model":         s.get("model", "unknown"),
            "input_tokens":  inp,
            "output_tokens": out,
            "context_used":  ctx,
            "context_limit": limit,
        })
    return result

def count_today_turns():
    """
    Count API turns per session key from today's JSONL entries.
    Returns dict: session_key → count_of_assistant_turns_today
    """
    today = datetime.now(timezone.utc).date().isoformat()
    counts = {}
    for jsonl in SESSIONS_DIR.glob("*.jsonl"):
        # Infer session key from sessions.json (match by sessionFile field)
        session_key = None
        sessions = load_json(SESSIONS_PATH, {})
        for k, s in sessions.items():
            if isinstance(s, dict) and jsonl.name in (s.get("sessionFile") or ""):
                session_key = k
                break
        if not session_key:
            continue
        try:
            with open(jsonl) as f:
                for line in f:
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    ts  = (d.get("timestamp") or "")[:10]
                    msg = d.get("message", {})
                    if ts == today and isinstance(msg, dict) and msg.get("role") == "assistant":
                        counts[session_key] = counts.get(session_key, 0) + 1
        except Exception:
            pass
    return counts

# ── Report formatter ───────────────────────────────────────────────────────────
def format_report(results, checked_at):
    now_str = checked_at[:16].replace("T", " ") + " UTC"
    lines = [f"📊 *Provider Quota* — {now_str}", ""]

    for name, p in results.items():
        ptype  = p["type"]
        api    = p.get("api_data", {})
        stats  = p.get("session_stats", [])
        turns  = p.get("turns_today", {})

        # Header line per provider
        tier_tag = " _(free)_" if api.get("is_free_tier") else ""
        lines.append(f"*{name}* [{ptype}]{tier_tag}")

        # Live API data (OpenRouter etc.)
        if api.get("status") == "ok":
            daily = api.get("usage_daily")
            monthly = api.get("usage_monthly")
            limit = api.get("limit")
            remaining = api.get("limit_remaining")
            reset = api.get("limit_reset")

            if daily is not None:
                lines.append(f"  Today: ${daily:.4f}")
            if monthly is not None:
                lines.append(f"  Month: ${monthly:.4f}")
            if limit is not None:
                lines.append(f"  Limit: ${limit:.2f} | Remaining: ${remaining:.2f}" if remaining is not None else f"  Limit: ${limit:.2f}")
            elif limit is None and api.get("status") == "ok":
                lines.append(f"  Limit: unlimited")
            if reset:
                lines.append(f"  Reset: {reset[:10]}")
        elif api.get("status") == "error":
            lines.append(f"  ⚠️ API error: {api.get('error', '?')}")
        # else: no API, skip

        # Session data
        for s in stats:
            ctx   = s["context_used"]
            limit = s["context_limit"]
            inp   = s["input_tokens"]
            out   = s["output_tokens"]
            short_key = s["key"].split(":")[-1][:20]
            short_model = (s["model"] or "").split("/")[-1]

            parts = []
            if limit:
                parts.append(f"ctx {fmt_k(ctx)}/{fmt_k(limit)} {fmt_pct(ctx, limit)}")
            if inp or out:
                parts.append(f"session {fmt_k(inp)}in/{fmt_k(out)}out")

            # Today's request count for this session
            day_count = turns.get(s["key"], 0)
            if day_count:
                parts.append(f"{day_count} req today")

            if parts:
                lines.append(f"  [{short_key}] {short_model}: " + " | ".join(parts))

        # If no session data and no API data
        if not stats and api.get("status") not in ("ok", "error"):
            lines.append(f"  No active sessions found")

        lines.append("")

    return "\n".join(lines).rstrip()

# ── Telegram sender ────────────────────────────────────────────────────────────
def send_telegram(text, bot_token, chat_id):
    """Send a message via Telegram Bot API using MarkdownV2."""
    url  = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    body = json.dumps({
        "chat_id":    chat_id,
        "text":       text,
        "parse_mode": "Markdown",
    }).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": e.read().decode()[:300]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def resolve_telegram_target(cfg, sessions):
    """Extract bot token and primary DM chat ID from config/sessions."""
    bot_token = (
        cfg.get("channels", {}).get("telegram", {}).get("botToken")
        or os.environ.get("TELEGRAM_BOT_TOKEN")
    )
    chat_id = None
    # Find from sessions: look for a direct telegram session
    for key, s in sessions.items():
        if not isinstance(s, dict):
            continue
        dc = s.get("deliveryContext") or s.get("origin") or {}
        if dc.get("channel") == "telegram" and "direct" in key:
            to = dc.get("to", "")
            if to.startswith("telegram:"):
                chat_id = to.split(":")[-1]
                break
    return bot_token, chat_id

# ── Main ───────────────────────────────────────────────────────────────────────
def resolve_api_keys(providers):
    """
    For providers whose apiKey looks like a placeholder (all-caps env var name),
    look up the real key from auth-profiles.json.
    Mapping: profile name "openrouter:default" → provider "openrouter", etc.
    """
    profiles = load_json(AUTH_PROFILES_PATH, {}).get("profiles", {})
    # Build a lookup: provider_name → actual key from auth profiles
    profile_keys = {}
    for profile_name, profile in profiles.items():
        if not isinstance(profile, dict):
            continue
        key  = profile.get("key") or profile.get("apiKey") or profile.get("token")
        prov = profile.get("provider") or profile_name.split(":")[0]
        if key:
            profile_keys[prov.lower()] = key

    for name, pcfg in providers.items():
        current = pcfg.get("apiKey", "")
        # Placeholder detection: all-caps, no lowercase letters, e.g. "OPENROUTER_API_KEY"
        is_placeholder = current == current.upper() and "_" in current
        if is_placeholder:
            resolved = profile_keys.get(name.lower())
            if resolved:
                pcfg["apiKey"] = resolved

    return providers


def main():
    cfg      = load_json(CONFIG_PATH, {})
    sessions = load_json(SESSIONS_PATH, {})

    # Merge providers from both config files (openclaw.json + models.json)
    runtime_providers = cfg.get("models", {}).get("providers", {})
    legacy_providers = load_json(MODELS_PATH, {}).get("providers", {})
    providers = {}
    for src_name, src in [
        ("runtime", runtime_providers),
        ("legacy", legacy_providers),
    ]:
        for k, v in src.items():
            if k not in providers:
                providers[k] = {
                    "config": v,
                    "source": src_name,
                }

    # Resolve placeholder API keys from auth-profiles
    providers = resolve_api_keys({
        name: dict(meta["config"])
        for name, meta in providers.items()
    })

    if not providers:
        print("No providers found in config.")
        sys.exit(0)

    # Count today's agent turns per session key
    turns_today = count_today_turns()

    results = {}
    for name, pcfg in providers.items():
        source = "runtime" if name in runtime_providers else "legacy"
        session_stats = get_session_stats(name)

        # Ignore stale legacy-only providers that have no active sessions.
        if source == "legacy" and not session_stats:
            continue

        api_key   = pcfg.get("apiKey", "")
        base_url  = pcfg.get("baseUrl", "")
        ptype     = detect_type(name, base_url)

        checker   = CHECKERS.get(ptype)
        api_data  = {}
        if checker and api_key and not api_key.upper().startswith(("YOUR", "PLACEHOLDER", "INSERT")):
            api_data = checker(api_key, base_url)
        else:
            api_data = {"status": "no_api"}

        results[name] = {
            "type":          ptype,
            "api_data":      api_data,
            "session_stats": session_stats,
            "turns_today":   turns_today,
        }

    checked_at = datetime.now(timezone.utc).isoformat()

    # Persist to memory file
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps({"checked_at": checked_at, "providers": results}, indent=2))

    report = format_report(results, checked_at)
    print(report)

    if ONLY_STDOUT:
        return

    # Send to Telegram
    bot_token, chat_id = resolve_telegram_target(cfg, sessions)
    if not bot_token or not chat_id:
        print("\n[WARN] Could not resolve Telegram bot token or chat ID — skipping send.", file=sys.stderr)
        return

    result = send_telegram(report, bot_token, chat_id)
    if result.get("ok"):
        print(f"\n[OK] Sent to Telegram chat {chat_id}", file=sys.stderr)
    else:
        print(f"\n[ERR] Telegram send failed: {result.get('error') or result}", file=sys.stderr)

if __name__ == "__main__":
    main()
