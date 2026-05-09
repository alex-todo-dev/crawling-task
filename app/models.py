from pydantic import BaseModel, Field
from datetime import datetime
from enum import StrEnum


class QueueItemStatus(StrEnum):
    CREATED = "created"
    RUNNING = "running"
    FAILED = "failed"
    COMPLETED = "completed"


class ScanQueueItem(BaseModel):
    id: str
    url_name: str
    depth: int
    status: QueueItemStatus = QueueItemStatus.CREATED
    created_at: datetime = Field(default_factory=datetime.now)
    scanned_by: str | None = None
    scanned_at: datetime | None = None


class Link(BaseModel):
    scan_id: str
    url: str
    depth: int
    found_on: str
    created_at: datetime = Field(default_factory=datetime.now)


class Cookie(BaseModel):
    name: str
    value: str
    domain: str
    path: str
    expires: float | None = None
    http_only: bool = False
    secure: bool = False

class AuthState(BaseModel):
    scan_id: str
    login_url: str
    success: bool
    cookies: list[Cookie]
    created_at: datetime = datetime.now()


class PageRequest(BaseModel):
    scan_id: str
    page_url: str
    method: str
    url: str
    headers: dict
    post_data: str | None

class PageResponse(BaseModel):
    scan_id: str
    page_url: str
    status: int
    headers: dict
    content_type: str
    body_preview: str
