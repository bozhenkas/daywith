from datetime import datetime, timedelta

def get_today_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")

def get_date_str(date_obj: datetime) -> str:
    return date_obj.strftime("%Y-%m-%d")

def parse_date_str(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")

def get_previous_day(date_obj: datetime) -> datetime:
    return date_obj - timedelta(days=1)

def get_next_day(date_obj: datetime) -> datetime:
    return date_obj + timedelta(days=1)
