from playwright.async_api import BrowserContext
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import ScanQueueItem, Link, Form, FormField
from app.db.queue import insert_url_queue, get_queue_count
from app.db.links import insert_link
from app.db.forms import insert_form
from app.config import CONFIG
from urllib.parse import urlparse, urljoin, urlunparse
import uuid
import hashlib
import json


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse(parsed._replace(fragment=''))


def hash_form(page_url: str, action: str | None, method: str, fields: list[FormField]) -> str:
    payload = {
        "page_url": page_url,
        "action": action,
        "method": method.upper(),
        "fields": sorted([{"name": f.name, "type": f.type} for f in fields], key=lambda x: x["name"])
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


async def scan_url(context: BrowserContext, db: AsyncIOMotorDatabase, item: ScanQueueItem, scan_id: str):
    page = await context.new_page()

    response = await page.goto(item.url_name)

    # Check if page is HTML, not a file
    if not response or 'text/html' not in response.headers.get('content-type', ''):
        await page.close()
        return

    print(f"SCAN_MODULE: Scanning page: {page.url}")

    # SCAN FOR LINKS AND FILTER
    links = await page.query_selector_all("a[href]")
    links = [await link.get_attribute("href") for link in links]
    links = [link for link in links if link is not None]

    # Filter excluded patterns and exact matches
    links = [link for link in links if link not in CONFIG['exact_exclude'] and not any(p in link for p in CONFIG['exclude_patterns'])]

    # Filter external links — keep only allowed domains
    links = [
        link for link in links
        if not link.startswith('http') or urlparse(link).netloc in CONFIG['allowed_domains']
    ]

    # Filter static/non-HTML file extensions
    links = [link for link in links if not any(urlparse(link).path.endswith(ext) for ext in CONFIG['skip_extensions'])]

    print(f"SCAN_MODULE: Links post filter: {links}")

    # Store and enqueue discovered links
    next_depth = item.depth + 1
    for link in links:
        resolved = normalize_url(urljoin(item.url_name, link))
        await insert_link(db=db, link=Link(scan_id=scan_id, url=resolved, depth=next_depth, found_on=item.url_name))
        if next_depth <= CONFIG['max_depth']:
            if await get_queue_count(db) >= CONFIG['max_pages']:
                print(f"SCAN_MODULE: max_pages ({CONFIG['max_pages']}) reached, stopping enqueue")
                break
            await insert_url_queue(db=db, id=str(uuid.uuid4()), url_name=resolved, depth=next_depth)

    # SCAN FOR FORMS
    form_elements = await page.query_selector_all("form")
    for form_el in form_elements:
        action = await form_el.get_attribute("action")
        method = await form_el.get_attribute("method") or "GET"

        # Extract fields
        field_elements = await form_el.query_selector_all("input, select, textarea")
        fields = []
        for field_el in field_elements:
            name = await field_el.get_attribute("name")
            if not name:
                continue
            fields.append(FormField(
                name=name,
                type=await field_el.get_attribute("type") or "text",
                required=await field_el.get_attribute("required") is not None
            ))

        # Extract buttons
        button_elements = await form_el.query_selector_all("button, input[type='submit'], input[type='button']")
        buttons = [await b.inner_text() or await b.get_attribute("value") or "" for b in button_elements]

        # Detect CSRF token
        csrf_detected = any(
            f.name.lower() in ("csrf_token", "csrf", "_token", "token") for f in fields
        )

        form = Form(
            scan_id=scan_id,
            page_url=item.url_name,
            form_hash=hash_form(item.url_name, action, method, fields),
            action=action,
            method=method.upper(),
            fields=fields,
            buttons=buttons,
            csrf_detected=csrf_detected
        )

        await insert_form(db=db, form=form)
        print(f"SCAN_MODULE: Found form — action={action} method={method} fields={len(fields)} csrf={csrf_detected}")

    # SCAN FOR SCRIPTS
    scripts = await page.query_selector_all("script[src]")
    scripts = [await script.get_attribute("src") for script in scripts]
    print(f"SCAN_MODULE: Found scripts: {scripts}")

    await page.close()
