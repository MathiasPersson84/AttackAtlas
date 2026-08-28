# Security Policy

AttackAtlas is intended for authorized security testing, labs, CTFs and penetration-testing engagements.

## Sensitive data

AttackAtlas projects may contain:

- credentials and hashes
- host and network information
- Nmap/NSE output
- assessment notes
- attack paths and access relationships

Credential secrets are encrypted at rest in SQLite using AES-256-GCM. AttackAtlas automatically creates a random 256-bit local vault key in `./secrets/credential-vault.json`.

This is protection for the database **at rest**, not authentication. There is currently no master password: the running application can automatically load the local vault key. If an attacker obtains both `attackatlas.db` and `credential-vault.json`, they can decrypt stored credentials.

Existing plaintext credentials from older AttackAtlas databases are migrated to encrypted values on first startup. If an encrypted database is present but the vault key is missing, AttackAtlas intentionally refuses to start rather than generate a replacement key.

The key-file format is versioned and structured so a future master-password layer can wrap the existing data-encryption key without re-encrypting every credential. Credential API responses are marked `Cache-Control: no-store`; however, secrets are still available to the running application and browser when explicitly displayed/copied. Complete Markdown exports may still contain plaintext credentials.

Keep the AttackAtlas `data/` and `secrets/` directories and exported archives on trusted or encrypted storage. Back up the database and vault key together, but do not publish either. Do not commit real engagement data to a public repository.

AttackAtlas binds to `127.0.0.1` by default. If you intentionally expose it on another interface, treat the application as containing sensitive data and protect access accordingly.

## Reporting a vulnerability

Please avoid publishing exploit details for a newly discovered AttackAtlas vulnerability before maintainers have had a reasonable opportunity to investigate and address it.

If the GitHub repository has Private Vulnerability Reporting or private security advisories enabled, prefer that channel.
