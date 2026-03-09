# Infra Check (Run 56)

- Task: **Monitor disk usage:** Alert if >80%.
- UTC: 2026-03-09T12:38:18.614247Z

## Disk Usage
Root usage: /: 100% used (19G/19G, avail 151M)
CRITICAL: Root filesystem usage is 100% (>90%)
Inodes: /: 15% used
Top disk usage under / (depth 1):
18G	/
9.3G	/usr
7.1G	/home
1.5G	/var
143M	/opt
106M	/tmp
8.7M	/etc
24K	/snap
Reclaim candidates (review before cleanup):
- 628M /var/cache/apt (APT package cache)
- 366M /home/ubuntu/.cache (user cache)
- 143M /var/log/journal (systemd journals)
Largest paths under /var/cache/apt:
628M	/var/cache/apt
511M	/var/cache/apt/archives
4.0K	/var/cache/apt/archives/partial
APT cleanup hint: sudo apt-get clean
Largest paths under /home/ubuntu/.cache:
366M	/home/ubuntu/.cache
198M	/home/ubuntu/.cache/pip/http-v2
198M	/home/ubuntu/.cache/pip
103M	/home/ubuntu/.cache/go-build
67M	/home/ubuntu/.cache/node-gyp/22.22.0
67M	/home/ubuntu/.cache/node-gyp
Cache review hint: focus on package/build caches before deleting app state
Largest paths under /var/log/journal:
144M	/var/log/journal/ec20eddcc7a50fd4b688e3dd6a473294
144M	/var/log/journal
Journal review hint: journalctl --disk-usage
Journal vacuum hint: sudo journalctl --vacuum-time=7d
Largest paths under /home/ubuntu (review-only):
7.1G	/home/ubuntu
2.3G	/home/ubuntu/.gradle
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
No deleted-but-open files detected
