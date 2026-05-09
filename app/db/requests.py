from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.connection import BROWSER_REQUESTS, BROWSER_RESPONSES, AUTH_STATE


async def insert_request(db: AsyncIOMotorDatabase, doc):
    await db[BROWSER_REQUESTS].insert_one(doc.model_dump())


async def insert_response(db: AsyncIOMotorDatabase, doc):
    await db[BROWSER_RESPONSES].insert_one(doc.model_dump())


async def insert_auth_state(db: AsyncIOMotorDatabase, doc) -> None:
    await db[AUTH_STATE].insert_one(doc.model_dump())


async def get_auth_state(db: AsyncIOMotorDatabase, scan_id: str):
    return await db[AUTH_STATE].find_one({"scan_id": scan_id}, {"_id": 0})
