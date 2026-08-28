# Changelog

All notable public releases of AttackAtlas are documented here.

## [0.1.0-alpha] - 2026-08-27

Initial public alpha release.

### Included

- Project-based local workspaces
- Free-form host canvas with domain grouping
- Editable attack paths and connections
- Multiple parallel edges between the same pair of hosts, with separate visual routing
- Host templates and host/domain editing
- Nmap XML import with service and NSE details
- User CSV import and user management
- Credential management
- Project notes and Markdown export
- SVG visualization snapshots
- REST API and OpenAPI documentation
- Docker deployment with localhost-only binding by default

### Security

- Credential secrets are encrypted at rest in SQLite using AES-256-GCM.
- A random local vault key is created in `./secrets/credential-vault.json` and kept separate from the database.
- Legacy plaintext credential rows are migrated automatically on startup.
- Startup fails safely if encrypted credentials exist but the vault key is missing.
- The key envelope is versioned for a future master-password/key-wrapping layer.

### Security note

The SQLite database stores credential secrets encrypted at rest. The separate local vault key and exported project archives remain sensitive.

<details>
<summary>Pre-public development history</summary>

The versions below were internal development milestones before the initial public alpha release.

## [0.14.0] - 2026-08-26

### Added
- SVG snapshot export for the current visualization.
- Snapshot includes host cards, domain hulls, attack-path edges, labels and project name.
- Export automatically crops to the host layout with padding and preserves vector quality.

### Changed
- UI panels and controls are intentionally excluded from snapshots so exports are report-friendly.

## [0.13.3] - 2026-08-25

### Changed
- Moved Projects out of the Hosts section into its own top-level sidebar view.
- Added dedicated Projects, Hosts and Users navigation tabs.
- The Hosts view now clearly shows the active project and provides a shortcut back to project selection.
- The Projects view includes a prominent New project action and active-project indicator.

## [0.13.2] - 2026-08-25

### Fixed
- Hardened the Add Host submit flow so failures are no longer silent.
- Add Host now reports missing project, missing address, duplicate address and API errors directly inside the dialog.
- Added an explicit submit button and loading state to prevent accidental duplicate submissions.

## [0.13.1] - 2026-08-25

### Changed
- Reserved red exclusively for the `UNASSIGNED` group in both the canvas and Users sidebar.
- Normal domain groups now rotate through a five-color palette that excludes red.

## [0.13.0] - 2026-08-25

### Added
- Shape-following domain hulls using smoothed convex contours around host cards.
- Dedicated Hosts and Users sidebar views.
- User search and quick CSV import in the Users view.
- Domain → host → user hierarchy with independent expand/collapse controls.
- Direct copy and edit controls for each user.
- Quick Add user and Add credential actions in the main header.

### Changed
- Domain regions now follow pyramid and irregular host layouts instead of rectangular bounding boxes.
- Unassigned hosts and users receive a subdued purple visual group.
- Users sidebar styling now mirrors domain grouping on the canvas.

## [0.12.0] - 2026-08-25

### Added
- Dynamic domain regions on the canvas for domains containing two or more hosts.
- Subtle tinted backgrounds, dashed boundaries and domain labels with host counts.
- Domain visibility toggle in the canvas toolbar.

### Changed
- Domain regions automatically resize and move as member hosts are repositioned.
- Hosts without a domain remain ungrouped, keeping the canvas uncluttered.

## [0.11.1] - 2026-08-25

### Added
- Added **Add user** to each host card hamburger menu, preselecting that host as the discovery source.
- User groups in the left sidebar can now be expanded or collapsed per host.
- Clicking a user in the sidebar copies the username; a separate edit button opens the user editor.

### Changed
- Improved visual separation of host-based user groups with clearer borders and OS-family accents.
- Connection mode can now be cancelled from the toolbar, with an inline Cancel action or by pressing Escape.
- Completing a connection returns the canvas to Select mode instead of leaving Connect mode active.

### Fixed
- Fixed Add connection from the host hamburger menu leaving the canvas stuck in connection mode.

## [0.11.0] - 2026-08-25

### Added
- Added **Attacker Machine** as a host status.
- Added a separate host domain field and FQDN display (`HOST.DOMAIN`) on host cards.
- Added click-to-copy behavior for visible host card values and host identity details.
- Credentials can create and associate a previously unknown username/domain directly from the Add Credential flow.

### Changed
- Simplified host card actions into a single hamburger menu to give the hostname more horizontal space.
- Hostnames/FQDNs stay on one line on host cards.
- Separated user management and credential management into distinct dialogs/workflows.

## [0.10.1] - 2026-08-24

### Added
- Existing users/accounts can now be edited after creation or CSV import.
- Username, domain, source host and notes can be corrected without recreating the user.
- Users in the left sidebar open directly in edit mode.

## [0.10.0] - 2026-08-24

### Added
- Added `cookie` as a credential type.
- Added a Users section in the left sidebar, grouped by the host where each account was found.
- Added host association for manually created users/accounts.
- Added drag-and-drop CSV user import using `username,domain,host,notes`.

### Changed
- Increased typography and width in the left navigation panel for improved readability.
- Markdown account exports now include the host where an account was found.

## [0.9.1] - 2026-08-23

### Changed
- Added sanitized Add Host and Credential Manager screenshots to the documentation.
- Re-encoded repository screenshots to remove embedded image metadata.

## [0.9.0]

### Added
- GitHub repository metadata, issue templates and pull request template.
- GitHub Actions CI for backend validation, frontend build and Docker image build.
- GPLv3 license, contribution guide and security policy.

### Changed
- Repository documentation prepared for public source control.

## [0.8.1]

### Fixed
- Improved contrast for project action buttons in dark mode.

## [0.8.0]

### Added
- Project name editing and project-level notes.
- Project deletion with cleanup of associated project data.
- Complete Markdown export as a ZIP archive.
- Separate Markdown output for hosts, accounts, credentials, attack paths and scan history.

### Security
- Markdown exports explicitly warn that complete exports may contain plaintext credential secrets.

## [0.7.2]

### Added
- Expandable service details in the host inspector.
- Per-port Nmap NSE script output.
- Retention and display of raw Nmap `<port>` XML for newly imported scans.

## [0.7.1]

### Added
- Host inspector credential view.
- Show/hide, copy and edit actions for credentials associated with the selected host.

### Fixed
- Long secrets and hashes wrap correctly inside the host inspector.

## [0.7.0]

### Added
- Expandable credential section in the left navigation panel.
- Larger credential manager entries and clearer actions.
- Editing of existing credentials, including account, type, secret, source host, source and notes.
- Project ownership validation for referenced accounts and hosts in credential updates.

## [0.6.1]

### Fixed
- Long hostnames wrap on host cards instead of being truncated.
- Host cards can grow vertically to display complete hostnames.
- Full hostname is available as a hover tooltip.

## [0.6.0]

### Added
- Host templates for Windows Server 2008/2012/2016/2019/2022/2025.
- Host templates for Windows XP, Windows 7, Windows 10 and Windows 11.
- Host templates for Kali Linux, Ubuntu and Ubuntu Server.
- Editing of existing hosts, including hosts created from Nmap imports.

### Changed
- Hostname and IP address are editable independently.
- Left navigation and right inspector typography/layout improved for readability.

## [0.5.0]

### Added
- Editable attack-path canvas with direct connection dragging from host handles.
- Edge editor for relation type, label and direction.
- Distinct lightweight visual styling for common relationship types.
- Project-local account and credential management.
- Credential association with the host on which a credential was discovered.
- Host context menu with connection, notes, Nmap, credential, details and delete actions.

### Security
- Credential secrets are masked by default in the UI.
- Application-level encryption at rest is not yet implemented; secrets remain plaintext in SQLite.

## [0.4.0]

### Added
- Canvas pan, zoom, reset and fit controls.
- Curved attack-path routing with side-aware host attachment points.
- Host inspector panel with details, services, notes and actions.
- Host deletion from cards and inspector.
- Drag-to-trash host deletion.

### Changed
- Deleting a host also removes its services, shares and connected host edges.

## [0.3.0]

### Added
- Free-position canvas with persistent X/Y host coordinates.
- Directed and undirected attack-path relationships.
- Built-in relationship types including access, valid credentials, SMB, WinRM, SSH, local admin, pivot, member-of and DCSync.
- Edge creation, selection and deletion through the REST API.
- Automatic initial placement for hosts discovered through Nmap imports.

## [0.2.0]

### Added
- Manual host creation with separate OS family and endpoint type.
- Persistent host ordering.
- Host-specific Nmap XML import endpoint.
- Nmap XML drag-and-drop directly onto an existing host.

### Changed
- Repeated scans merge into existing hosts and services instead of creating duplicates.

## [0.1.0]

### Added
- Initial AttackAtlas prototype.
- Project-based workspaces.
- FastAPI and SQLite backend.
- React/Vite browser interface.
- Nmap XML project import.
- Host and service inventory.
- REST API and OpenAPI documentation.
- Localhost-only Docker binding by default.

</details>
