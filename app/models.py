from pydantic import BaseModel

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
