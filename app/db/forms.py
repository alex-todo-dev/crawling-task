from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import Form

FORMS = "forms"

async def insert_form(db: AsyncIOMotorDatabase, form: Form):
    await db[FORMS].update_one(
        {"scan_id": form.scan_id, "form_hash": form.form_hash},
        {"$setOnInsert": form.model_dump()},
        upsert=True
    )
