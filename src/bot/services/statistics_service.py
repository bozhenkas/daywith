from database.mongo import MongoRepo
from datetime import datetime, timedelta

class StatisticsService:
    def __init__(self, db_repo: MongoRepo):
        self.repo = db_repo

    async def get_completion_rate(self, user_id: int, days: int = 30) -> float:
        cutoff = datetime.utcnow() - timedelta(days=days)
        cursor = self.repo.db.daily_logs.find({"user_id": user_id, "created_at": {"$gte": cutoff}})
        logs = await cursor.to_list(length=None)
        
        if not logs:
            return 0.0
        
        completed = sum(1 for log in logs if log.get("completed", False))
        return (completed / len(logs)) * 100

    async def calculate_streak(self, user_id: int, habit_id: str) -> int:
        from bson import ObjectId
        h_id = ObjectId(habit_id)
        logs = await self.repo.db.daily_logs.find({
            "user_id": user_id,
            "habit_id": h_id
        }).sort("date", -1).to_list(None)
        
        streak = 0
        for log in logs:
            if log.get("completed", False):
                streak += 1
            else:
                break
        return streak

    async def get_current_streaks(self, user_id: int) -> dict:
        habits = await self.repo.db.habits.find({"user_id": user_id, "archived": False}).to_list(None)
        res = {}
        for h in habits:
            streak = await self.calculate_streak(user_id, str(h["_id"]))
            res[str(h["_id"])] = streak
        return res

    async def get_best_habit(self, user_id: int) -> dict:
        streaks = await self.get_current_streaks(user_id)
        if not streaks:
            return None
        
        best_id = max(streaks, key=streaks.get)
        if streaks[best_id] == 0:
            return None
            
        from bson import ObjectId
        h = await self.repo.db.habits.find_one({"_id": ObjectId(best_id)})
        return {"name": h["name"], "streak": streaks[best_id]}
        
    async def get_calendar_data(self, user_id: int, days: int = 30) -> dict:
        cutoff = datetime.utcnow() - timedelta(days=days)
        logs = await self.repo.db.daily_logs.find({"user_id": user_id, "created_at": {"$gte": cutoff}}).to_list(None)
        
        date_map = {}
        for log in logs:
            d = log["date"]
            if d not in date_map:
                date_map[d] = {"total": 0, "completed": 0}
            date_map[d]["total"] += 1
            if log["completed"]:
                date_map[d]["completed"] += 1
                
        return date_map
