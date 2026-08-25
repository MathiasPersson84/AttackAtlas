import os
import csv
import io
from pathlib import Path
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .db import Base, engine, get_db, apply_lightweight_migrations
from .models import Project, Host, Service, Account, Credential, Share, Edge, Scan
from .schemas import ProjectCreate, ProjectUpdate, HostCreate, HostUpdate, HostReorder, AccountCreate, AccountUpdate, CredentialCreate, CredentialUpdate, ShareCreate, EdgeCreate, EdgeUpdate
from .nmap_import import import_nmap_xml
from .markdown_export import build_markdown_export

Base.metadata.create_all(bind=engine)
apply_lightweight_migrations()
app = FastAPI(title='AttackAtlas API', version='0.11.1', docs_url='/api/docs', openapi_url='/api/openapi.json')


def host_json(h: Host):
    return {
        'id': h.id,
        'address': h.address,
        'hostname': h.hostname,
        'domain': h.domain or '',
        'os': h.os,
        'os_family': h.os_family or 'unknown',
        'device_type': h.device_type or 'host',
        'status': h.status,
        'notes': h.notes,
        'sort_order': h.sort_order or 0,
        'pos_x': h.pos_x if h.pos_x is not None else 80,
        'pos_y': h.pos_y if h.pos_y is not None else 80,
        'services': [
            {'id': s.id, 'protocol': s.protocol, 'port': s.port, 'state': s.state, 'name': s.name, 'product': s.product, 'version': s.version, 'extra_info': s.extra_info, 'script_output': s.script_output or '', 'raw_output': s.raw_output or ''}
            for s in sorted(h.services, key=lambda x: (x.port, x.protocol))
        ],
    }


def edge_json(e: Edge):
    return {
        'id': e.id,
        'source_type': e.source_type,
        'source_id': e.source_id,
        'target_type': e.target_type,
        'target_id': e.target_id,
        'relation': e.relation,
        'label': e.label,
        'directed': bool(e.directed),
    }


@app.get('/api/health')
def health():
    return {'status': 'ok', 'name': 'AttackAtlas'}


@app.get('/api/v1/projects')
def projects(db: Session = Depends(get_db)):
    return [{'id': p.id, 'name': p.name, 'description': p.description or '', 'notes': p.notes or '', 'created_at': p.created_at} for p in db.query(Project).order_by(Project.id.desc())]


@app.post('/api/v1/projects')
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    if db.query(Project).filter_by(name=payload.name).first():
        raise HTTPException(409, 'Project name already exists')
    p = Project(**payload.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return {'id': p.id, 'name': p.name, 'description': p.description or '', 'notes': p.notes or ''}


@app.patch('/api/v1/projects/{project_id}')
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter_by(id=project_id).one_or_none()
    if project is None:
        raise HTTPException(404, 'Project not found')
    data = payload.model_dump(exclude_none=True)
    if 'name' in data:
        data['name'] = data['name'].strip()
        if not data['name']:
            raise HTTPException(400, 'Project name cannot be empty')
        duplicate = db.query(Project).filter(Project.name == data['name'], Project.id != project_id).first()
        if duplicate:
            raise HTTPException(409, 'Project name already exists')
    for key, value in data.items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return {'id': project.id, 'name': project.name, 'description': project.description or '', 'notes': project.notes or ''}


@app.delete('/api/v1/projects/{project_id}')
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter_by(id=project_id).one_or_none()
    if project is None:
        raise HTTPException(404, 'Project not found')
    host_ids = [row[0] for row in db.query(Host.id).filter_by(project_id=project_id).all()]
    if host_ids:
        db.query(Service).filter(Service.host_id.in_(host_ids)).delete(synchronize_session=False)
    db.query(Edge).filter_by(project_id=project_id).delete(synchronize_session=False)
    db.query(Credential).filter_by(project_id=project_id).delete(synchronize_session=False)
    db.query(Share).filter_by(project_id=project_id).delete(synchronize_session=False)
    db.query(Account).filter_by(project_id=project_id).delete(synchronize_session=False)
    db.query(Scan).filter_by(project_id=project_id).delete(synchronize_session=False)
    db.query(Host).filter_by(project_id=project_id).delete(synchronize_session=False)
    db.delete(project)
    db.commit()
    return {'ok': True}


@app.get('/api/v1/projects/{project_id}/export/markdown')
def export_project_markdown(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter_by(id=project_id).one_or_none()
    if project is None:
        raise HTTPException(404, 'Project not found')
    return build_markdown_export(project, db)


@app.get('/api/v1/projects/{project_id}/hosts')
def hosts(project_id: int, db: Session = Depends(get_db)):
    rows = db.query(Host).filter_by(project_id=project_id).order_by(Host.sort_order, Host.id).all()
    return [host_json(h) for h in rows]


@app.post('/api/v1/projects/{project_id}/hosts')
def create_host(project_id: int, payload: HostCreate, db: Session = Depends(get_db)):
    if not db.query(Project).filter_by(id=project_id).first():
        raise HTTPException(404, 'Project not found')
    order = db.query(Host).filter_by(project_id=project_id).count()
    h = Host(project_id=project_id, sort_order=order, **payload.model_dump())
    db.add(h)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'A host with this address already exists in the project')
    db.refresh(h)
    return host_json(h)


@app.patch('/api/v1/projects/{project_id}/hosts/{host_id}')
def update_host(project_id: int, host_id: int, payload: HostUpdate, db: Session = Depends(get_db)):
    h = db.query(Host).filter_by(id=host_id, project_id=project_id).one_or_none()
    if h is None:
        raise HTTPException(404, 'Host not found')
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(h, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'A host with this address already exists in the project')
    db.refresh(h)
    return host_json(h)


@app.delete('/api/v1/projects/{project_id}/hosts/{host_id}')
def delete_host(project_id: int, host_id: int, db: Session = Depends(get_db)):
    h = db.query(Host).filter_by(id=host_id, project_id=project_id).one_or_none()
    if h is None:
        raise HTTPException(404, 'Host not found')
    # Edge uses polymorphic IDs rather than foreign keys, so remove host-related
    # attack paths explicitly. Shares are removed explicitly as well so cleanup
    # is reliable even if SQLite foreign_keys was disabled in an older DB.
    db.query(Edge).filter(
        Edge.project_id == project_id,
        ((Edge.source_type == 'host') & (Edge.source_id == host_id)) |
        ((Edge.target_type == 'host') & (Edge.target_id == host_id))
    ).delete(synchronize_session=False)
    db.query(Credential).filter_by(project_id=project_id, host_id=host_id).update({'host_id': None}, synchronize_session=False)
    db.query(Account).filter_by(project_id=project_id, host_id=host_id).update({'host_id': None}, synchronize_session=False)
    db.query(Share).filter_by(project_id=project_id, host_id=host_id).delete(synchronize_session=False)
    db.query(Service).filter_by(host_id=host_id).delete(synchronize_session=False)
    db.delete(h)
    db.commit()
    return {'ok': True}


@app.post('/api/v1/projects/{project_id}/hosts/reorder')
def reorder_hosts(project_id: int, payload: HostReorder, db: Session = Depends(get_db)):
    rows = db.query(Host).filter_by(project_id=project_id).all()
    by_id = {h.id: h for h in rows}
    if set(payload.host_ids) != set(by_id):
        raise HTTPException(400, 'host_ids must contain every host in the project exactly once')
    for idx, host_id in enumerate(payload.host_ids):
        by_id[host_id].sort_order = idx
    db.commit()
    return {'ok': True}


@app.post('/api/v1/projects/{project_id}/hosts/{host_id}/imports/nmap')
async def import_nmap_for_host(project_id: int, host_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    raw = await file.read()
    if len(raw) > 100 * 1024 * 1024:
        raise HTTPException(413, 'Scan file too large')
    try:
        return import_nmap_xml(db, project_id, file.filename or 'scan.xml', raw, target_host_id=host_id)
    except Exception as e:
        db.rollback()
        raise HTTPException(400, f'Could not import Nmap XML for host: {e}')


@app.get('/api/v1/projects/{project_id}/accounts')
def accounts(project_id: int, db: Session = Depends(get_db)):
    return [{'id': x.id, 'username': x.username, 'domain': x.domain, 'notes': x.notes, 'host_id': x.host_id} for x in db.query(Account).filter_by(project_id=project_id).order_by(Account.host_id, Account.domain, Account.username).all()]


@app.post('/api/v1/projects/{project_id}/accounts')
def create_account(project_id: int, payload: AccountCreate, db: Session = Depends(get_db)):
    if payload.host_id is not None and not db.query(Host).filter_by(id=payload.host_id, project_id=project_id).first():
        raise HTTPException(400, 'Host does not belong to this project')
    x = Account(project_id=project_id, **payload.model_dump())
    db.add(x)
    db.commit()
    db.refresh(x)
    return {'id': x.id}


@app.patch('/api/v1/projects/{project_id}/accounts/{account_id}')
def update_account(project_id: int, account_id: int, payload: AccountUpdate, db: Session = Depends(get_db)):
    x = db.query(Account).filter_by(id=account_id, project_id=project_id).one_or_none()
    if x is None:
        raise HTTPException(404, 'Account not found')
    changes = payload.model_dump(exclude_unset=True)
    if 'host_id' in changes and changes['host_id'] is not None and not db.query(Host).filter_by(id=changes['host_id'], project_id=project_id).first():
        raise HTTPException(400, 'Host does not belong to this project')
    for key, value in changes.items():
        setattr(x, key, value)
    db.commit(); db.refresh(x)
    return {'id': x.id, 'username': x.username, 'domain': x.domain, 'notes': x.notes, 'host_id': x.host_id}


@app.post('/api/v1/projects/{project_id}/accounts/import/csv')
async def import_accounts_csv(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    raw = await file.read()
    if len(raw) > 5 * 1024 * 1024:
        raise HTTPException(413, 'CSV file too large')
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        raise HTTPException(400, 'CSV must be UTF-8 encoded')
    try:
        reader = csv.DictReader(io.StringIO(text))
        required = {'username'}
        fields = {str(x).strip().lower() for x in (reader.fieldnames or [])}
        if not required.issubset(fields):
            raise HTTPException(400, 'CSV must contain a username column. Supported columns: username,domain,host,notes')
        hosts = db.query(Host).filter_by(project_id=project_id).all()
        host_lookup = {}
        for h in hosts:
            if h.address: host_lookup[h.address.strip().lower()] = h
            if h.hostname:
                host_lookup[h.hostname.strip().lower()] = h
                if h.domain:
                    host_lookup[f'{h.hostname.strip()}.{h.domain.strip()}'.lower()] = h
        created = updated = skipped = 0
        errors = []
        for line_no, raw_row in enumerate(reader, start=2):
            row = {(k or '').strip().lower(): (v or '').strip() for k, v in raw_row.items()}
            username = row.get('username', '')
            if not username:
                skipped += 1
                continue
            domain = row.get('domain', '')
            host_value = row.get('host', '')
            notes = row.get('notes', '')
            host_id = None
            if host_value:
                host = host_lookup.get(host_value.lower())
                if not host:
                    errors.append(f'Line {line_no}: host "{host_value}" was not found')
                    continue
                host_id = host.id
            existing = db.query(Account).filter_by(project_id=project_id, username=username, domain=domain, host_id=host_id).first()
            if existing:
                if notes and notes != (existing.notes or ''):
                    existing.notes = notes
                    updated += 1
                else:
                    skipped += 1
                continue
            db.add(Account(project_id=project_id, username=username, domain=domain, host_id=host_id, notes=notes))
            created += 1
        db.commit()
        return {'created': created, 'updated': updated, 'skipped': skipped, 'errors': errors[:50], 'error_count': len(errors)}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(400, f'Could not import users CSV: {e}')


@app.delete('/api/v1/projects/{project_id}/accounts/{account_id}')
def delete_account(project_id: int, account_id: int, db: Session = Depends(get_db)):
    x = db.query(Account).filter_by(id=account_id, project_id=project_id).one_or_none()
    if x is None:
        raise HTTPException(404, 'Account not found')
    db.query(Credential).filter_by(project_id=project_id, account_id=account_id).update({'account_id': None}, synchronize_session=False)
    db.delete(x); db.commit()
    return {'ok': True}


def credential_json(x: Credential):
    return {'id': x.id, 'account_id': x.account_id, 'kind': x.kind, 'secret': x.secret, 'source': x.source, 'host_id': x.host_id, 'notes': x.notes or ''}


@app.get('/api/v1/projects/{project_id}/credentials')
def credentials(project_id: int, db: Session = Depends(get_db)):
    return [credential_json(x) for x in db.query(Credential).filter_by(project_id=project_id).order_by(Credential.id.desc()).all()]


@app.post('/api/v1/projects/{project_id}/credentials')
def create_credential(project_id: int, payload: CredentialCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    username = (data.pop('username', '') or '').strip()
    domain = (data.pop('domain', '') or '').strip()
    account_id = data.get('account_id')
    if account_id is not None and not db.query(Account).filter_by(id=account_id, project_id=project_id).first():
        raise HTTPException(400, 'Account does not belong to this project')
    if data.get('host_id') is not None and not db.query(Host).filter_by(id=data['host_id'], project_id=project_id).first():
        raise HTTPException(400, 'Host does not belong to this project')
    if account_id is None and username:
        account = db.query(Account).filter_by(project_id=project_id, username=username, domain=domain, host_id=data.get('host_id')).first()
        if account is None:
            account = Account(project_id=project_id, username=username, domain=domain, host_id=data.get('host_id'), notes='Created with credential')
            db.add(account)
            db.flush()
        data['account_id'] = account.id
    x = Credential(project_id=project_id, **data)
    db.add(x)
    db.commit()
    db.refresh(x)
    return credential_json(x)


@app.patch('/api/v1/projects/{project_id}/credentials/{credential_id}')
def update_credential(project_id: int, credential_id: int, payload: CredentialUpdate, db: Session = Depends(get_db)):
    x = db.query(Credential).filter_by(id=credential_id, project_id=project_id).one_or_none()
    if x is None:
        raise HTTPException(404, 'Credential not found')
    changes = payload.model_dump(exclude_unset=True)
    username = (changes.pop('username', None) or '').strip() if 'username' in changes else ''
    domain = (changes.pop('domain', None) or '').strip() if 'domain' in changes else ''
    if 'account_id' in changes and changes['account_id'] is not None and not db.query(Account).filter_by(id=changes['account_id'], project_id=project_id).first():
        raise HTTPException(400, 'Account does not belong to this project')
    if 'host_id' in changes and changes['host_id'] is not None and not db.query(Host).filter_by(id=changes['host_id'], project_id=project_id).first():
        raise HTTPException(400, 'Host does not belong to this project')
    if changes.get('account_id') is None and username:
        host_id = changes.get('host_id', x.host_id)
        account = db.query(Account).filter_by(project_id=project_id, username=username, domain=domain, host_id=host_id).first()
        if account is None:
            account = Account(project_id=project_id, username=username, domain=domain, host_id=host_id, notes='Created with credential')
            db.add(account)
            db.flush()
        changes['account_id'] = account.id
    for key, value in changes.items():
        setattr(x, key, value)
    db.commit(); db.refresh(x)
    return credential_json(x)


@app.delete('/api/v1/projects/{project_id}/credentials/{credential_id}')
def delete_credential(project_id: int, credential_id: int, db: Session = Depends(get_db)):
    x = db.query(Credential).filter_by(id=credential_id, project_id=project_id).one_or_none()
    if x is None:
        raise HTTPException(404, 'Credential not found')
    db.delete(x); db.commit()
    return {'ok': True}


@app.get('/api/v1/projects/{project_id}/shares')
def shares(project_id: int, db: Session = Depends(get_db)):
    return [{'id': x.id, 'host_id': x.host_id, 'name': x.name, 'path': x.path, 'notes': x.notes} for x in db.query(Share).filter_by(project_id=project_id).all()]


@app.post('/api/v1/projects/{project_id}/shares')
def create_share(project_id: int, payload: ShareCreate, db: Session = Depends(get_db)):
    x = Share(project_id=project_id, **payload.model_dump())
    db.add(x)
    db.commit()
    db.refresh(x)
    return {'id': x.id}


@app.get('/api/v1/projects/{project_id}/edges')
def edges(project_id: int, db: Session = Depends(get_db)):
    return [edge_json(x) for x in db.query(Edge).filter_by(project_id=project_id).order_by(Edge.id).all()]


@app.post('/api/v1/projects/{project_id}/edges')
def create_edge(project_id: int, payload: EdgeCreate, db: Session = Depends(get_db)):
    x = Edge(project_id=project_id, **payload.model_dump())
    db.add(x)
    db.commit()
    db.refresh(x)
    return edge_json(x)


@app.patch('/api/v1/projects/{project_id}/edges/{edge_id}')
def update_edge(project_id: int, edge_id: int, payload: EdgeUpdate, db: Session = Depends(get_db)):
    x = db.query(Edge).filter_by(project_id=project_id, id=edge_id).one_or_none()
    if x is None:
        raise HTTPException(404, 'Edge not found')
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(x, key, int(value) if key == 'directed' else value)
    db.commit(); db.refresh(x)
    return edge_json(x)


@app.delete('/api/v1/projects/{project_id}/edges/{edge_id}')
def delete_edge(project_id: int, edge_id: int, db: Session = Depends(get_db)):
    x = db.query(Edge).filter_by(project_id=project_id, id=edge_id).one_or_none()
    if x is None:
        raise HTTPException(404, 'Edge not found')
    db.delete(x)
    db.commit()
    return {'ok': True}


@app.get('/api/v1/projects/{project_id}/scans')
def scans(project_id: int, db: Session = Depends(get_db)):
    return [{'id': x.id, 'filename': x.filename, 'imported_at': x.imported_at, 'hosts_seen': x.hosts_seen, 'services_seen': x.services_seen} for x in db.query(Scan).filter_by(project_id=project_id).order_by(Scan.id.desc()).all()]


@app.post('/api/v1/projects/{project_id}/imports/nmap')
async def import_nmap(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not db.query(Project).filter_by(id=project_id).first():
        raise HTTPException(404, 'Project not found')
    raw = await file.read()
    if len(raw) > 100 * 1024 * 1024:
        raise HTTPException(413, 'Scan file too large')
    try:
        return import_nmap_xml(db, project_id, file.filename or 'scan.xml', raw)
    except Exception as e:
        db.rollback()
        raise HTTPException(400, f'Could not parse Nmap XML: {e}')


STATIC_DIR = Path(os.environ.get('ATTACKATLAS_STATIC_DIR', '/app/static'))
if STATIC_DIR.exists():
    assets = STATIC_DIR / 'assets'
    if assets.exists():
        app.mount('/assets', StaticFiles(directory=assets), name='assets')

    @app.get('/{full_path:path}', include_in_schema=False)
    def spa(full_path: str):
        candidate = STATIC_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(STATIC_DIR / 'index.html')
