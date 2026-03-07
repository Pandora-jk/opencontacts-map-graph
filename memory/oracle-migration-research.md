# Oracle Cloud Migration Research
_Researched 2026-02-26_

## Context
Jim is running openclaw on AWS free tier. Evaluating move to Oracle Cloud Always Free.
openclaw process: ~472 MB RAM, Node.js, outbound API calls only (Telegram, NVIDIA, etc.)

## AWS Free Tier — Summary
- t2/t3.micro: 1 vCPU, 1 GB RAM — **12 months only** (new accounts from July 2025: 6 months)
- No permanent free compute
- Cost after free tier: ~$8.50/month
- 1 GB RAM is tight — OS takes ~250 MB, leaves ~750 MB headroom for openclaw (~472 MB)

## Oracle Always Free — Summary
- **VM.Standard.A1.Flex** (ARM64 Ampere): 4 OCPUs + 24 GB RAM pool, permanent
  - Can split: e.g. 1×4-OCPU/24GB, or 2×2-OCPU/12GB, etc.
- **2× AMD micro** (x86): 1 GB RAM each, permanent (bonus on top)
- **200 GB** block storage, **10 TB/month** egress
- No expiry as long as account stands

## Three Real Risks

### 1. Capacity at provisioning (one-time problem)
- A1 instances frequently "out of capacity" — popular regions oversubscribed
- Sydney (ap-sydney-1): moderately available, not worst, not best
- **Fix**: use retry script https://github.com/hitrov/oci-arm-host-capacity
  OR upgrade to Pay-As-You-Go (PAYG) — often unlocks capacity immediately
- Once running, it stays running

### 2. Account termination without warning (ongoing risk)
- Oracle has a pattern of terminating always-free accounts, no notice, no appeal, no data recovery
- HN thread Feb 2025: https://news.ycombinator.com/item?id=42901897
- Triggers: sustained high CPU (mistaken for crypto mining), failed card verification, opaque fraud detection
- **Mitigation**: upgrade to PAYG after provisioning (free resources stay free, better account stability)
  Set $5/month spending alert in OCI Cost Management

### 3. Idle reclamation
- Oracle stops A1 if CPU + network + memory all stay under 20% for 7-day rolling window
- Email warning + 7-day grace period before shutdown
- openclaw making regular API calls should stay above threshold naturally
- **Mitigation if quiet**: hourly cron job (e.g. `curl` to any external API)

## ARM64 Compatibility
- Non-issue for openclaw stack
- Node.js has official ARM64 binaries
- All pure-JS npm packages work; Python fine
- No native module gotchas for this workload

## Migration Plan (when ready)
1. Sign up Oracle — choose **ap-sydney-1** as home region (cannot change later)
2. Use retry script or upgrade PAYG to provision A1 (may take hours to days)
3. Immediately upgrade to PAYG after getting instance
4. Set $5/month spending alert in OCI Cost Management
5. Install Node.js (nvm or NodeSource), copy `~/.openclaw/`, workspace, tools
6. Re-run `tools/patch-openclaw-reply.py`
7. Set up systemd service, verify
8. Add hourly idle-prevention cron if bot goes quiet for days at a time
9. Keep config in git — rebuild time ~20 min if Oracle nukes account

## Alternative: Hetzner CAX11
- 2 ARM vCPUs, 4 GB RAM, 40 GB SSD, 20 TB traffic
- ~€3.79/month (~$6 AUD)
- No termination risk, real SLA, same ARM64 architecture
- Worth it if ~$6/month is acceptable vs Oracle's reliability uncertainty

## Decision Factors
- AWS free tier expires in ~5 months (approx Aug 2026) — no urgency
- Plan: migrate to Oracle a month or two before expiry
- If can rebuild from git in 20 min → Oracle is fine
- If zero-drama SLA needed → Hetzner at ~$6/month as fallback
