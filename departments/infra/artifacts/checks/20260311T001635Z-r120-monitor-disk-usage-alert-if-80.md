# Infra Check (Run 120)

- Task: **Monitor disk usage:** Alert if >80%.
- UTC: 2026-03-11T00:16:35.043520Z

## Disk Usage
Root usage: /: 97% used (18G/18G, avail 706M)
CRITICAL: Root filesystem usage is 97% (>90%)
Inodes: /: 16% used
Top disk usage under / (depth 1):
18G	/
9.3G	/usr
6.6G	/home
1.5G	/var
143M	/opt
66M	/tmp
8.7M	/etc
24K	/snap
Reclaim candidates (review before cleanup):
- 617M /var/cache/apt (APT package cache)
- 197M /home/ubuntu/.cache/pip (pip download cache)
- 159M /var/log/journal (systemd journals)
- 103M /home/ubuntu/.cache/go-build (Go build cache)
- 3.9M /home/ubuntu/.openclaw/workspace/logs/night-infra.log (generated workspace log)
- 1.4M /home/ubuntu/.openclaw/workspace/logs/night-coding.log (generated workspace log)
- 236K /home/ubuntu/.openclaw/workspace/tools/__pycache__ (Python bytecode cache)
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
236K	/home/ubuntu/.openclaw/workspace/tools/__pycache__
Home cache cleanup helper available for allowlisted user-owned caches:
- Review: python3 tools/infra_home_cache_cleanup.py --path /home/ubuntu/.cache/pip --path /home/ubuntu/.cache/go-build
- Apply: python3 tools/infra_home_cache_cleanup.py --apply --path /home/ubuntu/.cache/pip --path /home/ubuntu/.cache/go-build
Workspace log cleanup helper available for repo-local generated logs:
- Review: python3 tools/infra_workspace_log_cleanup.py --path /home/ubuntu/.openclaw/workspace/logs/night-infra.log --path /home/ubuntu/.openclaw/workspace/logs/night-coding.log
- Apply: python3 tools/infra_workspace_log_cleanup.py --apply --path /home/ubuntu/.openclaw/workspace/logs/night-infra.log --path /home/ubuntu/.openclaw/workspace/logs/night-coding.log
Workspace cache cleanup helper available for repo-local caches:
- Review: python3 tools/infra_workspace_cache_cleanup.py --path /home/ubuntu/.openclaw/workspace/tools/__pycache__
- Apply: python3 tools/infra_workspace_cache_cleanup.py --apply --path /home/ubuntu/.openclaw/workspace/tools/__pycache__
Current-session writable workspace-log plan:
- Need about 1.1G reclaimed to reach <=90% on /
  All workspace logs total 5.3M across 2 path(s); short by 1.1G
  Review remaining workspace logs: python3 tools/infra_workspace_log_cleanup.py --path /home/ubuntu/.openclaw/workspace/logs/night-infra.log --path /home/ubuntu/.openclaw/workspace/logs/night-coding.log
  Host-level reclaim is still required after workspace-log cleanup
- Need about 3.0G reclaimed to reach <=80% on /
  All workspace logs total 5.3M across 2 path(s); short by 3.0G
  Review remaining workspace logs: python3 tools/infra_workspace_log_cleanup.py --path /home/ubuntu/.openclaw/workspace/logs/night-infra.log --path /home/ubuntu/.openclaw/workspace/logs/night-coding.log
  Host-level reclaim is still required after workspace-log cleanup
Current-session writable workspace-cache plan:
- Need about 1.1G reclaimed to reach <=90% on /
  All workspace caches total 236K across 1 path(s); short by 1.1G
  Review remaining workspace caches: python3 tools/infra_workspace_cache_cleanup.py --path /home/ubuntu/.openclaw/workspace/tools/__pycache__
  Host-level reclaim is still required after workspace-cache cleanup
- Need about 3.0G reclaimed to reach <=80% on /
  All workspace caches total 236K across 1 path(s); short by 3.0G
  Review remaining workspace caches: python3 tools/infra_workspace_cache_cleanup.py --path /home/ubuntu/.openclaw/workspace/tools/__pycache__
  Host-level reclaim is still required after workspace-cache cleanup
Allowlisted home-cache recovery plan:
- Need about 1.1G reclaimed to reach <=90% on /
  All allowlisted home caches total 300M across 2 path(s); short by 856M
  Review remaining home caches: python3 tools/infra_home_cache_cleanup.py --path /home/ubuntu/.cache/pip --path /home/ubuntu/.cache/go-build
  Additional host-level reclaim is still required after allowlisted home-cache cleanup
- Need about 3.0G reclaimed to reach <=80% on /
  All allowlisted home caches total 300M across 2 path(s); short by 2.7G
  Review remaining home caches: python3 tools/infra_home_cache_cleanup.py --path /home/ubuntu/.cache/pip --path /home/ubuntu/.cache/go-build
  Additional host-level reclaim is still required after allowlisted home-cache cleanup
Host-level recovery plan (sudo required for host-owned caches/logs):
- Need about 1.1G reclaimed to reach <=90% on /
  All host-level caches/logs total 776M across 2 path(s); short by 379M
  - /var/cache/apt: sudo apt-get clean
  - /var/log/journal: sudo journalctl --vacuum-time=7d
  Additional reclaim is still required after host-level cleanup
- Need about 3.0G reclaimed to reach <=80% on /
  All host-level caches/logs total 776M across 2 path(s); short by 2.2G
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
6.6G	/home/ubuntu
1.8G	/home/ubuntu/.npm-global/lib
1.8G	/home/ubuntu/.npm-global
1.6G	/home/ubuntu/.gradle
1.4G	/home/ubuntu/.gradle/caches
965M	/home/ubuntu/.android-sdk
962M	/home/ubuntu/.local
706M	/home/ubuntu/.local/share
366M	/home/ubuntu/.cache
359M	/home/ubuntu/.android-sdk/system-images
317M	/home/ubuntu/.android-sdk/cmdline-tools
312M	/home/ubuntu/go
Home review hint: prioritize build/package caches before SDKs or active workspaces
Protected install roots under /home/ubuntu (manual review, not safe cache cleanup):
- 1.8G /home/ubuntu/.npm-global (global npm packages; removing may break installed CLIs)
- 964M /home/ubuntu/.android-sdk (Android SDK toolchains; removing breaks Android builds)
- 469M /home/ubuntu/.local/share/pipx/venvs (pipx virtualenvs; removing breaks installed pipx apps)
- 224M /home/ubuntu/.local/share/claude/versions (Claude local app versions; treat as installed software)
Protected-root hint: reclaim caches first; remove these only when intentionally uninstalling the owning toolchain
No deleted-but-open files detected
