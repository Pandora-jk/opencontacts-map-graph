# Infra Check (Run 44)

- Task: **Monitor disk usage:** Alert if >80%.
- UTC: 2026-03-09T04:34:13.720994Z

## Disk Usage
Root usage: /: 88% used (16G/19G, avail 2.4G)
ALERT: Root filesystem usage is 88% (>80%)
Inodes: /: 15% used
Top disk usage under / (depth 1):
16G	/
9.3G	/usr
4.9G	/home
1.5G	/var
143M	/opt
103M	/tmp
8.7M	/etc
24K	/snap
Reclaim candidates (review before cleanup):
- 628M /var/cache/apt (APT package cache)
- 366M /home/ubuntu/.cache (user cache)
- 130M /var/log/journal (systemd journals)
No deleted-but-open files detected
