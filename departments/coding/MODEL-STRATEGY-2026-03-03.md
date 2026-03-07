# Coding Model Strategy (2026-03-03)

## Decision
- **Primary for complex coding:** `nvidia/qwen/qwen3.5-397b-a17b`
- **First fallback:** `nvidia/moonshotai/kimi-k2-thinking`
- **Cheap utility model:** `zai/glm-4.7-Flash` for heartbeat/triage/summaries only

## Why
- `qwen3.5-397b` gives strongest coding/reasoning quality in your currently configured free/low-cost stack.
- Kimi is strong for agentic reasoning and tool-use, but it is better as fallback/secondary to control spend and reliability variance.
- Z.AI Flash is valid and very cheap/free for lightweight tasks, but not ideal as final authority for high-risk refactors.

## About "moonshine"
- Interpreting "moonshine" as **Moonshot/Kimi** (likely typo). If you meant a different provider/model, update this file and routing.

## Source Check (current)
- Gemini API rate limits (free tier): https://ai.google.dev/gemini-api/docs/quota
- Gemini API pricing: https://ai.google.dev/gemini-api/docs/pricing
- Z.AI pricing overview: https://docs.z.ai/guides/overview/pricing
- Moonshot Kimi Open Platform update (K2 thinking + pricing updates): https://platform.moonshot.ai/blog/posts/Kimi_API_Newsletter
- NVIDIA NIM program access overview: https://docs.api.nvidia.com/nim/docs/product

## Guardrails
- Route complex implementation/security/debug tasks to primary or first fallback only.
- Use flash-tier models for planning, summarization, and low-risk automation.
- Re-evaluate model routing weekly based on failure rate, latency, and test pass outcomes.
