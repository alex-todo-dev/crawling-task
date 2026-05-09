from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from datetime import datetime
from app.models import QueueItemStatus, ScanQueueItem, Link

client : AsyncIOMotorClient = None


# collections
SCAN_QUEUE = "scan_queue"
BROWSER_REQUESTS = "browser_requests"
BROWSER_RESPONSES = "browser_responses"
AUTH_STATE = "auth_state"
ERROR_LOG = "error_log"
LINKS = "links"

# connect to mongo 
async def get_db(uri: str = "mongodb://localhost:27017", db_name: str = "crawl-task") -> AsyncIOMotorDatabase:
    global client
    if client is None:
        client = AsyncIOMotorClient(uri)
        print("Mongo DB connected")
    return client[db_name]

# close connection
async def db_close() -> dict:
    global client
    if client:
        client.close()
        client = None
        print("Mongo DB connection closed")
    return {"db status":"closed"}


#*********************************** SCAN QUEUE MONGO DB *****************************************************

# inserts new url scan into the queue
async def insert_url_queue(db: AsyncIOMotorDatabase, id: str, url_name: str, depth: int):
    item = ScanQueueItem(id=id, url_name=url_name, depth=depth)
    res = await db[SCAN_QUEUE].update_one({"url_name": url_name}, {"$setOnInsert": item.model_dump()}, upsert=True)
    if res.upserted_id:
        print(f"DB: queued new URL: {url_name} (depth {depth})")
    else:
        print(f"DB: skipped duplicate: {url_name}")
    return res

# get total count of queued pages
async def get_queue_count(db: AsyncIOMotorDatabase) -> int:
    return await db[SCAN_QUEUE].count_documents({})

# update scan queue item status
async def update_scan_item_status(db: AsyncIOMotorDatabase, item: ScanQueueItem):
    update = {"$set": {"status": item.status, "scanned_by": item.scanned_by, "scanned_at": item.scanned_at}}
    res = await db[SCAN_QUEUE].update_one({"id": item.id}, update)
    return res

# pull next url for scan from the queue 
async def pull_next_scan(db: AsyncIOMotorDatabase):                                  
      url =  await db[SCAN_QUEUE].find_one_and_update(                                                               
          {"status": QueueItemStatus.CREATED},                                                                       
          {"$set": {"status": QueueItemStatus.RUNNING}},                                                             
          return_document=True,                                                                                 
      )
      return url

# **************************************** LINKS *************************************************
async def insert_link(db: AsyncIOMotorDatabase, link: Link):
    await db[LINKS].update_one(
        {"scan_id": link.scan_id, "url": link.url},
        {"$setOnInsert": link.model_dump()},
        upsert=True
    )

# **************************************** REQUESTS / RESPONSES *************************************************
async def insert_request(db: AsyncIOMotorDatabase, doc):
    await db[BROWSER_REQUESTS].insert_one(doc.model_dump())

async def insert_response(db: AsyncIOMotorDatabase, doc):
    await db[BROWSER_RESPONSES].insert_one(doc.model_dump())

# **************************************** AUTH STATE *************************************************
async def insert_auth_state(db: AsyncIOMotorDatabase, doc) -> None:
    await db[AUTH_STATE].insert_one(doc.model_dump())

async def get_auth_state(db: AsyncIOMotorDatabase, scan_id: str):
    return await db[AUTH_STATE].find_one({"scan_id": scan_id}, {"_id": 0})












