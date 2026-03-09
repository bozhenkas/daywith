from datetime import datetime
from database.mongo import MongoRepo
from database.models import UserData, HabitData, DailyLogData
from bson import ObjectId
from typing import List

class HabitService:
    def __init__(self, db_repo: MongoRepo):
        self.repo = db_repo

    async def get_or_create_user(self, tg_id: int, username: str, first_name: str) -> dict:
        user = await self.repo.db.users.find_one({"telegram_id": tg_id})
        if not user:
            new_user = UserData(
                telegram_id=tg_id,
                username=username,
                first_name=first_name,
                created_at=datetime.utcnow(),
                last_active=datetime.utcnow()
            )
            res = await self.repo.db.users.insert_one(new_user.model_dump(by_alias=True, exclude={"id"}))
            return await self.repo.db.users.find_one({"_id": res.inserted_id})
        else:
            await self.repo.db.users.update_one(
                {"telegram_id": tg_id},
                {"$set": {"last_active": datetime.utcnow()}}
            )
            return user

    async def update_user_time(self, tg_id: int, new_time: str):
        await self.repo.db.users.update_one({"telegram_id": tg_id}, {"$set": {"digest_time": new_time}})

    async def toggle_notifications(self, tg_id: int) -> bool:
        user = await self.repo.db.users.find_one({"telegram_id": tg_id})
        new_val = not user.get("notifications_enabled", True)
        await self.repo.db.users.update_one({"telegram_id": tg_id}, {"$set": {"notifications_enabled": new_val}})
        return new_val

    async def create_habit(self, user_id: int, name: str, h_type: str, goal: int = 7):
        habit = HabitData(
            user_id=user_id,
            name=name,
            type=h_type,
            goal_count=goal,
            created_at=datetime.utcnow()
        )
        await self.repo.db.habits.insert_one(habit.model_dump(by_alias=True, exclude={"id"}))

    async def get_user_habits(self, user_id: int, active_only: bool = True) -> List[dict]:
        query = {"user_id": user_id}
        if active_only:
            query["archived"] = False
        cursor = self.repo.db.habits.find(query)
        return await cursor.to_list(length=None)

    async def get_habit(self, habit_id: str) -> dict:
        return await self.repo.db.habits.find_one({"_id": ObjectId(habit_id)})

    async def archive_habit(self, habit_id: str):
        await self.repo.db.habits.update_one({"_id": ObjectId(habit_id)}, {"$set": {"archived": True}})

    async def get_daily_logs(self, user_id: int, date_str: str) -> List[dict]:
        cursor = self.repo.db.daily_logs.find({"user_id": user_id, "date": date_str})
        return await cursor.to_list(length=None)

    async def mark_habit(self, user_id: int, habit_id: str, date_str: str, completed: bool):
        h_id = ObjectId(habit_id)
        log = await self.repo.db.daily_logs.find_one({
            "user_id": user_id,
            "habit_id": h_id,
            "date": date_str
        })
        if log:
            await self.repo.db.daily_logs.update_one(
                {"_id": log["_id"]},
                {"$set": {"completed": completed, "updated_at": datetime.utcnow()}}
            )
        else:
            new_log = DailyLogData(
                user_id=user_id,
                habit_id=h_id,
                date=date_str,
                completed=completed,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            await self.repo.db.daily_logs.insert_one(new_log.model_dump(by_alias=True, exclude={"id"}))

    async def get_all_users_for_digest(self, current_time_str: str) -> List[dict]:
        cursor = self.repo.db.users.find({
            "notifications_enabled": True,
            "digest_time": current_time_str
        })
        return await cursor.to_list(length=None)
