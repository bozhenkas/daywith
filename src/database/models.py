from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> Any:
        from pydantic_core import core_schema
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate)
            ])
        ])

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class UserData(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    digest_time: str = "21:00"
    timezone: str = "UTC"
    notifications_enabled: bool = True
    language: str = "ru"
    created_at: datetime
    last_active: datetime

class HabitData(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: int
    name: str
    type: str
    goal_type: str = "daily"
    goal_count: int = 7
    created_at: datetime
    archived: bool = False

class DailyLogData(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: int
    habit_id: PyObjectId
    date: str
    completed: bool
    created_at: datetime
    updated_at: datetime
