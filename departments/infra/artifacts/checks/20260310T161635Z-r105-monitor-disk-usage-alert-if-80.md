# Infra Check (Run 105)

- Task: **Monitor disk usage:** Alert if >80%.
- UTC: 2026-03-10T16:16:35.815960Z

## Disk Usage
Root usage: /: 100% used (18G/18G, avail 120M)
CRITICAL: Root filesystem usage is 100% (>90%)
Inodes: /: 16% used
Top disk usage under / (depth 1):
18G	/
9.3G	/usr
7.2G	/home
1.5G	/var
143M	/opt
40M	/tmp
8.7M	/etc
24K	/snap
Reclaim candidates (review before cleanup):
- 617M /var/cache/apt (APT package cache)
- 197M /home/ubuntu/.cache/pip (pip download cache)
- 159M /var/log/journal (systemd journals)
- 103M /home/ubuntu/.cache/go-build (Go build cache)
- 136K /home/ubuntu/.openclaw/workspace/tools/__pycache__ (Python bytecode cache)
Largest paths under /var/cache/apt:
617M	/var/cache/apt
500M	/var/cache/apt/archives
4.0K	/var/cache/apt/archives/partial
APT cleanup hint: sudo apt-get clean
Largest paths under /home/ubuntu/.cache/pip:
198M	/home/ubuntu/.cache/pip/http-v2
198M	/home/ubuntu/.cache/pip
50M	/home/ubuntu/.cache/pip/http-v2/0
21M	/home/ubuntu/.cache/pip/http-v2/1
20M	/home/ubuntu/.cache/pip/http-v2/5
17M	/home/ubuntu/.cache/pip/http-v2/c
Largest paths under /var/log/journal:
160M	/var/log/journal/ec20eddcc7a50fd4b688e3dd6a473294
160M	/var/log/journal
Journal review hint: journalctl --disk-usage
Journal vacuum hint: sudo journalctl --vacuum-time=7d
Largest paths under /home/ubuntu/.cache/go-build:
103M	/home/ubuntu/.cache/go-build
12M	/home/ubuntu/.cache/go-build/3a
8.1M	/home/ubuntu/.cache/go-build/0c
6.5M	/home/ubuntu/.cache/go-build/36
4.7M	/home/ubuntu/.cache/go-build/5a
4.0M	/home/ubuntu/.cache/go-build/d9
Largest paths under /home/ubuntu/.openclaw/workspace/tools/__pycache__:
136K	/home/ubuntu/.openclaw/workspace/tools/__pycache__
Home cache cleanup helper available for allowlisted user-owned caches:
- Review: python3 tools/infra_home_cache_cleanup.py --path /home/ubuntu/.cache/pip --path /home/ubuntu/.cache/go-build
- Apply: python3 tools/infra_home_cache_cleanup.py --apply --path /home/ubuntu/.cache/pip --path /home/ubuntu/.cache/go-build
Workspace cache cleanup helper available for repo-local caches:
- Review: python3 tools/infra_workspace_cache_cleanup.py --path /home/ubuntu/.openclaw/workspace/tools/__pycache__
- Apply: python3 tools/infra_workspace_cache_cleanup.py --apply --path /home/ubuntu/.openclaw/workspace/tools/__pycache__
Current-session writable workspace-cache plan:
- Need about 1.7G reclaimed to reach <=90% on /
  All workspace caches total 136K across 1 path(s); short by 1.7G
  Review remaining workspace caches: python3 tools/infra_workspace_cache_cleanup.py --path /home/ubuntu/.openclaw/workspace/tools/__pycache__
  Host-level reclaim is still required after workspace-cache cleanup
- Need about 3.5G reclaimed to reach <=80% on /
  All workspace caches total 136K across 1 path(s); short by 3.5G
  Review remaining workspace caches: python3 tools/infra_workspace_cache_cleanup.py --path /home/ubuntu/.openclaw/workspace/tools/__pycache__
  Host-level reclaim is still required after workspace-cache cleanup
Allowlisted home-cache recovery plan:
- Need about 1.7G reclaimed to reach <=90% on /
  All allowlisted home caches total 300M across 2 path(s); short by 1.4G
  Review remaining home caches: python3 tools/infra_home_cache_cleanup.py --path /home/ubuntu/.cache/pip --path /home/ubuntu/.cache/go-build
  Additional host-level reclaim is still required after allowlisted home-cache cleanup
- Need about 3.5G reclaimed to reach <=80% on /
  All allowlisted home caches total 300M across 2 path(s); short by 3.2G
  Review remaining home caches: python3 tools/infra_home_cache_cleanup.py --path /home/ubuntu/.cache/pip --path /home/ubuntu/.cache/go-build
  Additional host-level reclaim is still required after allowlisted home-cache cleanup
Host-level recovery plan (sudo required for host-owned caches/logs):
- Need about 1.7G reclaimed to reach <=90% on /
  All host-level caches/logs total 776M across 2 path(s); short by 965M
  - /var/cache/apt: sudo apt-get clean
  - /var/log/journal: sudo journalctl --vacuum-time=7d
  Additional reclaim is still required after host-level cleanup
- Need about 3.5G reclaimed to reach <=80% on /
  All host-level caches/logs total 776M across 2 path(s); short by 2.8G
  - /var/cache/apt: sudo apt-get clean
  - /var/log/journal: sudo journalctl --vacuum-time=7d
  Additional reclaim is still required after host-level cleanup
Review-only cache roots (not safe broad cleanup targets):
- 366M /home/ubuntu/.cache (shared cache root; review allowlisted build/package caches before deleting app state)
Largest paths under /home/ubuntu/.cache:
366M	/home/ubuntu/.cache
198M	/home/ubuntu/.cache/pip/http-v2
198M	/home/ubuntu/.cache/pip
103M	/home/ubuntu/.cache/go-build
67M	/home/ubuntu/.cache/node-gyp/22.22.0
67M	/home/ubuntu/.cache/node-gyp
Cache review hint: focus on package/build caches before deleting app state
Largest paths under /home/ubuntu (review-only):
7.2G	/home/ubuntu
2.4G	/home/ubuntu/.gradle
1.9G	/home/ubuntu/.gradle/caches
1.8G	/home/ubuntu/.npm-global/lib
1.8G	/home/ubuntu/.npm-global
965M	/home/ubuntu/.android-sdk
962M	/home/ubuntu/.local
706M	/home/ubuntu/.local/share
410M	/home/ubuntu/.gradle/wrapper
366M	/home/ubuntu/.cache
359M	/home/ubuntu/.android-sdk/system-images
317M	/home/ubuntu/.android-sdk/cmdline-tools
Home review hint: prioritize build/package caches before SDKs or active workspaces
Protected install roots under /home/ubuntu (manual review, not safe cache cleanup):
- 1.8G /home/ubuntu/.npm-global (global npm packages; removing may break installed CLIs)
- 964M /home/ubuntu/.android-sdk (Android SDK toolchains; removing breaks Android builds)
- 469M /home/ubuntu/.local/share/pipx/venvs (pipx virtualenvs; removing breaks installed pipx apps)
- 224M /home/ubuntu/.local/share/claude/versions (Claude local app versions; treat as installed software)
Protected-root hint: reclaim caches first; remove these only when intentionally uninstalling the owning toolchain
No deleted-but-open files detected
