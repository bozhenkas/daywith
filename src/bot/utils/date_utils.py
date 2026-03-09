import datetime

def parse_date_str(date_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(date_str, "%Y-%m-%d")

def get_russian_month(date: datetime.date = None) -> str:
    if date is None:
        date = datetime.date.today()
        
    months = {
        1: "январь",
        2: "февраль",
        3: "март",
        4: "апрель",
        5: "май",
        6: "июнь",
        7: "июль",
        8: "август",
        9: "сентябрь",
        10: "октябрь",
        11: "ноябрь",
        12: "декабрь"
    }
    return months.get(date.month, "март")
