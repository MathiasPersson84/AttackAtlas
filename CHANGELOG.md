# Changelog

All notable public changes to AttackAtlas are documented in this file.

## [0.1.0-alpha] - 2026-08-31

Initial public alpha release.

### Added

- Local-first project workspaces with persistent SQLite storage.
- Visual host canvas with free positioning, pan, zoom, fit, domain grouping, and SVG snapshot export.
- Host inventory with hostname, domain/FQDN, OS/device templates, status, notes, and attacker-machine designation.
- Nmap XML import at project or host level, including merged services, NSE output, raw per-port XML, and scan history.
- Users/accounts with manual creation, CSV import, host/domain grouping, editing, and quick-copy actions.
- Credential manager supporting passwords, NTLM/hashes, SSH keys, tokens, API keys, cookies, and custom credential types.
- AES-256-GCM encryption for credential secrets at rest with a separately persisted local vault key.
- Attack-path relationships with directed/undirected edges, labels, editing, deletion, and multiple parallel edges between the same hosts.
- Structured host activity notes using Markdown, categories, timestamps, tags, and screenshot/evidence attachments.
- Live Report view that automatically reflects linked host notes.
- Editable project-level report text and chronological Timeline view.
- Markdown report export with portable evidence assets and credential secrets redacted in `report.md` by default.
- Full project Markdown ZIP export for assessment data, with explicit warning when plaintext credential material is included.
- Docker deployment with a nonstandard localhost default port (`127.0.0.1:7843`).
- GitHub contribution, security, CI, issue, and pull-request templates.

### Fixed

- Parallel attack-path relationships between the same pair of hosts are rendered on separate lanes instead of overlapping.
- GUI branding markup corrected so the frontend builds successfully.
- Reporting controls now use AttackAtlas-consistent dark button styling instead of browser-native light buttons.

### Security

- Credential secrets are encrypted before being stored in SQLite.
- The vault refuses to silently replace a missing key when encrypted credentials already exist.
- Credential/vault API responses use no-cache headers.
- Runtime data and vault secrets are excluded from Git tracking.
- AttackAtlas binds to localhost by default and should not be exposed directly to untrusted networks.

### Known alpha limitations

- The local credential vault is auto-unlocked; there is not yet a master-password lock/unlock workflow.
- Anyone who obtains both the database and matching vault key can decrypt stored credentials.
- API and database compatibility may change during the alpha phase.
- AttackAtlas is intended for authorized security testing, labs, and CTF environments.
