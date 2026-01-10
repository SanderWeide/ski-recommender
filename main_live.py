#!/usr/bin/env python3
"""CLI for ski piste recommendations using live API data."""

import sys
from datetime import datetime
from src.models import SkierProfile, SkillLevel, Difficulty, TimeOfDay
from src.data.resorts import get_resort, list_resorts
from src.services.open_meteo import get_weather_forecast
from src.recommendation.engine import RecommendationEngine
from src.recommendation.formatter import format_recommendations_text, format_recommendations_json


def main():
    """Main CLI entry point with live data."""
    print("🎿 Ski Piste Recommender (Live API Data Mode)\n")
    
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
    
    # Fetch live weather forecast
    print("Fetching live weather forecast from Open-Meteo API...")
    try:
        weather_forecast = get_weather_forecast(
            resort.latitude,
            resort.longitude,
            days=7
        )
        print(f"Fetched {len(weather_forecast)} hourly forecasts\n")
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        print("Falling back to mock data...\n")
        from main import generate_mock_weather
        weather_forecast = generate_mock_weather(days=7)
    
    if not weather_forecast:
        print("Error: No weather data available")
        return 1
    
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
