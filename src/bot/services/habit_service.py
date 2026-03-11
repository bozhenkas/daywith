from datetime import datetime
from database.mongo import MongoRepo
from database.models import UserData, HabitData, DailyLogData
from bson import ObjectId
from typing import List, Optional


class HabitService:
    def __init__(self, db_repo: MongoRepo):
        self.repo = db_repo

    async def get_or_create_user(
        self,
        tg_id: int,
        username: Optional[str],
        first_name: Optional[str],
        last_name: Optional[str] = None,
        lang_code: Optional[str] = None,
        is_premium: Optional[bool] = None,
    ) -> dict:
        user = await self.repo.db.users.find_one({"telegram_id": tg_id})
        now = datetime.utcnow()
        if not user:
            new_user = UserData(
                telegram_id=tg_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=lang_code,
                is_premium=is_premium,
                created_at=now,
                last_active=now,
            )
            res = await self.repo.db.users.insert_one(new_user.model_dump(by_alias=True, exclude={"id"}))
            return await self.repo.db.users.find_one({"_id": res.inserted_id})
        else:
            await self.repo.db.users.update_one(
                {"telegram_id": tg_id},
                {"$set": {
                    "last_active": now,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "language_code": lang_code,
                    "is_premium": is_premium,
                }},
            )
            return await self.repo.db.users.find_one({"telegram_id": tg_id})

    async def get_user(self, tg_id: int) -> Optional[dict]:
        return await self.repo.db.users.find_one({"telegram_id": tg_id})

    async def reset_user_data(self, user_id: int) -> None:
        habits = await self.repo.db.habits.find({"user_id": user_id}).to_list(None)
        if habits:
            for h in habits:
                h["reset_at"] = datetime.utcnow()
            await self.repo.db.backup_habits.insert_many(habits)
            await self.repo.db.habits.delete_many({"user_id": user_id})

        logs = await self.repo.db.daily_logs.find({"user_id": user_id}).to_list(None)
        if logs:
            for l in logs:
                l["reset_at"] = datetime.utcnow()
            await self.repo.db.backup_logs.insert_many(logs)
            await self.repo.db.daily_logs.delete_many({"user_id": user_id})

        await self.repo.db.users.update_one(
            {"telegram_id": user_id},
            {"$set": {"digest_time": "21:00", "notifications_enabled": True}},
        )

    async def update_user_time(self, tg_id: int, new_time: str) -> None:
        await self.repo.db.users.update_one(
            {"telegram_id": tg_id}, {"$set": {"digest_time": new_time}}
        )

    async def update_user_timezone(self, tg_id: int, timezone: str) -> None:
        await self.repo.db.users.update_one(
            {"telegram_id": tg_id}, {"$set": {"timezone": timezone}}
        )

    async def toggle_notifications(self, tg_id: int) -> bool:
        user = await self.repo.db.users.find_one({"telegram_id": tg_id})
        new_val = not user.get("notifications_enabled", True)
        await self.repo.db.users.update_one(
            {"telegram_id": tg_id}, {"$set": {"notifications_enabled": new_val}}
        )
        return new_val

    async def update_last_digest_date(self, tg_id: int, date_str: str) -> None:
        await self.repo.db.users.update_one(
            {"telegram_id": tg_id}, {"$set": {"last_digest_date": date_str}}
        )

    async def create_habit(self, user_id: int, name: str, h_type: str, goal: int = 7) -> None:
        habit = HabitData(
            user_id=user_id,
            name=name,
            type=h_type,
            goal_count=goal,
            created_at=datetime.utcnow(),
        )
        await self.repo.db.habits.insert_one(habit.model_dump(by_alias=True, exclude={"id"}))

    async def get_user_habits(self, user_id: int, active_only: bool = True) -> List[dict]:
        query = {"user_id": user_id}
        if active_only:
            query["archived"] = False
        return await self.repo.db.habits.find(query).sort("created_at", 1).to_list(length=None)

    async def get_habit(self, habit_id: str) -> Optional[dict]:
        return await self.repo.db.habits.find_one({"_id": ObjectId(habit_id)})

    async def archive_habit(self, habit_id: str) -> None:
        await self.repo.db.habits.update_one(
            {"_id": ObjectId(habit_id)}, {"$set": {"archived": True}}
        )

    async def rename_habit(self, habit_id: str, new_name: str) -> None:
        await self.repo.db.habits.update_one(
            {"_id": ObjectId(habit_id)}, {"$set": {"name": new_name}}
        )

    async def get_daily_logs(self, user_id: int, date_str: str) -> List[dict]:
        return await self.repo.db.daily_logs.find(
            {"user_id": user_id, "date": date_str}
        ).to_list(length=None)

    async def mark_habit(self, user_id: int, habit_id: str, date_str: str, completed: bool) -> None:
        h_id = ObjectId(habit_id)
        log = await self.repo.db.daily_logs.find_one(
            {"user_id": user_id, "habit_id": h_id, "date": date_str}
        )
        if log:
            await self.repo.db.daily_logs.update_one(
                {"_id": log["_id"]},
                {"$set": {"completed": completed, "updated_at": datetime.utcnow()}},
            )
        else:
            new_log = DailyLogData(
                user_id=user_id,
                habit_id=h_id,
                date=date_str,
                completed=completed,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            await self.repo.db.daily_logs.insert_one(
                new_log.model_dump(by_alias=True, exclude={"id"})
            )

    async def get_all_notif_users(self) -> List[dict]:
        return await self.repo.db.users.find(
            {"notifications_enabled": True}
        ).to_list(length=None)
