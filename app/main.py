from app.db import get_db, db_close
from app.requests_responses import collect_browser_requests
from playwright.async_api import async_playwright
import asyncio
from app.config import CONFIG
from app.login import login
from app.login_validation import login_verification


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
    loging_status = await login_verification(page=page, expected_url=CONFIG['start_url_after_login'])
    print(loging_status)
    
   


    # on browser close 
    stop = asyncio.Event()
    browser.on("disconnected", lambda _: stop.set())
    await stop.wait()  
    await pw.stop()

    # db connection close
    await db_close()


asyncio.run(main())