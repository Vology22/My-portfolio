from datetime import datetime, date, timedelta

def is_even_week(target_date=None):
    start_date = date(2025, 9, 1)
    if target_date is None:
        target_date = date.today()
    delta_days = (target_date - start_date).days
    week_number = delta_days // 7 + 1
    return week_number % 2 == 0


# Примеры использования
if __name__ == "__main__":
    print(f"Четная неделя: {is_even_week()}")

    