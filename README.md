# AttackAtlas

AttackAtlas is a lightweight, local-first workspace for mapping hosts, services, credentials and attack paths during penetration tests, CTFs and lab environments.

Everything runs locally and is accessed through a browser.

![AttackAtlas overview](docs/images/attackatlas-overview.png)

### Host and credential management

| Add host | Credential manager |
| --- | --- |
| ![Add a host using a template](docs/images/add-host.png) | ![Manage project credentials](docs/images/credential-manager.png) |


## Features

- Free-form canvas with draggable hosts and persistent layouts
- Visual, editable attack paths between systems
- Host templates for common Windows, Linux and macOS systems
- Nmap XML import with service, NSE and raw per-port scan output
- Account and credential management with per-host associations
- Per-host services, credentials and notes
- Project workspaces with project-level notes
- Markdown export for portable project documentation
- REST API with OpenAPI documentation
- Local SQLite storage
- Single-container Docker deployment

## Quick start

### Docker Compose v2

```bash
docker compose up --build -d
```

### Docker Compose v1

```bash
docker-compose up --build -d
```

Open AttackAtlas at:

```text
http://127.0.0.1:7843
```

API documentation:

```text
http://127.0.0.1:7843/api/docs
```

AttackAtlas binds to localhost by default. To use another host-side port:

```bash
ATTACKATLAS_PORT=9127 docker compose up --build -d
```

For Compose v1, replace `docker compose` with `docker-compose`.

## Nmap import

Generate an XML scan, for example:

```bash
nmap -sC -sV -p- 10.10.10.0/24 -oX scan.xml
```

Then either:

- drag the XML file onto the project canvas to import discovered hosts, or
- drop a single-host XML file directly onto an existing host to merge the scan into that endpoint.

Repeated imports are merged and services are deduplicated.

## User import

Users can be added manually or imported by dropping a UTF-8 CSV file on **Users** in the sidebar.

```csv
username,domain,host,notes
administrator,CORP,DC01,Domain admin
svc_backup,CORP,10.10.10.20,Found in backup config
```

`host` may be a hostname or IP/address already present in the project. Leave it blank for an unassigned user.

## Data and security

Persistent application data is stored in:

```text
./data/attackatlas.db
```

AttackAtlas may contain sensitive engagement data. Credential secrets are currently stored in plaintext in the local SQLite database, and complete Markdown exports may contain plaintext credentials.

Keep the data directory and exported archives on trusted or encrypted storage. See [SECURITY.md](SECURITY.md) for details.

## Project documentation

- [CHANGELOG.md](CHANGELOG.md) — release history
- [CONTRIBUTING.md](CONTRIBUTING.md) — development and contribution guide
- [SECURITY.md](SECURITY.md) — security considerations and vulnerability reporting
- OpenAPI — available at `/api/docs` while AttackAtlas is running

## Technology

- **Backend:** Python, FastAPI, SQLite
- **Frontend:** React, TypeScript, Vite
- **Deployment:** Docker / Docker Compose

AttackAtlas is intentionally designed to remain lightweight and local-first, without external services for normal operation.

## License

AttackAtlas is licensed under the [MIT License](LICENSE).
