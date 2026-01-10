"""Freeze-thaw cycle detection and analysis."""

from typing import List, Tuple
from src.models import WeatherConditions


def detect_freeze_thaw_cycles(weather_history: List[WeatherConditions]) -> List[Tuple[int, bool]]:
    """Detect freeze-thaw cycles in weather history.
    
    Returns:
        List of (hour_index, had_good_refreeze) tuples
    """
    cycles = []
    
    for i in range(24, len(weather_history)):
        # Look at previous 24 hours
        last_24h = weather_history[i-24:i]
        
        # Check if we had temperatures above freezing
        had_thaw = any(w.temperature > 2 for w in last_24h[6:18])  # daytime
        
        # Check if we had good refreeze overnight
        overnight = last_24h[-8:]  # last 8 hours
        had_refreeze = all(w.temperature < -2 for w in overnight) if overnight else False
        
        if had_thaw:
            cycles.append((i, had_refreeze))
    
    return cycles


def evaluate_overnight_refreeze(overnight_weather: List[WeatherConditions]) -> Tuple[str, float]:
    """Evaluate the quality of overnight refreeze.
    
    Args:
        overnight_weather: Weather conditions from previous night (6-12 hours)
    
    Returns:
        Tuple of (quality_description, quality_score 0-1)
    """
    if not overnight_weather:
        return "unknown", 0.5
    
    temps = [w.temperature for w in overnight_weather]
    avg_temp = sum(temps) / len(temps)
    min_temp = min(temps)
    
    # Excellent refreeze: consistently below -5°C
    if avg_temp < -5 and min_temp < -8:
        return "excellent", 1.0
    
    # Good refreeze: consistently below -2°C
    if avg_temp < -2 and all(t < 0 for t in temps):
        return "good", 0.8
    
    # Fair refreeze: mostly below 0°C
    if avg_temp < 0 and sum(1 for t in temps if t < 0) > len(temps) * 0.7:
        return "fair", 0.6
    
    # Poor refreeze: some freezing but inconsistent
    if min_temp < -1:
        return "poor", 0.3
    
    # No refreeze
    return "none", 0.0


def has_recent_snowfall(weather_history: List[WeatherConditions], hours: int = 12) -> Tuple[bool, float]:
    """Check if there has been recent snowfall.
    
    Args:
        weather_history: Recent weather conditions
        hours: Number of hours to look back
    
    Returns:
        Tuple of (has_snow, total_snowfall_cm)
    """
    if not weather_history:
        return False, 0.0
    
    recent = weather_history[-hours:] if len(weather_history) >= hours else weather_history
    total_snow = sum(w.snowfall for w in recent)
    
    return total_snow > 0.5, total_snow
