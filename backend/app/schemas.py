from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    name: str
    description: str = ''
    notes: str = ''

class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    notes: str | None = None

class HostCreate(BaseModel):
    address: str
    hostname: str = ''
    domain: str = ''
    os: str = ''
    os_family: str = 'unknown'
    device_type: str = 'host'
    status: str = 'discovered'
    notes: str = ''
    pos_x: int = 80
    pos_y: int = 80

class HostUpdate(BaseModel):
    address: str | None = None
    hostname: str | None = None
    domain: str | None = None
    os: str | None = None
    os_family: str | None = None
    device_type: str | None = None
    status: str | None = None
    notes: str | None = None
    pos_x: int | None = None
    pos_y: int | None = None

class HostReorder(BaseModel):
    host_ids: list[int] = Field(default_factory=list)

class AccountCreate(BaseModel):
    username: str
    domain: str = ''
    notes: str = ''
    host_id: int | None = None

class AccountUpdate(BaseModel):
    username: str | None = None
    domain: str | None = None
    notes: str | None = None
    host_id: int | None = None

class CredentialCreate(BaseModel):
    account_id: int | None = None
    username: str = ''
    domain: str = ''
    kind: str = 'password'
    secret: str
    source: str = 'manual'
    host_id: int | None = None
    notes: str = ''

class CredentialUpdate(BaseModel):
    account_id: int | None = None
    username: str | None = None
    domain: str | None = None
    kind: str | None = None
    secret: str | None = None
    source: str | None = None
    host_id: int | None = None
    notes: str | None = None

class ShareCreate(BaseModel):
    host_id: int
    name: str
    path: str = ''
    notes: str = ''

class EdgeCreate(BaseModel):
    source_type: str
    source_id: int
    target_type: str
    target_id: int
    relation: str
    label: str = ''
    directed: bool = True

class EdgeUpdate(BaseModel):
    relation: str | None = None
    label: str | None = None
    directed: bool | None = None


class NoteEntryCreate(BaseModel):
    host_id: int | None = None
    category: str = 'General'
    title: str = ''
    content_markdown: str = ''
    tags: str = ''

class NoteEntryUpdate(BaseModel):
    category: str | None = None
    title: str | None = None
    content_markdown: str | None = None
    tags: str | None = None
    sort_order: int | None = None

class AttachmentUpdate(BaseModel):
    caption: str | None = None

class ReportBlockCreate(BaseModel):
    title: str = ''
    content_markdown: str = ''

class ReportBlockUpdate(BaseModel):
    title: str | None = None
    content_markdown: str | None = None
    sort_order: int | None = None
