# AttackAtlas v0.1.0-alpha

AttackAtlas is a lightweight, local-first visual workspace for documenting hosts, identities, credentials, services, and attack paths during authorized penetration tests, CTFs, and lab environments.

This initial public alpha includes Nmap XML import, project/host management, users and encrypted credential storage, multi-edge attack-path visualization, structured host notes, screenshot evidence, a live Report/Timeline workflow, Markdown exports, SVG map snapshots, and Docker deployment.

## Important

This is an alpha release. Back up both `data/` and `secrets/` before upgrading.

Credential secrets are encrypted in SQLite using AES-256-GCM, but the current local vault is auto-unlocked. Anyone with both the database and its matching vault key can decrypt credentials.

The live `report.md` export redacts credential secrets by default. Other full project exports may contain sensitive plaintext assessment material and must be handled accordingly.

## License

GNU General Public License v3.0 (`GPL-3.0-only`).
