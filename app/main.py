from app.db import get_db, db_close, insert_url_queue
from app.capture.requests_responses import collect_browser_requests
from app.crawler.worker import worker
from playwright.async_api import async_playwright
import asyncio
from app.config import CONFIG
from app.auth.login import login
from app.auth.validation import login_verification


async def main():
    # db connection
    db_ = await get_db("mongodb://localhost:27017", "crawl-task")

    # start playwright browser
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=False)
    context = await browser.new_context()

    # start collecting responses/requests 
    collect_browser_requests(context=context, db=db_, scan_id=CONFIG['scan_id'])

    # start new page and navigate to login 
    page = await context.new_page()
    await page.goto(CONFIG["login_url"])

    # login action 
    await login(page=page)

    # login validation
    await login_verification(page=page, expected_url=CONFIG['start_url_after_login'], db=db_)
    
    # insert after login page depth 0 for scan
    await insert_url_queue(db=db_, id=CONFIG['scan_id'], url_name=CONFIG['start_url_after_login'], depth=0)

    # start workers
    workers = [asyncio.create_task(worker(i, db_, context)) for i in range(CONFIG['concurrency'])]

    



    # on browser close
    stop = asyncio.Event()
    browser.on("disconnected", lambda _: stop.set())
    await stop.wait()

    # workers cancel 
    for w in workers:
        w.cancel()
    await asyncio.gather(*workers, return_exceptions=True)

    await pw.stop()

    # db connection close
    await db_close()


asyncio.run(main())