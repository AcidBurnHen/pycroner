from datetime import datetime

def should_run(schedule: dict[str, set[int]]) -> bool:
    now = datetime.now()
    
    return (
        now.minute in schedule["minute"] and
        now.hour in schedule["hour"] and
        now.day in schedule["day"] and
        now.month in schedule["month"] and
        now.weekday() in schedule["weekday"]
    )