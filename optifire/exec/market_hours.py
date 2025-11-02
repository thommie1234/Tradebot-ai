"""
Market hours utilities.
"""
from datetime import datetime, time, timezone, timedelta


def is_market_open() -> bool:
    """
    Check if US market is currently open.
    NYSE/NASDAQ hours: 9:30 AM - 4:00 PM ET, Monday-Friday
    """
    # Get current time in UTC and convert to ET (UTC-5 or UTC-4 depending on DST)
    now_utc = datetime.now(timezone.utc)
    # Approximate ET as UTC-5 (standard time)
    et_offset = timedelta(hours=-5)
    now_et = now_utc + et_offset

    # Check if weekend
    if now_et.weekday() >= 5:  # Saturday=5, Sunday=6
        return False

    # Check if within market hours (9:30 AM - 4:00 PM ET)
    market_open = time(9, 30)
    market_close = time(16, 0)
    current_time = now_et.time()

    return market_open <= current_time <= market_close


def get_market_status() -> dict:
    """Get detailed market status."""
    now_utc = datetime.now(timezone.utc)
    et_offset = timedelta(hours=-5)
    now_et = now_utc + et_offset

    is_open = is_market_open()
    is_weekend = now_et.weekday() >= 5

    if is_weekend:
        status = "closed_weekend"
        message = f"Market is closed (weekend). Next open: Monday 9:30 AM ET."
    elif is_open:
        status = "open"
        message = "Market is open (9:30 AM - 4:00 PM ET)"
    else:
        current_time = now_et.time()
        if current_time < time(9, 30):
            status = "pre_market"
            message = f"Market opens at 9:30 AM ET (currently {current_time.strftime('%I:%M %p')} ET)"
        else:
            status = "after_hours"
            message = f"Market closed at 4:00 PM ET (currently {current_time.strftime('%I:%M %p')} ET)"

    return {
        "is_open": is_open,
        "status": status,
        "message": message,
        "current_time_et": now_et.strftime('%Y-%m-%d %I:%M %p ET'),
    }
