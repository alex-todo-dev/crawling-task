from motor.motor_asyncio import AsyncIOMotorDatabase
from playwright.async_api import BrowserContext
from app.db.queue import pull_next_scan, update_scan_item_status
from app.models import QueueItemStatus, ScanQueueItem
from app.crawler.scan_url import scan_url
from app.config import CONFIG
from datetime import datetime
import asyncio

async def worker(worker_id: int, db: AsyncIOMotorDatabase, context: BrowserContext, shutdown_event: asyncio.Event):

    pull_frequency = 1.0
    print(f"WORKER {worker_id}: started and waiting for new URL")

    while not shutdown_event.is_set():
        # pulls next url from the queue 
        raw = await pull_next_scan(db)

        if not raw:
            await asyncio.sleep(pull_frequency)
        else:
            item = ScanQueueItem(**{k: v for k, v in raw.items() if k != '_id'})
            print("*************************************************")
            print(f"WORKER {worker_id}: Scanning: {item.url_name}")

            try:
                await scan_url(context=context, db=db, item=item, scan_id=CONFIG['scan_id'])
                item.status = QueueItemStatus.COMPLETED
            except Exception as e:
                print(f"WORKER {worker_id}: failed to scan {item.url_name} — {e}")
                item.status = QueueItemStatus.FAILED

            item.scanned_by = str(worker_id)
            item.scanned_at = datetime.now()
            await update_scan_item_status(db=db, item=item)

    print(f"WORKER {worker_id}: stopped gracefully")

                
        
    