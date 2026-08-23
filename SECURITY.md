# Security Policy

AttackAtlas is designed for authorized security testing, labs, CTFs, and penetration-testing engagements.

## Sensitive data

Projects may contain credentials, hashes, network information, scan output, and notes. Treat the AttackAtlas data directory and Markdown exports as sensitive material.

Credentials are currently stored in the local SQLite database without application-level encryption. Markdown exports may contain credential secrets in clear text.

## Reporting a vulnerability

Please avoid publishing exploit details for a newly discovered AttackAtlas vulnerability before maintainers have had a reasonable opportunity to address it. If the repository enables private security advisories, prefer that channel.
