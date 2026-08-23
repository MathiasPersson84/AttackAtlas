# Security Policy

AttackAtlas is intended for authorized security testing, labs, CTFs and penetration-testing engagements.

## Sensitive data

AttackAtlas projects may contain:

- credentials and hashes
- host and network information
- Nmap/NSE output
- assessment notes
- attack paths and access relationships

Credential secrets are currently stored in plaintext in the local SQLite database. Complete Markdown exports may also contain plaintext credentials.

Keep the AttackAtlas data directory and exported archives on trusted or encrypted storage. Do not commit real engagement data to a public repository.

AttackAtlas binds to `127.0.0.1` by default. If you intentionally expose it on another interface, treat the application as containing sensitive data and protect access accordingly.

## Reporting a vulnerability

Please avoid publishing exploit details for a newly discovered AttackAtlas vulnerability before maintainers have had a reasonable opportunity to investigate and address it.

If the GitHub repository has Private Vulnerability Reporting or private security advisories enabled, prefer that channel.
