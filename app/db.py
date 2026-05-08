from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from datetime import datetime
from enum import StrEnum

client : AsyncIOMotorClient = None


# collections 
SCAN_QUEUE = "scan_queue"
BROWSER_REQUETS =  "browser_requests"
BROWSER_RESPONSES = "browser_responses"
AUTH_STATE = "auth_state"


# data classes
class QueueItemStatus(StrEnum):
    CREATED = "created"
    RUNNING = "running"
    FAILED = "failed"
    COMPLETED = "completed"

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
async def insert_scan_queue(db: AsyncIOMotorDatabase, id: str, url_name: str):
    doc = {
        "id": id, 
        "url_neme": url_name,
        "status": QueueItemStatus.CREATED,
        "created_at": datetime.now(),
        "scanned_by": None,
        "scanned_at": None
    }
    res = await db[SCAN_QUEUE].insert_one(doc)
    return res

# update scan queue item status 
async def update_scan_item_status(db: AsyncIOMotorDatabase, item_id: str, status: QueueItemStatus, woker_id: str):
    update = {"$set":{"status": status, "scanned_by": woker_id, "scanned_at": datetime.now()}}
    res = await db[SCAN_QUEUE].update_one({"id": item_id}, update)
    return res

# pull next url for scan from the queue 
async def pull_next_scan(db: AsyncIOMotorDatabase):                                  
      url =  await db[SCAN_QUEUE].find_one_and_update(                                                               
          {"status": QueueItemStatus.CREATED},                                                                       
          {"$set": {"status": QueueItemStatus.RUNNING}},                                                             
          return_document=True,                                                                                 
      )
      return url

# **************************************** RESQUESTS / RESPONSES *************************************************
async def insert_request(db: AsyncIOMotorDatabase, doc):
    await db[BROWSER_REQUETS].insert_one(doc.model_dump())

async def insert_response(db: AsyncIOMotorDatabase, doc):
    await db[BROWSER_RESPONSES].insert_one(doc.model_dump())

# **************************************** AUTH STATE *************************************************
async def insert_auth_state(db: AsyncIOMotorDatabase, doc) -> None:
    await db[AUTH_STATE].insert_one(doc.model_dump())

async def get_auth_state(db: AsyncIOMotorDatabase, scan_id: str):
    return await db[AUTH_STATE].find_one({"scan_id": scan_id}, {"_id": 0})












