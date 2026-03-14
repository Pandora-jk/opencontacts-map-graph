# Infra Check (Run 283)

- Task: **Check for system updates** daily and report count.
- UTC: 2026-03-14T17:42:10.827791Z

## Pending Updates
5 pending updates
INFO: auto-updates enabled (APT::Periodic::Update-Package-Lists=1, APT::Periodic::Unattended-Upgrade=1)
WARN: unattended-upgrades last started at 2026-03-14 13:06 UTC (4h ago) but no completion was logged
INFO: package-manager activity: no active apt/dpkg/unattended-upgrades process visible
WARN: apt periodic stamps recorded fresh update discovery at 2026-03-14 13:06 UTC but no newer unattended-upgrades/upgrade completion stamp was written (latest completion stamp: 2026-03-14 06:26 UTC)
RISK: unattended-upgrades appears stalled; last start was 2026-03-14 13:06 UTC and no active package-manager process is visible
RISK: security-sensitive updates pending: kernel=linux-aws, linux-headers-aws, linux-image-aws, linux-libc-dev, linux-tools-common
HARDENING: schedule a maintenance reboot after these updates land

## Package Listing
linux-aws/noble-updates,noble-security 6.17.0-1009.9~24.04.2 amd64 [upgradable from: 6.17.0-1007.7~24.04.1]
linux-headers-aws/noble-updates,noble-security 6.17.0-1009.9~24.04.2 amd64 [upgradable from: 6.17.0-1007.7~24.04.1]
linux-image-aws/noble-updates,noble-security 6.17.0-1009.9~24.04.2 amd64 [upgradable from: 6.17.0-1007.7~24.04.1]
linux-libc-dev/noble-updates,noble-security 6.8.0-106.106 amd64 [upgradable from: 6.8.0-101.101]
linux-tools-common/noble-updates,noble-security 6.8.0-106.106 all [upgradable from: 6.8.0-101.101]
