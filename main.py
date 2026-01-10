#!/usr/bin/env python3
"""CLI for ski piste recommendations using mock weather data."""

import sys
from datetime import datetime, timedelta
from src.models import SkierProfile, SkillLevel, Difficulty, TimeOfDay, WeatherConditions
from src.data.resorts import get_resort, list_resorts
from src.recommendation.engine import RecommendationEngine
from src.recommendation.formatter import format_recommendations_text, format_recommendations_json


def generate_mock_weather(days: int = 7) -> list:
    """Generate mock weather data for testing."""
    conditions = []
    start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for day in range(days):
        for hour in range(24):
            timestamp = start + timedelta(days=day, hours=hour)
            
            # Pattern: cold clear mornings, warming afternoons
            if hour < 6:
                temp = -8
                snowfall = 0.5  # Light overnight snow
            elif hour < 12:
                temp = -5 + (hour - 6) * 0.8
                snowfall = 0.0
            elif hour < 18:
                temp = -2 + (hour - 12) * 0.5
                snowfall = 0.0
            else:
                temp = max(-8, -2 - (hour - 18) * 1.0)
                snowfall = 0.0
            
            conditions.append(WeatherConditions(
                timestamp=timestamp,
                temperature=temp,
                snowfall=snowfall,
                rainfall=0.0,
                wind_speed=8.0,
                wind_direction=270.0,
                cloud_cover=30.0,
                freezing_level=max(0, temp * 150),
            ))
    
    return conditions


def main():
    """Main CLI entry point."""
    print("🎿 Ski Piste Recommender (Mock Data Mode)\n")
    
    # Show available resorts
    resorts = list_resorts()
    print("Available resorts:")
    for i, resort in enumerate(resorts, 1):
        print(f"  {i}. {resort['name']} ({resort['country']})")
    
    print()
    
    # Get resort selection
    if len(sys.argv) > 1:
        resort_id = sys.argv[1]
    else:
        resort_id = "val_thorens"  # Default
    
    try:
        resort = get_resort(resort_id)
    except ValueError:
        print(f"Error: Unknown resort '{resort_id}'")
        print(f"Available: {', '.join([r['id'] for r in resorts])}")
        return 1
    
    print(f"Selected resort: {resort.name} ({resort.country})")
    print(f"Location: {resort.latitude:.4f}, {resort.longitude:.4f}")
    print(f"Number of pistes: {len(resort.pistes)}\n")
    
    # Get skill level
    if len(sys.argv) > 2:
        skill_input = sys.argv[2].lower()
    else:
        skill_input = "intermediate"  # Default
    
    skill_map = {
        "beginner": SkillLevel.BEGINNER,
        "intermediate": SkillLevel.INTERMEDIATE,
        "advanced": SkillLevel.ADVANCED,
    }
    
    skill_level = skill_map.get(skill_input, SkillLevel.INTERMEDIATE)
    print(f"Skill level: {skill_level.value}\n")
    
    # Generate mock weather
    print("Generating mock weather forecast...")
    weather_forecast = generate_mock_weather(days=7)
    print(f"Generated {len(weather_forecast)} hourly forecasts\n")
    
    # Create skier profile
    skier_profile = SkierProfile(
        skill_level=skill_level,
        preferred_difficulty=None,
        preferred_time=None,
    )
    
    # Generate recommendations
    print("Generating recommendations...\n")
    engine = RecommendationEngine(resort, weather_forecast)
    
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    recommendations = engine.generate_recommendations(
        skier_profile=skier_profile,
        start_date=start_date,
        days=7,
        top_n=5,
    )
    
    # Output format
    output_format = sys.argv[3] if len(sys.argv) > 3 else "text"
    
    if output_format == "json":
        output = format_recommendations_json(recommendations, resort.name)
        print(output)
    else:
        output = format_recommendations_text(recommendations, resort.name)
        print(output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
