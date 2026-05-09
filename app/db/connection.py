from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

client: AsyncIOMotorClient = None

# collection names
SCAN_QUEUE = "scan_queue"
BROWSER_REQUESTS = "browser_requests"
BROWSER_RESPONSES = "browser_responses"
AUTH_STATE = "auth_state"
ERROR_LOG = "error_log"
LINKS = "links"


async def get_db(uri: str = "mongodb://localhost:27017", db_name: str = "crawl-task") -> AsyncIOMotorDatabase:
    global client
    if client is None:
        client = AsyncIOMotorClient(uri)
        print("MongoDB connected")
    return client[db_name]


async def db_close() -> dict:
    global client
    if client:
        client.close()
        client = None
        print("MongoDB connection closed")
    return {"db status": "closed"}
