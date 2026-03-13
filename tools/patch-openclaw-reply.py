#!/usr/bin/env python3
"""
Permanent patches for OpenClaw dist files.
Safe to run repeatedly — checks if each patch is already applied before modifying.
Run automatically via systemd ExecStartPre before the gateway starts.

Patch 1 (reply-*.js): Add context window % to usage footer + italic formatting.
  Before: Usage: 68k in / 47 out · est $0.0000
  After:  _Usage: 68k in / 47 out · est $0.0000 · ctx 53%_

Patch 2 (reply-*.js): Smart prefix spacing — no extra space when prefix ends with \\n.
  Allows responsePrefix like "*〔model〕*\\n" to put body on its own line.

Patch 3 (image-*.js): Fix Nemotron malformed <think> close tag.
  Nemotron Ultra outputs bare 'think>' (no '</') as the closing tag.
  Without this fix, OpenClaw's regex never finds </think>, strips everything
  from <think> to end of text, and the reply payload is empty — nothing sent.

Patch 4 (openai-completions.js): Add NVIDIA and Groq to isNonStandard providers.
  These providers don't support the 'developer' role (OpenAI-specific) but were
  not in the isNonStandard list, causing openclaw to send role='developer' for
  the system prompt on reasoning models, resulting in HTTP 400 "Unexpected message
  role." which openclaw mis-reports as "Message ordering conflict".

Patch 5 (net/tailnet/ws/daemon bundles): Guard os.networkInterfaces() calls.
  Some restricted environments raise:
    SystemError [ERR_SYSTEM_ERROR]: uv_interface_addresses returned ...
  These commands should degrade gracefully instead of crashing.
"""

import os
import re
import sys
from pathlib import Path

DIST = Path(
    os.environ.get(
        "OPENCLAW_DIST",
        str(Path.home() / ".npm-global/lib/node_modules/openclaw/dist"),
    )
)
PI_AI = Path(
    os.environ.get(
        "OPENCLAW_PI_AI_DIST",
        str(
            Path.home()
            / ".npm-global/lib/node_modules/openclaw/node_modules/@mariozechner/pi-ai/dist/providers"
        ),
    )
)


def iter_dist_candidates(*patterns):
    seen = {}
    for pattern in patterns:
        for path in sorted(DIST.rglob(pattern)):
            if not path.is_file() or path.suffix != ".js":
                continue
            seen[path] = path
    return list(seen.values())


def patch_reply():
    """Patch reply bundles: ctx% footer, italic footer, smart prefix spacing."""
    candidates = [
        path
        for path in iter_dist_candidates("reply-*.js", "pi-embedded-*.js", "subagent-registry-*.js")
        if not path.name.startswith("reply-prefix-")
    ]
    if not candidates:
        print("[patch-openclaw] WARNING: no reply bundle found — skipping reply patches", file=sys.stderr)
        return

    ctx_return_old = (
        'return `Usage: ${inputLabel} in / ${outputLabel} out'
        '${costLabel ? ` · est ${costLabel}` : ""}`;'
    )
    ctx_return_new = (
        'const ctxPctSuffix = params.contextPct != null ? ` · ctx ${params.contextPct}%` : "";\n'
        '\treturn `_Usage: ${inputLabel} in / ${outputLabel} out'
        '${costLabel ? ` · est ${costLabel}` : ""}${ctxPctSuffix}_`;'
    )
    ctx_call_old = (
        "formatResponseUsageLine({\n"
        "\t\t\t\tusage,\n"
        "\t\t\t\tshowCost,\n"
        "\t\t\t\tcostConfig: showCost ? resolveModelCostConfig({\n"
        "\t\t\t\t\tprovider: providerUsed,\n"
        "\t\t\t\t\tmodel: modelUsed,\n"
        "\t\t\t\t\tconfig: cfg\n"
        "\t\t\t\t}) : void 0\n"
        "\t\t\t});"
    )
    ctx_call_new = (
        "formatResponseUsageLine({\n"
        "\t\t\t\tusage,\n"
        "\t\t\t\tshowCost,\n"
        "\t\t\t\tcostConfig: showCost ? resolveModelCostConfig({\n"
        "\t\t\t\t\tprovider: providerUsed,\n"
        "\t\t\t\t\tmodel: modelUsed,\n"
        "\t\t\t\t\tconfig: cfg\n"
        "\t\t\t\t}) : void 0,\n"
        '\t\t\t\tcontextPct: typeof usage.input === "number" && contextTokensUsed'
        " ? Math.round(usage.input / contextTokensUsed * 100) : void 0\n"
        "\t\t\t});"
    )
    italic_return_old = (
        'const ctxPctSuffix = params.contextPct != null ? ` · ctx ${params.contextPct}%` : "";\n'
        '\treturn `Usage: ${inputLabel} in / ${outputLabel} out'
        '${costLabel ? ` · est ${costLabel}` : ""}${ctxPctSuffix}`;'
    )
    italic_return_new = (
        'const ctxPctSuffix = params.contextPct != null ? ` · ctx ${params.contextPct}%` : "";\n'
        '\treturn `_Usage: ${inputLabel} in / ${outputLabel} out'
        '${costLabel ? ` · est ${costLabel}` : ""}${ctxPctSuffix}_`;'
    )
    old_space = (
        'if (effectivePrefix && text && text.trim() !== HEARTBEAT_TOKEN && '
        '!text.startsWith(effectivePrefix)) text = `${effectivePrefix} ${text}`;'
    )
    new_space = (
        'if (effectivePrefix && text && text.trim() !== HEARTBEAT_TOKEN && '
        '!text.startsWith(effectivePrefix)) text = effectivePrefix.endsWith("\\n") '
        '? `${effectivePrefix}${text}` : `${effectivePrefix} ${text}`;'
    )
    space_marker = 'effectivePrefix.endsWith("\\n")'

    matched_any = False
    for target in candidates:
        data = target.read_text()
        if not any(marker in data for marker in ("formatResponseUsageLine", "ctxPctSuffix", old_space, space_marker)):
            continue

        matched_any = True
        changed = False

        if "ctxPctSuffix" not in data:
            if ctx_return_old in data and ctx_call_old in data:
                data = data.replace(ctx_return_old, ctx_return_new, 1)
                data = data.replace(ctx_call_old, ctx_call_new, 1)
                changed = True
                print(f"[patch-openclaw] ctx%+italic footer patch applied: {target.name}", file=sys.stderr)
        else:
            if "_Usage:" not in data and italic_return_old in data:
                data = data.replace(italic_return_old, italic_return_new, 1)
                changed = True
                print(f"[patch-openclaw] italic footer patch applied: {target.name}", file=sys.stderr)

        if space_marker not in data and old_space in data:
            data = data.replace(old_space, new_space, 1)
            changed = True
            print(f"[patch-openclaw] smart-prefix-spacing patch applied: {target.name}", file=sys.stderr)

        if changed:
            target.write_text(data)
        elif "ctxPctSuffix" in data or "_Usage:" in data or space_marker in data:
            print(f"[patch-openclaw] reply patches already applied: {target.name}", file=sys.stderr)

    if not matched_any:
        print("[patch-openclaw] reply patches already applied or no matching targets found", file=sys.stderr)


def patch_image():
    """Patch image bundles: fix Nemotron malformed </think> tag."""
    image_files = [
        path
        for path in iter_dist_candidates("image-*.js")
        if "stripReasoningTagsFromText" in path.read_text()
    ]
    if not image_files:
        print("[patch-openclaw] WARNING: image-*.js target not found — skipping think-tag patch", file=sys.stderr)
        return

    old = (
        "function stripReasoningTagsFromText(text, options) {\n"
        "\tif (!text) return text;\n"
        "\tif (!QUICK_TAG_RE.test(text)) return text;"
    )
    new = (
        "function stripReasoningTagsFromText(text, options) {\n"
        "\tif (!text) return text;\n"
        "\t// Normalize Nemotron malformed close tag: bare 'think>' at line start -> '</think>'\n"
        '\ttext = text.replace(/^think(?:ing)?>$/mg, "</think>");\n'
        "\tif (!QUICK_TAG_RE.test(text)) return text;"
    )

    matched_any = False
    for target in image_files:
        data = target.read_text()
        if "Normalize Nemotron" in data:
            matched_any = True
            print(f"[patch-openclaw] think-tag patch already applied: {target.name}", file=sys.stderr)
            continue
        if old not in data:
            continue
        matched_any = True
        data = data.replace(old, new, 1)
        target.write_text(data)
        print(f"[patch-openclaw] think-tag patch applied: {target.name}", file=sys.stderr)

    if not matched_any:
        print("[patch-openclaw] think-tag patch already applied or no matching targets found", file=sys.stderr)


def patch_compat():
    """Patch openai-completions.js: add NVIDIA and Groq to isNonStandard providers.

    These providers don't support the 'developer' role. Without this patch,
    openclaw sends role='developer' for the system prompt on reasoning models,
    getting HTTP 400 "Unexpected message role." from NVIDIA/Groq.
    """
    target = PI_AI / "openai-completions.js"
    if not target.exists():
        print(f"[patch-openclaw] WARNING: {target} not found — skipping compat patch", file=sys.stderr)
        return

    data = target.read_text()

    if 'provider === "nvidia"' in data:
        print(f"[patch-openclaw] compat patch already applied: {target.name}", file=sys.stderr)
        return

    old = (
        '        provider === "opencode" ||\n'
        '        baseUrl.includes("opencode.ai");'
    )
    new = (
        '        provider === "opencode" ||\n'
        '        baseUrl.includes("opencode.ai") ||\n'
        '        provider === "nvidia" ||\n'
        '        baseUrl.includes("nvidia.com") ||\n'
        '        provider === "groq" ||\n'
        '        baseUrl.includes("groq.com");'
    )

    if old not in data:
        print(f"[patch-openclaw] WARNING: compat target not found in {target.name} — skipping", file=sys.stderr)
        return

    data = data.replace(old, new, 1)
    target.write_text(data)
    print(f"[patch-openclaw] compat patch applied: {target.name}", file=sys.stderr)


def patch_tailnet():
    """Patch dist bundles: guard os.networkInterfaces() for environments that throw.

    Some environments can raise:
      SystemError [ERR_SYSTEM_ERROR]: uv_interface_addresses returned ...
    This should not break CLI status/health commands.
    """
    candidates = iter_dist_candidates("tailnet-*.js", "net-*.js", "ws-*.js", "daemon-cli.js")
    if not candidates:
        print("[patch-openclaw] WARNING: no network bundle found — skipping network patch", file=sys.stderr)
        return

    tailnet_old = "const ifaces = os.networkInterfaces();"
    tailnet_new = (
        "let ifaces;\n"
        "\ttry {\n"
        "\t\tifaces = os.networkInterfaces();\n"
        "\t} catch (networkInterfacesSafeError) {\n"
        "\t\treturn {\n"
        "\t\t\tipv4: [],\n"
        "\t\t\tipv6: []\n"
        "\t\t};\n"
        "\t}"
    )
    lan_old = "function pickPrimaryLanIPv4() {\n\tconst nets = os.networkInterfaces();"
    lan_new = (
        "function pickPrimaryLanIPv4() {\n"
        "\tlet nets;\n"
        "\ttry {\n"
        "\t\tnets = os.networkInterfaces();\n"
        "\t} catch (networkInterfacesSafeError) {\n"
        "\t\treturn;\n"
        "\t}"
    )

    matched_any = False
    for target in candidates:
        data = target.read_text()
        changed = False

        if tailnet_old in data:
            matched_any = True
            data = data.replace(tailnet_old, tailnet_new, 1)
            changed = True

        if lan_old in data:
            matched_any = True
            data = data.replace(lan_old, lan_new, 1)
            changed = True

        if changed:
            target.write_text(data)
            print(f"[patch-openclaw] network patch applied: {target.name}", file=sys.stderr)
        elif "networkInterfacesSafeError" in data:
            matched_any = True
            print(f"[patch-openclaw] network patch already applied: {target.name}", file=sys.stderr)

    if not matched_any:
        print("[patch-openclaw] WARNING: networkInterfaces targets not found — skipping", file=sys.stderr)


if __name__ == "__main__":
    patch_reply()
    patch_image()
    patch_compat()
    patch_tailnet()
