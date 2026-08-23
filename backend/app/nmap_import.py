from pathlib import Path
from tempfile import NamedTemporaryFile
from xml.etree.ElementTree import iterparse, tostring
from sqlalchemy.orm import Session
from .models import Host, Service, Scan


def _first_text(host_el, path, attr):
    node = host_el.find(path)
    return node.attrib.get(attr, '') if node is not None else ''


def _guess_os_family(os_name: str) -> str:
    s = (os_name or '').lower()
    if 'windows' in s or 'microsoft' in s:
        return 'windows'
    if 'linux' in s:
        return 'linux'
    if 'mac os' in s or 'macos' in s or 'darwin' in s or 'apple' in s:
        return 'macos'
    if any(x in s for x in ('freebsd', 'openbsd', 'netbsd')):
        return 'bsd'
    return 'unknown'


def _scan_host_identity(elem):
    addr_el = elem.find("address[@addrtype='ipv4']") or elem.find('address')
    address = addr_el.attrib.get('addr', '') if addr_el is not None else ''
    hostname = _first_text(elem, './hostnames/hostname', 'name')
    return address, hostname


def _apply_host_element(db: Session, host: Host, elem) -> tuple[int, int]:
    new_services = updated_services = 0
    hostname = _first_text(elem, './hostnames/hostname', 'name')
    os_name = _first_text(elem, './os/osmatch', 'name')
    if hostname and not host.hostname:
        host.hostname = hostname
    if os_name:
        host.os = os_name
        if not host.os_family or host.os_family == 'unknown':
            host.os_family = _guess_os_family(os_name)

    for port_el in elem.findall('./ports/port'):
        state_el = port_el.find('state')
        state = state_el.attrib.get('state', '') if state_el is not None else ''
        if state != 'open':
            continue
        port = int(port_el.attrib['portid'])
        proto = port_el.attrib.get('protocol', 'tcp')
        svc_el = port_el.find('service')
        attrs = svc_el.attrib if svc_el is not None else {}
        script_blocks = []
        for script_el in port_el.findall('script'):
            script_id = script_el.attrib.get('id', 'script')
            output = script_el.attrib.get('output', '')
            script_blocks.append(f'[{script_id}]\n{output}'.rstrip())
        values = dict(
            state=state,
            name=attrs.get('name', ''),
            product=attrs.get('product', ''),
            version=attrs.get('version', ''),
            extra_info=attrs.get('extrainfo', ''),
            script_output='\n\n'.join(script_blocks),
            raw_output=tostring(port_el, encoding='unicode'),
        )
        svc = db.query(Service).filter_by(host_id=host.id, protocol=proto, port=port).one_or_none()
        if svc is None:
            db.add(Service(host_id=host.id, protocol=proto, port=port, **values))
            new_services += 1
        else:
            changed = False
            for key, value in values.items():
                if value and getattr(svc, key) != value:
                    setattr(svc, key, value)
                    changed = True
            if changed:
                updated_services += 1
    return new_services, updated_services


def import_nmap_xml(db: Session, project_id: int, filename: str, raw: bytes, target_host_id: int | None = None):
    """Import Nmap XML globally, or merge one host scan into an explicitly selected host."""
    with NamedTemporaryFile(delete=False, suffix='.xml') as tmp:
        tmp.write(raw)
        tmp_path = Path(tmp.name)

    target = None
    if target_host_id is not None:
        target = db.query(Host).filter_by(id=target_host_id, project_id=project_id).one_or_none()
        if target is None:
            raise ValueError('Target host not found in this project')

    parsed = []
    try:
        for _, elem in iterparse(tmp_path, events=('end',)):
            if elem.tag != 'host':
                continue
            status = elem.find('status')
            if status is not None and status.attrib.get('state') not in ('up', None):
                elem.clear()
                continue
            address, hostname = _scan_host_identity(elem)
            if not address and not hostname:
                elem.clear()
                continue
            # Keep a compact serialized host element only until selection is resolved.
            import xml.etree.ElementTree as ET
            parsed.append((address, hostname, ET.tostring(elem, encoding='unicode')))
            elem.clear()

        if target is not None:
            matches = [x for x in parsed if x[0] == target.address or (target.hostname and x[1] == target.hostname)]
            if not matches and len(parsed) == 1:
                matches = parsed
            if len(matches) != 1:
                raise ValueError('Targeted import must contain exactly one matching host, or a single-host Nmap scan')
            import xml.etree.ElementTree as ET
            elem = ET.fromstring(matches[0][2])
            service_count = sum(1 for p in elem.findall('./ports/port') if p.find('state') is not None and p.find('state').attrib.get('state') == 'open')
            new_services, updated_services = _apply_host_element(db, target, elem)
            db.add(Scan(project_id=project_id, filename=filename, hosts_seen=1, services_seen=service_count))
            db.commit()
            return {
                'filename': filename,
                'hosts_seen': 1,
                'services_seen': service_count,
                'new_hosts': 0,
                'new_services': new_services,
                'updated_services': updated_services,
                'target_host_id': target.id,
                'changes': [f'updated host {target.address}'],
            }

        hosts_seen = services_seen = new_hosts = new_services = updated_services = 0
        changes = []
        import xml.etree.ElementTree as ET
        max_order = db.query(Host).filter_by(project_id=project_id).count()
        for address, hostname, xml in parsed:
            elem = ET.fromstring(xml)
            hosts_seen += 1
            os_name = _first_text(elem, './os/osmatch', 'name')
            host = db.query(Host).filter_by(project_id=project_id, address=address).one_or_none()
            if host is None:
                host = Host(
                    project_id=project_id,
                    address=address,
                    hostname=hostname,
                    os=os_name,
                    os_family=_guess_os_family(os_name),
                    device_type='host',
                    sort_order=max_order,
                    pos_x=80 + (max_order % 5) * 300,
                    pos_y=80 + (max_order // 5) * 190,
                )
                max_order += 1
                db.add(host)
                db.flush()
                new_hosts += 1
                changes.append(f'+ host {address} {hostname}'.strip())
            ns, us = _apply_host_element(db, host, elem)
            new_services += ns
            updated_services += us
            services_seen += sum(1 for p in elem.findall('./ports/port') if p.find('state') is not None and p.find('state').attrib.get('state') == 'open')

        db.add(Scan(project_id=project_id, filename=filename, hosts_seen=hosts_seen, services_seen=services_seen))
        db.commit()
        return {
            'filename': filename,
            'hosts_seen': hosts_seen,
            'services_seen': services_seen,
            'new_hosts': new_hosts,
            'new_services': new_services,
            'updated_services': updated_services,
            'changes': changes[:100],
        }
    finally:
        tmp_path.unlink(missing_ok=True)
