from app.models import PageRequest, PageResponse
from app.db.requests import insert_request, insert_response
from motor.motor_asyncio import AsyncIOMotorDatabase


def collect_browser_requests(context, db: AsyncIOMotorDatabase, scan_id: str):

    async def on_request(req):
        doc = PageRequest(
            scan_id=scan_id,
            page_url=req.frame.url,
            method=req.method,
            url=req.url,
            headers=req.headers,
            post_data=req.post_data,
        )
        await insert_request(db, doc)

    async def on_response(res):
        try: 
            body = await res.body()
        except Exception as e: 
            body = 'redirect response - no body'

        doc = PageResponse(
            scan_id=scan_id,
            page_url=res.frame.url,
            status=res.status,
            headers=res.headers,
            content_type=res.headers.get("content-type", ""),
            body_preview=body[:500].decode("utf-8", errors="replace") if isinstance(body, bytes) else body,           
        )
        await insert_response(db, doc)

    context.on("request", on_request)
    context.on("response", on_response)
