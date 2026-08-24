# Changelog

All notable changes to AttackAtlas are documented in this file.

The project is currently in alpha development. Version numbers below describe development milestones and do not yet imply API stability.

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
- MIT license, contribution guide and security policy.

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
