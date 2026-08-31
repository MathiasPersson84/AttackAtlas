from pathlib import Path
import io
import re
import zipfile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from .models import Project, Host, Service, Account, Credential, Share, Edge, Scan, NoteEntry, Attachment, ReportBlock
from .vault import decrypt_secret
from .db import DATA_DIR


def _safe_name(value: str) -> str:
    value = re.sub(r'[^A-Za-z0-9._-]+', '-', (value or '').strip()).strip('-')
    return value or 'project'


def _md(value) -> str:
    if value is None:
        return ''
    return str(value).replace('\r\n', '\n').replace('\r', '\n')


def build_markdown_export(project: Project, db: Session):
    project_id = project.id
    hosts = db.query(Host).filter_by(project_id=project_id).order_by(Host.sort_order, Host.id).all()
    accounts = db.query(Account).filter_by(project_id=project_id).order_by(Account.id).all()
    credentials = db.query(Credential).filter_by(project_id=project_id).order_by(Credential.id).all()
    shares = db.query(Share).filter_by(project_id=project_id).order_by(Share.host_id, Share.name).all()
    edges = db.query(Edge).filter_by(project_id=project_id).order_by(Edge.id).all()
    scans = db.query(Scan).filter_by(project_id=project_id).order_by(Scan.imported_at).all()
    notes = db.query(NoteEntry).filter_by(project_id=project_id).order_by(NoteEntry.created_at, NoteEntry.id).all()
    report_blocks = db.query(ReportBlock).filter_by(project_id=project_id).order_by(ReportBlock.sort_order, ReportBlock.id).all()
    account_by_id = {a.id: a for a in accounts}
    host_by_id = {h.id: h for h in hosts}

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        overview = [f'# {_md(project.name)}', '', '> Exported from AttackAtlas. This archive may contain plaintext credentials.', '']
        if project.description:
            overview += ['## Description', '', _md(project.description), '']
        if project.notes:
            overview += ['## Notes', '', _md(project.notes), '']
        overview += [
            '## Summary', '',
            f'- Hosts: {len(hosts)}',
            f'- Accounts: {len(accounts)}',
            f'- Credentials: {len(credentials)}',
            f'- Shares: {len(shares)}',
            f'- Attack paths: {len(edges)}',
            f'- Imported scans: {len(scans)}', ''
        ]
        # Living report: manual project blocks plus linked host notes. Secrets are not included here.
        report = [f'# {_md(project.name)} — Report', '', '> Generated from the live AttackAtlas report. Credential secrets are redacted from this report.', '']
        for b in report_blocks:
            report += [f'## {_md(b.title) or "Report Notes"}', '', _md(b.content_markdown), '']
        if notes:
            report += ['## Host Activity', '']
        for h in hosts:
            hn=[n for n in notes if n.host_id==h.id]
            if not hn: continue
            report += [f'### {_md(h.hostname or h.address)}', '', f'`{_md(h.address)}`', '']
            for n in hn:
                report += [f'#### {_md(n.title) or _md(n.category)}', '', f'**Category:** {_md(n.category)}  ', f'**Recorded:** {n.created_at.isoformat()}  ']
                if n.tags: report += [f'**Tags:** {_md(n.tags)}  ']
                report += ['', _md(n.content_markdown), '']
                for a in db.query(Attachment).filter_by(note_id=n.id).order_by(Attachment.id).all():
                    src=DATA_DIR/'projects'/str(project_id)/'attachments'/a.stored_filename
                    ext=Path(a.filename).suffix or Path(a.stored_filename).suffix or '.png'
                    asset=f'assets/{a.id:04d}-{_safe_name(Path(a.filename).stem)}{ext}'
                    if src.exists(): zf.write(src, asset)
                    report += [f'![{_md(a.caption or a.filename)}]({asset})', '']
                    if a.caption: report += [f'*{_md(a.caption)}*', '']
        zf.writestr('report.md', '\n'.join(report))

        zf.writestr('README.md', '\n'.join(overview))

        for h in hosts:
            title = h.hostname or h.address
            lines = [
                f'# {_md(title)}', '',
                f'- **Address:** `{_md(h.address)}`',
                f'- **Hostname:** {_md(h.hostname) or "—"}',
                f'- **Domain:** {_md(h.domain) or "—"}',
                f'- **OS:** {_md(h.os) or "—"}',
                f'- **OS family:** {_md(h.os_family) or "unknown"}',
                f'- **Device type:** {_md(h.device_type) or "host"}',
                f'- **Status:** {_md(h.status) or "discovered"}',
                f'- **Canvas position:** {h.pos_x}, {h.pos_y}', ''
            ]
            if h.notes:
                lines += ['## Notes', '', _md(h.notes), '']
            lines += ['## Services', '']
            services = sorted(h.services, key=lambda x: (x.port, x.protocol))
            if not services:
                lines += ['_No services stored._', '']
            for svc in services:
                lines += [
                    f'### {svc.port}/{_md(svc.protocol)} — {_md(svc.name) or "unknown"}', '',
                    f'- **State:** {_md(svc.state)}',
                    f'- **Product:** {_md(svc.product) or "—"}',
                    f'- **Version:** {_md(svc.version) or "—"}',
                    f'- **Extra info:** {_md(svc.extra_info) or "—"}', ''
                ]
                if svc.script_output:
                    lines += ['#### Nmap script output', '', '```text', _md(svc.script_output), '```', '']
                if svc.raw_output:
                    lines += ['<details>', '<summary>Raw Nmap XML for this port</summary>', '', '```xml', _md(svc.raw_output), '```', '</details>', '']
            host_shares = [x for x in shares if x.host_id == h.id]
            if host_shares:
                lines += ['## Shares', '']
                for sh in host_shares:
                    suffix = f' — {_md(sh.notes)}' if sh.notes else ''
                    lines.append(f'- **{_md(sh.name)}** — `{_md(sh.path)}`{suffix}')
                lines.append('')
            zf.writestr(f'hosts/{h.id:04d}-{_safe_name(title)}.md', '\n'.join(lines))

        account_lines = ['# Accounts', '']
        if not accounts:
            account_lines += ['_No accounts stored._', '']
        for a in accounts:
            identity = ((a.domain + '\\') if a.domain else '') + a.username
            account_lines += [f'## {_md(identity)}', '']
            ah = host_by_id.get(a.host_id) if getattr(a, 'host_id', None) else None
            account_lines += [f'- **Found on:** {_md((ah.hostname or ah.address) if ah else "Unassigned")}', '']
            if a.notes:
                account_lines += [_md(a.notes), '']
        zf.writestr('accounts.md', '\n'.join(account_lines))

        cred_lines = ['# Credentials', '', '> **Sensitive:** secrets are exported in plaintext because this export contains all project data.', '']
        if not credentials:
            cred_lines += ['_No credentials stored._', '']
        for c in credentials:
            a = account_by_id.get(c.account_id) if c.account_id else None
            h = host_by_id.get(c.host_id) if c.host_id else None
            identity = ((a.domain + '\\') if a and a.domain else '') + (a.username if a else 'Unassigned')
            escaped_secret = _md(decrypt_secret(c.secret)).replace('`', '\\`')
            cred_lines += [
                f'## {_md(identity)}', '',
                f'- **Type:** {_md(c.kind)}',
                f'- **Secret:** `{escaped_secret}`',
                f'- **Source:** {_md(c.source) or "manual"}',
                f'- **Found on:** {_md((h.hostname or h.address) if h else "Unknown")}', ''
            ]
            if c.notes:
                cred_lines += ['### Notes', '', _md(c.notes), '']
        zf.writestr('credentials.md', '\n'.join(cred_lines))

        edge_lines = ['# Attack paths', '']
        if not edges:
            edge_lines += ['_No attack paths stored._', '']
        for e in edges:
            src = host_by_id.get(e.source_id) if e.source_type == 'host' else None
            dst = host_by_id.get(e.target_id) if e.target_type == 'host' else None
            src_name = (src.hostname or src.address) if src else f'{e.source_type}:{e.source_id}'
            dst_name = (dst.hostname or dst.address) if dst else f'{e.target_type}:{e.target_id}'
            arrow = '→' if e.directed else '—'
            label = e.label or e.relation
            extra = f' — {_md(label)}' if label != e.relation else ''
            edge_lines.append(f'- **{_md(src_name)}** {arrow} **{_md(dst_name)}** — `{_md(e.relation)}`{extra}')
        edge_lines.append('')
        zf.writestr('attack-paths.md', '\n'.join(edge_lines))

        scan_lines = ['# Scan history', '']
        if not scans:
            scan_lines += ['_No scans imported._', '']
        for sc in scans:
            scan_lines.append(f'- `{_md(sc.filename)}` — {sc.imported_at.isoformat()} — {sc.hosts_seen} hosts / {sc.services_seen} services')
        scan_lines.append('')
        zf.writestr('scans.md', '\n'.join(scan_lines))

    buf.seek(0)
    filename = f'attackatlas-{_safe_name(project.name)}-markdown.zip'
    return StreamingResponse(buf, media_type='application/zip', headers={'Content-Disposition': f'attachment; filename="{filename}"'})
