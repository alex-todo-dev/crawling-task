from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import QueueItemStatus, ScanQueueItem
from app.db.connection import SCAN_QUEUE


async def insert_url_queue(db: AsyncIOMotorDatabase, id: str, url_name: str, depth: int):
    item = ScanQueueItem(id=id, url_name=url_name, depth=depth)
    res = await db[SCAN_QUEUE].update_one(
        {"url_name": url_name},
        {"$setOnInsert": item.model_dump()},
        upsert=True
    )
    if res.upserted_id:
        print(f"DB: queued new URL: {url_name} (depth {depth})")
    else:
        print(f"DB: skipped duplicate: {url_name}")
    return res


async def get_queue_count(db: AsyncIOMotorDatabase) -> int:
    return await db[SCAN_QUEUE].count_documents({})


async def update_scan_item_status(db: AsyncIOMotorDatabase, item: ScanQueueItem):
    update = {"$set": {"status": item.status, "scanned_by": item.scanned_by, "scanned_at": item.scanned_at}}
    res = await db[SCAN_QUEUE].update_one({"id": item.id}, update)
    return res


async def pull_next_scan(db: AsyncIOMotorDatabase):
    return await db[SCAN_QUEUE].find_one_and_update(
        {"status": QueueItemStatus.CREATED},
        {"$set": {"status": QueueItemStatus.RUNNING}},
        return_document=True,
    )


async def reset_running_items(db: AsyncIOMotorDatabase) -> int:
    res = await db[SCAN_QUEUE].update_many(
        {"status": QueueItemStatus.RUNNING},
        {"$set": {"status": QueueItemStatus.CREATED, "scanned_by": None, "scanned_at": None}}
    )
    return res.modified_count
