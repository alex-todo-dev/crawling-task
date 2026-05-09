from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import Link
from app.db.connection import LINKS


async def insert_link(db: AsyncIOMotorDatabase, link: Link):
    await db[LINKS].update_one(
        {"scan_id": link.scan_id, "url": link.url},
        {"$setOnInsert": link.model_dump()},
        upsert=True
    )
