"""Piste scoring engine - assigns numerical scores (0-100) to pistes."""

from src.models import (
    Piste, WeatherConditions, SnowState, SkillLevel, 
    Difficulty, TimeOfDay, Aspect
)
from src.snow_model.surface_state import (
    determine_snow_state, get_sun_exposure_factor
)
from src.snow_model.freeze_thaw import evaluate_overnight_refreeze
from typing import List, Tuple


# Skill level to difficulty mapping
SKILL_DIFFICULTY_MAP = {
    SkillLevel.BEGINNER: [Difficulty.GREEN, Difficulty.BLUE],
    SkillLevel.INTERMEDIATE: [Difficulty.GREEN, Difficulty.BLUE, Difficulty.RED],
    SkillLevel.ADVANCED: [Difficulty.BLUE, Difficulty.RED, Difficulty.BLACK],
}


def score_piste(
    piste: Piste,
    weather: WeatherConditions,
    time_of_day: TimeOfDay,
    recent_weather: List[WeatherConditions],
    skill_level: SkillLevel,
) -> Tuple[float, SnowState, str]:
    """Score a piste for given conditions.
    
    Args:
        piste: The piste to score
        weather: Current weather conditions
        time_of_day: Time block
        recent_weather: Weather history for context
        skill_level: Skier skill level
    
    Returns:
        Tuple of (score 0-100, snow_state, explanation)
    """
    # Determine snow state
    snow_state = determine_snow_state(
        piste, weather, time_of_day.value, recent_weather
    )
    
    # Base score from snow state
    base_score = get_base_score_from_snow_state(snow_state)
    
    # Altitude bonus (higher is generally better, more reliable snow)
    altitude_factor = 1.0 + (piste.altitude_mid - 2000) / 4000
    altitude_factor = max(0.8, min(1.2, altitude_factor))
    
    # Grooming bonus
    grooming_bonus = 10 if piste.groomed else -10
    
    # Wind penalty
    wind_penalty = calculate_wind_penalty(weather.wind_speed, piste.altitude_mid)
    
    # Temperature adjustment
    temp_at_piste = weather.temperature - (piste.altitude_mid - 2000) * 0.0065
    temp_factor = calculate_temp_factor(temp_at_piste, time_of_day)
    
    # Overnight refreeze quality
    overnight = recent_weather[-16:-8] if len(recent_weather) >= 16 else []
    refreeze_quality, refreeze_score = evaluate_overnight_refreeze(overnight)
    refreeze_bonus = refreeze_score * 15 if time_of_day == TimeOfDay.MORNING else refreeze_score * 5
    
    # Sun exposure - can be good or bad depending on conditions
    sun_factor = get_sun_exposure_factor(piste.aspect, time_of_day.value)
    if temp_at_piste > 2:
        # Warm: sun is bad (melting)
        sun_adjustment = -sun_factor * 15
    elif temp_at_piste < -5:
        # Cold: sun can help soften firm snow slightly
        sun_adjustment = sun_factor * 5
    else:
        # Moderate: neutral to slightly positive
        sun_adjustment = sun_factor * 2
    
    # Difficulty match with skill level
    difficulty_match = calculate_difficulty_match(piste.difficulty, skill_level)
    
    # Fresh snow bonus
    recent_snow = sum(w.snowfall for w in recent_weather[-12:]) if len(recent_weather) >= 12 else 0
    snow_bonus = min(15, recent_snow * 3) if recent_snow > 1 else 0
    
    # Rain penalty
    recent_rain = sum(w.rainfall for w in recent_weather[-4:]) if len(recent_weather) >= 4 else 0
    rain_penalty = -min(30, recent_rain * 20) if recent_rain > 0.1 else 0
    
    # Calculate final score
    score = (
        base_score * altitude_factor * temp_factor * difficulty_match
        + grooming_bonus
        + wind_penalty
        + refreeze_bonus
        + sun_adjustment
        + snow_bonus
        + rain_penalty
    )
    
    # Clamp to 0-100
    score = max(0, min(100, score))
    
    # Generate explanation
    explanation = generate_explanation(
        piste, snow_state, time_of_day, temp_at_piste, 
        refreeze_quality, sun_factor, recent_snow, recent_rain,
        weather.wind_speed
    )
    
    return score, snow_state, explanation


def get_base_score_from_snow_state(snow_state: SnowState) -> float:
    """Get base score from snow surface state."""
    return {
        SnowState.FIRM_GROOMED: 80,
        SnowState.PACKED_POWDER: 85,
        SnowState.SOFT: 75,
        SnowState.ICY: 40,
        SnowState.SLUSHY: 45,
    }[snow_state]


def calculate_wind_penalty(wind_speed: float, altitude: int) -> float:
    """Calculate penalty for wind exposure.
    
    Higher altitudes are more exposed to wind.
    """
    exposure_factor = 1.0 + (altitude - 2000) / 2000
    wind_penalty = -min(20, wind_speed * exposure_factor)
    return wind_penalty


def calculate_temp_factor(temp: float, time_of_day: TimeOfDay) -> float:
    """Calculate temperature factor (multiplier 0.7-1.1).
    
    Ideal temps are around -5 to 0°C depending on time of day.
    """
    if time_of_day == TimeOfDay.MORNING:
        # Morning: prefer cold firm snow
        if -8 <= temp <= -2:
            return 1.1
        elif -10 <= temp <= 2:
            return 1.0
        else:
            return 0.85
    elif time_of_day == TimeOfDay.LATE_MORNING:
        # Late morning: moderate temps ok
        if -5 <= temp <= 0:
            return 1.1
        elif -8 <= temp <= 3:
            return 1.0
        else:
            return 0.85
    else:  # AFTERNOON
        # Afternoon: some warmth is ok but not too much
        if -3 <= temp <= 2:
            return 1.0
        elif -6 <= temp <= 5:
            return 0.9
        else:
            return 0.8


def calculate_difficulty_match(difficulty: Difficulty, skill_level: SkillLevel) -> float:
    """Calculate how well piste difficulty matches skill level.
    
    Returns multiplier (0.5-1.0).
    """
    suitable_difficulties = SKILL_DIFFICULTY_MAP[skill_level]
    
    if difficulty in suitable_difficulties:
        return 1.0
    else:
        return 0.6  # Still include but lower score


def generate_explanation(
    piste: Piste,
    snow_state: SnowState,
    time_of_day: TimeOfDay,
    temp: float,
    refreeze_quality: str,
    sun_factor: float,
    recent_snow: float,
    recent_rain: float,
    wind_speed: float,
) -> str:
    """Generate human-readable explanation for the score."""
    parts = []
    
    # Aspect and altitude
    parts.append(f"{piste.aspect.value}-facing {piste.difficulty.value} piste")
    
    if piste.altitude_mid > 2800:
        parts.append("high altitude")
    elif piste.altitude_mid > 2300:
        parts.append("mid-altitude")
    else:
        parts.append("lower altitude")
    
    # Snow condition
    snow_desc = {
        SnowState.FIRM_GROOMED: "firm, grippy snow",
        SnowState.PACKED_POWDER: "packed powder",
        SnowState.SOFT: "soft snow",
        SnowState.ICY: "icy conditions",
        SnowState.SLUSHY: "slushy snow",
    }[snow_state]
    
    # Time context
    if time_of_day == TimeOfDay.MORNING:
        if refreeze_quality in ["excellent", "good"]:
            parts.append(f"cold overnight refreeze → {snow_desc}")
        else:
            parts.append(f"{snow_desc} this morning")
    elif time_of_day == TimeOfDay.LATE_MORNING:
        parts.append(f"{snow_desc}")
        if sun_factor > 0.6:
            parts.append("warming in sun")
    else:  # AFTERNOON
        if sun_factor > 0.6 and temp > 2:
            parts.append(f"{snow_desc}, softening in afternoon sun")
        else:
            parts.append(f"{snow_desc}")
    
    # Fresh snow
    if recent_snow > 2:
        parts.append(f"fresh snow ({recent_snow:.0f}cm)")
    
    # Rain
    if recent_rain > 0.5:
        parts.append("recent rain degraded conditions")
    
    # Wind
    if wind_speed > 15:
        parts.append("windy")
    
    # Grooming
    if piste.groomed:
        parts.append("groomed overnight")
    
    return ", ".join(parts) + "."
