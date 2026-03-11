from database.mongo import MongoRepo
from datetime import datetime, timedelta
from bson import ObjectId


class StatisticsService:
    def __init__(self, db_repo: MongoRepo):
        self.repo = db_repo

    async def get_completion_rate(self, user_id: int, days: int = 30) -> float:
        today = datetime.utcnow().date()
        cutoff_str = (today - timedelta(days=days)).strftime("%Y-%m-%d")
        logs = await self.repo.db.daily_logs.find(
            {"user_id": user_id, "date": {"$gte": cutoff_str}}
        ).to_list(length=None)
        if not logs:
            return 0.0
        completed = sum(1 for log in logs if log.get("completed", False))
        return (completed / len(logs)) * 100

    async def calculate_streak(self, user_id: int, habit_id: str) -> int:
        h_id = ObjectId(habit_id)
        logs = await self.repo.db.daily_logs.find(
            {"user_id": user_id, "habit_id": h_id}
        ).sort("date", -1).to_list(None)

        if not logs:
            return 0

        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        yesterday_str = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

        latest_date = logs[0]["date"]
        if latest_date not in (today_str, yesterday_str):
            return 0

        streak = 0
        prev_date = None
        for log in logs:
            if not log.get("completed", False):
                break
            log_date = datetime.strptime(log["date"], "%Y-%m-%d").date()
            if prev_date is None:
                streak = 1
                prev_date = log_date
            else:
                expected = prev_date - timedelta(days=1)
                if log_date == expected:
                    streak += 1
                    prev_date = log_date
                else:
                    break

        return streak

    async def get_current_streaks(self, user_id: int) -> dict:
        habits = await self.repo.db.habits.find(
            {"user_id": user_id, "archived": False}
        ).to_list(None)

        result = {}
        for h in habits:
            streak = await self.calculate_streak(user_id, str(h["_id"]))
            result[str(h["_id"])] = streak
        return result

    async def get_best_habit(self, user_id: int) -> dict | None:
        streaks = await self.get_current_streaks(user_id)
        if not streaks:
            return None
        best_id = max(streaks, key=streaks.get)
        if streaks[best_id] == 0:
            return None
        h = await self.repo.db.habits.find_one({"_id": ObjectId(best_id)})
        return {"_id": best_id, "name": h["name"], "streak": streaks[best_id]}

    async def get_calendar_data(self, user_id: int, days: int = 35) -> dict:
        today = datetime.utcnow().date()
        cutoff_str = (today - timedelta(days=days)).strftime("%Y-%m-%d")
        logs = await self.repo.db.daily_logs.find(
            {"user_id": user_id, "date": {"$gte": cutoff_str}}
        ).to_list(length=None)

        date_map = {}
        for log in logs:
            d = log["date"]
            if d not in date_map:
                date_map[d] = {"total": 0, "completed": 0}
            date_map[d]["total"] += 1
            if log["completed"]:
                date_map[d]["completed"] += 1

        return date_map
