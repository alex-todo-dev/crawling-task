from app.db.connection import get_db, db_close
from app.db.queue import insert_url_queue, reset_running_items
from app.capture.requests_responses import collect_browser_requests
from app.crawler.worker import worker
from playwright.async_api import async_playwright
import asyncio
import signal
from app.config import CONFIG
from app.auth.login import login
from app.auth.validation import login_verification


async def main():
    # db connection
    db_ = await get_db("mongodb://localhost:27017", "crawl-task")

    # shutdown event — set by SIGINT/SIGTERM or browser close
    shutdown_event = asyncio.Event()

    def handle_shutdown():
        print("\nShutdown signal received — stopping workers gracefully...")
        shutdown_event.set()

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, handle_shutdown)
    loop.add_signal_handler(signal.SIGTERM, handle_shutdown)

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

    # check is url links in Running state due killed process 
    reset_count = await reset_running_items(db_)
    if reset_count:
        print(f"Found {reset_count} stuck in running state.Switched to CREATED")

    # insert after login page depth 0 for scan
    await insert_url_queue(db=db_, id=CONFIG['scan_id'], url_name=CONFIG['start_url_after_login'], depth=0)

    # start workers
    workers = [asyncio.create_task(worker(i, db_, context, shutdown_event)) for i in range(CONFIG['concurrency'])]

    # on browser close also trigger shutdown
    browser.on("disconnected", lambda _: shutdown_event.set())

    # wait until shutdown signal or browser close
    await shutdown_event.wait()

    # wait for all workers to finish their current scan
    print("Waiting for workers to finish current tasks...")
    await asyncio.gather(*workers, return_exceptions=True)

    # reset any items still stuck in RUNNING state for resume
    reset_count = await reset_running_items(db_)
    if reset_count:
        print(f"Reset {reset_count} running items to created for resume")

    await pw.stop()
    await db_close()


asyncio.run(main())
