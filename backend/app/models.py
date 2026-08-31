from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .db import Base

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, unique=True)
    description = Column(Text, default='')
    notes = Column(Text, default='')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    hosts = relationship('Host', back_populates='project', cascade='all, delete-orphan')

class Host(Base):
    __tablename__ = 'hosts'
    __table_args__ = (UniqueConstraint('project_id', 'address', name='uq_host_project_address'),)
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    address = Column(String(255), nullable=False)
    hostname = Column(String(255), default='')
    domain = Column(String(255), default='')
    os = Column(String(255), default='')
    os_family = Column(String(32), default='unknown')
    device_type = Column(String(32), default='host')
    status = Column(String(32), default='discovered')
    notes = Column(Text, default='')
    sort_order = Column(Integer, default=0, nullable=False)
    pos_x = Column(Integer, default=80, nullable=False)
    pos_y = Column(Integer, default=80, nullable=False)
    project = relationship('Project', back_populates='hosts')
    services = relationship('Service', back_populates='host', cascade='all, delete-orphan')

class Service(Base):
    __tablename__ = 'services'
    __table_args__ = (UniqueConstraint('host_id', 'protocol', 'port', name='uq_service_host_proto_port'),)
    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('hosts.id', ondelete='CASCADE'), nullable=False, index=True)
    protocol = Column(String(16), nullable=False)
    port = Column(Integer, nullable=False)
    state = Column(String(32), default='open')
    name = Column(String(120), default='')
    product = Column(String(255), default='')
    version = Column(String(255), default='')
    extra_info = Column(String(255), default='')
    script_output = Column(Text, default='')
    raw_output = Column(Text, default='')
    host = relationship('Host', back_populates='services')

class Scan(Base):
    __tablename__ = 'scans'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    imported_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    hosts_seen = Column(Integer, default=0)
    services_seen = Column(Integer, default=0)

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    username = Column(String(255), nullable=False)
    domain = Column(String(255), default='')
    notes = Column(Text, default='')
    host_id = Column(Integer, ForeignKey('hosts.id', ondelete='SET NULL'), nullable=True, index=True)

class Credential(Base):
    __tablename__ = 'credentials'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id', ondelete='SET NULL'), nullable=True)
    kind = Column(String(32), default='password')
    secret = Column(Text, nullable=False)
    source = Column(String(255), default='manual')
    host_id = Column(Integer, ForeignKey('hosts.id', ondelete='SET NULL'), nullable=True, index=True)
    notes = Column(Text, default='')

class Share(Base):
    __tablename__ = 'shares'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    host_id = Column(Integer, ForeignKey('hosts.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    path = Column(String(512), default='')
    notes = Column(Text, default='')

class Edge(Base):
    __tablename__ = 'edges'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    source_type = Column(String(32), nullable=False)
    source_id = Column(Integer, nullable=False)
    target_type = Column(String(32), nullable=False)
    target_id = Column(Integer, nullable=False)
    relation = Column(String(64), nullable=False)
    label = Column(String(255), default='')
    directed = Column(Integer, default=1, nullable=False)


class NoteEntry(Base):
    __tablename__ = 'note_entries'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    host_id = Column(Integer, ForeignKey('hosts.id', ondelete='CASCADE'), nullable=True, index=True)
    category = Column(String(64), default='General', nullable=False)
    title = Column(String(255), default='', nullable=False)
    content_markdown = Column(Text, default='', nullable=False)
    tags = Column(String(512), default='', nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)

class Attachment(Base):
    __tablename__ = 'attachments'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    note_id = Column(Integer, ForeignKey('note_entries.id', ondelete='CASCADE'), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    mime_type = Column(String(128), nullable=False)
    size = Column(Integer, default=0, nullable=False)
    caption = Column(String(512), default='', nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class ReportBlock(Base):
    __tablename__ = 'report_blocks'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), default='', nullable=False)
    content_markdown = Column(Text, default='', nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
