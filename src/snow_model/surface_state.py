"""Snow surface state modeling based on weather conditions."""

from src.models import SnowState, WeatherConditions, Piste, Aspect, TimeOfDay
from typing import List, Tuple, Union
from datetime import datetime, time


def determine_snow_state(
    piste: Piste,
    weather: WeatherConditions,
    time_of_day: Union[TimeOfDay, str],
    recent_weather: List[WeatherConditions]
) -> SnowState:
    """Determine snow surface state for a piste at a given time.
    
    Args:
        piste: The piste to evaluate
        weather: Current weather conditions
        time_of_day: TimeOfDay enum or string ("morning", "late_morning", "afternoon")
        recent_weather: Weather conditions from the past 24 hours
    
    Returns:
        SnowState enum value
    """
    # Convert TimeOfDay enum to string if needed
    if isinstance(time_of_day, TimeOfDay):
        time_of_day = time_of_day.value
    # Get overnight conditions (last 8 hours from midnight to 8am)
    overnight_temps = [w.temperature for w in recent_weather[-16:-8]] if len(recent_weather) >= 16 else []
    overnight_snow = sum(w.snowfall for w in recent_weather[-16:-8]) if len(recent_weather) >= 16 else 0
    
    # Get recent conditions (last 4 hours)
    recent_temps = [w.temperature for w in recent_weather[-4:]] if len(recent_weather) >= 4 else [weather.temperature]
    recent_rain = sum(w.rainfall for w in recent_weather[-4:]) if len(recent_weather) >= 4 else weather.rainfall
    
    current_temp = weather.temperature
    altitude = piste.altitude_mid
    
    # Adjust temperature for altitude (roughly -0.65°C per 100m)
    temp_at_piste = current_temp - (altitude - 2000) * 0.0065
    
    # Check for rain-on-snow (instant degradation)
    if recent_rain > 0.5 and temp_at_piste > 0:
        return SnowState.SLUSHY
    
    # Check for fresh overnight snow
    if overnight_snow > 2:  # cm
        if temp_at_piste < -5:
            return SnowState.PACKED_POWDER
        elif temp_at_piste < 0:
            return SnowState.FIRM_GROOMED
    
    # Check for overnight refreeze
    avg_overnight_temp = sum(overnight_temps) / len(overnight_temps) if overnight_temps else temp_at_piste
    had_refreeze = avg_overnight_temp < -2
    
    # Morning conditions after good refreeze
    if time_of_day == "morning" and had_refreeze and piste.groomed:
        return SnowState.FIRM_GROOMED
    
    # Check sun exposure and time of day
    sun_exposed = is_sun_exposed(piste.aspect, time_of_day)
    
    # Afternoon with sun exposure and warm temps
    if time_of_day == "afternoon" and sun_exposed and temp_at_piste > 2:
        return SnowState.SLUSHY
    
    # Late morning with some warming
    if time_of_day == "late_morning" and temp_at_piste > 0 and sun_exposed:
        return SnowState.SOFT
    
    # Cold conditions generally stay firm
    if temp_at_piste < -5:
        if had_refreeze or piste.groomed:
            return SnowState.FIRM_GROOMED
        else:
            return SnowState.PACKED_POWDER
    
    # Freezing conditions
    if temp_at_piste < -1:
        return SnowState.FIRM_GROOMED if piste.groomed else SnowState.ICY
    
    # Marginal conditions
    if temp_at_piste < 2:
        return SnowState.SOFT if time_of_day == "morning" else SnowState.SLUSHY
    
    # Warm conditions
    return SnowState.SLUSHY


def is_sun_exposed(aspect: Aspect, time_of_day: Union[TimeOfDay, str]) -> bool:
    """Determine if a slope aspect receives significant sun at a time of day.
    
    Args:
        aspect: Slope aspect (direction it faces)
        time_of_day: TimeOfDay enum or string ("morning", "late_morning", "afternoon")
    
    Returns:
        True if slope receives significant sun exposure
    """
    # Convert TimeOfDay enum to string if needed
    if isinstance(time_of_day, TimeOfDay):
        time_of_day = time_of_day.value
    # Morning sun: East-facing slopes
    if time_of_day == "morning":
        return aspect in [Aspect.E, Aspect.NE, Aspect.SE]
    
    # Late morning to afternoon: South and West facing slopes
    if time_of_day == "late_morning":
        return aspect in [Aspect.S, Aspect.SE, Aspect.SW, Aspect.E]
    
    # Afternoon: South and West facing slopes
    if time_of_day == "afternoon":
        return aspect in [Aspect.S, Aspect.SW, Aspect.W, Aspect.SE]
    
    return False


def get_sun_exposure_factor(aspect: Aspect, time_of_day: Union[TimeOfDay, str]) -> float:
    """Get a numerical sun exposure factor (0-1).
    
    Higher values mean more sun exposure which can degrade snow quality
    in warm conditions but improve it in cold conditions.
    
    Args:
        aspect: Slope aspect (direction it faces)
        time_of_day: TimeOfDay enum or string ("morning", "late_morning", "afternoon")
    
    Returns:
        Exposure factor from 0 (no sun) to 1 (full sun)
    """
    # Convert TimeOfDay enum to string if needed
    if isinstance(time_of_day, TimeOfDay):
        time_of_day = time_of_day.value
    exposure_map = {
        "morning": {
            Aspect.E: 1.0,
            Aspect.NE: 0.7,
            Aspect.SE: 0.7,
            Aspect.N: 0.0,
            Aspect.S: 0.3,
            Aspect.W: 0.0,
            Aspect.NW: 0.0,
            Aspect.SW: 0.0,
            Aspect.FLAT: 0.5,
        },
        "late_morning": {
            Aspect.S: 1.0,
            Aspect.SE: 0.9,
            Aspect.SW: 0.8,
            Aspect.E: 0.6,
            Aspect.W: 0.3,
            Aspect.NE: 0.3,
            Aspect.N: 0.0,
            Aspect.NW: 0.0,
            Aspect.FLAT: 0.7,
        },
        "afternoon": {
            Aspect.SW: 1.0,
            Aspect.W: 0.9,
            Aspect.S: 0.8,
            Aspect.SE: 0.5,
            Aspect.NW: 0.3,
            Aspect.E: 0.0,
            Aspect.N: 0.0,
            Aspect.NE: 0.0,
            Aspect.FLAT: 0.6,
        },
    }
    
    return exposure_map.get(time_of_day, {}).get(aspect, 0.5)
