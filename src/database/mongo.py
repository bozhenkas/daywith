from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import asyncio

class MongoRepo:
    def __init__(self, uri: str, db_name: str):
        self._client = AsyncIOMotorClient(uri)
        self.db: AsyncIOMotorDatabase = self._client[db_name]
        
    async def init_indexes(self):
        await self.db.users.create_index("telegram_id", unique=True)
        await self.db.habits.create_index([("user_id", 1), ("archived", 1)])
        await self.db.daily_logs.create_index([("user_id", 1), ("date", 1), ("habit_id", 1)], unique=True)

    def close(self):
        self._client.close()
