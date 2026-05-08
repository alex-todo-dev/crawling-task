from pydantic import BaseModel
from datetime import datetime

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
