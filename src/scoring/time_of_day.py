"""Time of day definitions and utilities."""

from datetime import datetime, time
from src.models import TimeOfDay


# Time block definitions
TIME_BLOCKS = {
    TimeOfDay.MORNING: (time(8, 0), time(10, 30)),
    TimeOfDay.LATE_MORNING: (time(10, 30), time(12, 30)),
    TimeOfDay.AFTERNOON: (time(12, 30), time(16, 0)),
}


def get_time_block(dt: datetime) -> TimeOfDay:
    """Get the time block for a given datetime.
    
    Args:
        dt: Datetime to classify
    
    Returns:
        TimeOfDay enum value
    """
    t = dt.time()
    
    for block, (start, end) in TIME_BLOCKS.items():
        if start <= t < end:
            return block
    
    # Default to morning for times outside blocks
    return TimeOfDay.MORNING


def get_representative_hour(time_of_day: TimeOfDay) -> int:
    """Get a representative hour for a time block.
    
    Returns:
        Hour of day (0-23)
    """
    return {
        TimeOfDay.MORNING: 9,
        TimeOfDay.LATE_MORNING: 11,
        TimeOfDay.AFTERNOON: 14,
    }[time_of_day]


def list_time_blocks() -> list:
    """Get list of all time blocks in order."""
    return [TimeOfDay.MORNING, TimeOfDay.LATE_MORNING, TimeOfDay.AFTERNOON]
