# AttackAtlas

Local-first pentest/CTF workspace for visualizing hosts, services, access relationships and attack paths.

## MVP features
- Project-based workspaces
- Lightweight FastAPI + SQLite backend
- React/Vite browser GUI
- Manual host creation with OS family and endpoint type
- Drag-and-drop host ordering on the board
- Nmap XML import by file picker or project-level drag-and-drop
- Drop Nmap XML directly on a host card to merge that scan into the selected endpoint
- Merge/deduplicate hosts and open services on repeated scans
- Expandable host cards with service details
- REST API and OpenAPI docs
- Localhost-only Docker binding by default
- Single runtime container

## Host model
Hosts can be added before any scan exists. OS family and endpoint type are separate fields, allowing combinations such as:

- Windows + Server
- Linux + Server
- Linux + Workstation
- macOS + Workstation
- Unknown + Network device

Board order is persisted in SQLite when cards are dragged.

## Start
```bash
docker compose up --build -d
```
Open: `http://127.0.0.1:7843`
API docs: `http://127.0.0.1:7843/api/docs`

Change host-side port:
```bash
ATTACKATLAS_PORT=9127 docker compose up --build -d
```

## Nmap import
Generate XML:
```bash
nmap -sC -sV -p- 10.10.10.0/24 -oX fullscan.xml
```

### Import an entire project scan
Drag `fullscan.xml` anywhere on the project board, use the Import button, or:
```bash
curl -F "file=@fullscan.xml" http://127.0.0.1:7843/api/v1/projects/1/imports/nmap
```

### Import into one existing host
Drop a single-host Nmap XML directly on the host card, or:
```bash
curl -F "file=@dc01.xml" http://127.0.0.1:7843/api/v1/projects/1/hosts/3/imports/nmap
```

For a targeted host import, AttackAtlas uses an address/hostname match when possible. A single-host scan may also be explicitly merged into the selected host.

## API additions in 0.2.0
```text
POST  /api/v1/projects/{project_id}/hosts
PATCH /api/v1/projects/{project_id}/hosts/{host_id}
POST  /api/v1/projects/{project_id}/hosts/reorder
POST  /api/v1/projects/{project_id}/hosts/{host_id}/imports/nmap
```

## Data
Persistent SQLite data is stored in `./data/attackatlas.db` through the Docker volume.

Existing 0.1 databases are upgraded with small additive SQLite migrations for host OS family, endpoint type and board ordering.

## 0.3.0 — Free canvas and attack paths
- Board is now a free-position canvas instead of a fixed card grid.
- Drag hosts anywhere on the canvas; X/Y positions persist in SQLite.
- Connect mode: select a source host, then a target host, and create a labeled path.
- Relationships can be directed arrows or undirected lines.
- Built-in relation types include access, valid credentials, SMB, WinRM, SSH, local admin, pivot, member-of and DCSync; labels are free text.
- Edges are persisted through the REST API and can be selected/deleted from the canvas.
- Nmap XML can still be dropped on the project or directly on a specific host.
- Newly discovered Nmap hosts receive spread-out initial canvas positions.

### Graph API
```text
GET    /api/v1/projects/{project_id}/edges
POST   /api/v1/projects/{project_id}/edges
DELETE /api/v1/projects/{project_id}/edges/{edge_id}
PATCH  /api/v1/projects/{project_id}/hosts/{host_id}   # includes pos_x / pos_y
```

## v0.5 canvas interactions

- Free host placement with persistent X/Y coordinates.
- Pan mode plus zoom in/out, reset and fit-to-hosts controls.
- Curved attack-path routing that attaches to the nearest side of each host card.
- Visible connection handles on selected/hovered hosts.
- Host inspector panel with details, services, notes, host-specific Nmap upload and connect action.
- Delete a host from its card/inspector, or drag the host onto the trash target in the lower-right corner.
- Host deletion also removes its services, shares and connected host edges.

## Attack paths and credentials

AttackAtlas 0.5 adds an editable attack-path canvas and project-local credential management. Drag from a host connection handle onto another host to create a path, or use the Connect tool/context menu. Double-click an edge (or select it and choose Edit edge) to change relation, label, and direction. Relation types receive distinct lightweight SVG styling.

Right-click a host for quick actions: add connection, edit notes, import an Nmap XML for that host, add/manage credentials, open details, or delete the host.

Credentials are modeled separately from accounts and can be linked to the host where they were discovered. Secrets are masked by default in the UI and can be revealed/copied. **MVP security note:** secrets are currently stored as plaintext in the local SQLite project database. Keep the data directory on trusted/encrypted storage; at-rest application encryption is a future hardening item.

## v0.6 host templates and editing

The **Add host** dialog includes ready-made templates for:

- Windows Server 2008, 2012, 2016, 2019, 2022 and 2025
- Windows XP, Windows 7, Windows 10 and Windows 11
- Kali Linux, Ubuntu Linux and Ubuntu Server
- Custom/blank hosts

A template only prefills OS family, device type, and OS/version; every field remains editable before creation.

Existing hosts can be edited at any time from the pencil icon on the card, the host right-click menu, or the right-side inspector. This includes hosts created by Nmap imports, so an imported IP-only host can later be given a hostname without changing its IP address, services, credentials, or attack-path relationships.

The left project/navigation panel and right host inspector use larger text and a slightly wider layout for improved readability.

### 0.6.1 UI fix
- Long hostnames on host cards now wrap instead of being truncated with an ellipsis.
- Host cards grow vertically when needed so the complete hostname remains visible.
- The full hostname is also available as a hover tooltip.


## v0.7 credential UX

- The left Assets panel now has an expandable Credentials section showing stored credentials inline.
- Sidebar credentials remain masked and open directly in edit mode when selected.
- The Credential manager uses larger rows, larger account/secret text and clearer actions.
- Stored credentials can now be edited in place: account, type, secret, source host, source and notes can all be changed.
- Credential PATCH requests validate that referenced accounts and hosts belong to the active project.
## v0.7.1 host credential inspector

- The selected-host **Credentials** tab now shows the actual credentials linked to that host.
- Secrets stay masked by default and can be revealed or hidden per credential.
- Credentials can be copied directly from the host inspector with a dedicated **Copy** action.
- Each credential can also be opened in edit mode directly from the host inspector.
- Long secrets/hashes wrap inside the inspector instead of overflowing the panel.


### Service scan details (v0.7.2)
Services in the selected-host inspector are expandable. New Nmap XML imports retain per-port NSE script output and the raw `<port>` XML fragment so the exact scan context can be reviewed without leaving AttackAtlas. Existing services imported by an older AttackAtlas version can be populated by re-importing the original Nmap XML; service deduplication still applies.

## v0.8 project management and Markdown export

- Project names can be changed after creation from **Project settings**.
- Each project has a dedicated multi-line **Project notes** field for scope, objectives, reminders, VPN details, findings, or other engagement context.
- Projects can be deleted from Project settings. Deletion removes that project's hosts, services, accounts, credentials, shares, scans, and attack-path edges.
- **Export Markdown** downloads a ZIP containing:
  - `README.md` with project notes and summary
  - one Markdown file per host under `hosts/`, including services and stored Nmap/NSE output
  - `accounts.md`
  - `credentials.md`
  - `attack-paths.md`
  - `scans.md`
- The export is intentionally portable and works well with Git, Obsidian, VS Code, and ordinary Markdown readers.

**Sensitive export warning:** Markdown export is a complete project export, so `credentials.md` contains credential secrets in plaintext. Treat exported archives as sensitive material.

### Project API

```text
PATCH  /api/v1/projects/{project_id}
DELETE /api/v1/projects/{project_id}
GET    /api/v1/projects/{project_id}/export/markdown
```


### 0.8.1
- Improved contrast for Project, Markdown export, Save project, Export Markdown, and Delete project buttons in dark mode.

## GitHub repository setup

AttackAtlas includes repository metadata for GitHub, including issue templates, a pull request template, an MIT license, contribution/security notes, and a small CI workflow.

### First push

Create an empty repository on GitHub, then from the AttackAtlas directory run:

```bash
git init
git add .
git commit -m "Initial AttackAtlas release"
git branch -M main
git remote add origin git@github.com:YOUR_USERNAME/AttackAtlas.git
git push -u origin main
```

If you use HTTPS instead of SSH, use the HTTPS repository URL for `origin`.

### Continuous integration

`.github/workflows/ci.yml` runs automatically on pushes to `main` and pull requests. It validates the Python backend, builds the React frontend, and performs a Docker image build. This does not deploy AttackAtlas anywhere; it only checks that the repository still builds successfully.
