from datetime import datetime

def should_run(schedule: dict[str, int]) -> bool:
    now = datetime.now()

    return all(
        (
            schedule["minute"] & (1 << now.minute),
            schedule["hour"] & (1 << now.hour),
            schedule["day"] & (1 << now.day),
            schedule["month"] & (1 << now.month),
            schedule["weekday"] & (1 << now.weekday()),
        )
    )