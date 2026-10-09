import motor.motor_asyncio
from config import MONGO_URL

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client["KalakaarBotDB"]
users_col = db["users"]

async def add_user(user_id):
    if not await users_col.find_one({"_id": user_id}):
        await users_col.insert_one({"_id": user_id})

async def get_all_users():
    return [user["_id"] async for user in users_col.find({})]

async def total_users():
    return await users_col.count_documents({})
