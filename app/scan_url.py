from playwright.async_api import BrowserContext
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import ScanQueueItem
from app.db import insert_url_queue
from app.config import CONFIG
from urllib.parse import urlparse, urljoin, urlunparse
import uuid

def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse(parsed._replace(fragment=''))

async def scan_url(context: BrowserContext, db: AsyncIOMotorDatabase, item: ScanQueueItem):
    page = await context.new_page()

    response = await page.goto(item.url_name)

    # Check if page is html. NOT a file 
    if not response or 'text/html' not in response.headers.get('content-type', ''):                                                                                                                           
        await page.close()
        return 

    print(f"SCAN_MODULE:Scanning page:{page.url}")



    # SCAN FOR LINKS AND FILTER
    links = await page.query_selector_all("a[href]")
    links = [await link.get_attribute("href") for link in links]
    links = [link for link in links if link is not None]

    # Filter links exclude
    links = [link for link in links if link not in CONFIG['exact_exclude'] and not any(p in link for p in CONFIG['exclude_patterns'])]

    # Filter external links. Or starts with http or differnet domain name
    links = [
      link for link in links
      if not link.startswith('http') or urlparse(link).netloc in CONFIG['allowed_domains']]

    # Filter static/non-HTML file extensions
    links = [link for link in links if not any(urlparse(link).path.endswith(ext) for ext in CONFIG['skip_extensions'])]

    print(f"SCAN_MODULE:Links post filter:{links}")

    # Resolve and enqueue links within depth limit
    next_depth = item.depth + 1
    if next_depth <= CONFIG['max_depth']:
        for link in links:
            resolved = normalize_url(urljoin(item.url_name, link))
            await insert_url_queue(db=db, id=str(uuid.uuid4()), url_name=resolved, depth=next_depth)




    # SCAN FOR FORMS 
    forms = await page.query_selector_all("form")
    forms = [await form.get_attribute("action") for form in forms]
    print(f"SCAN_MODULE:Found page forms:{forms}")

    # SCAN FOR BUTTONS
    buttons = await page.query_selector_all("button, input[type='submit'], input[type='button']")
    buttons = [await button.inner_text() for button in buttons]
    print(f"SCAN_MODULE:Found page buttons:{buttons}")

    # SCAN FOR SCIPTS
    scripts = await page.query_selector_all("script[src]")
    scripts = [await script.get_attribute("src") for script in scripts]
    print(f"SCAN_MODULE:Found page scripts:{scripts}")

   

    await page.close()
