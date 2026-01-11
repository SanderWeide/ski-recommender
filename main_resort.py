#!/usr/bin/env python3
"""CLI for ski resort recommendations (comparing multiple resorts)."""

import sys
from datetime import datetime, timedelta
from src.models import SkierProfile, SkillLevel, WeatherConditions
from src.data.resorts import get_resort, list_resorts
from src.recommendation.resort_engine import ResortRecommendationEngine
from src.recommendation.formatter import (
    format_resort_recommendations_text, format_resort_recommendations_json,
    format_daily_resort_recommendations_text, format_daily_resort_recommendations_json,
    format_weekly_resort_recommendation_text, format_weekly_resort_recommendation_json
)


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
    print("🎿 Ski Resort Recommender (Resort Comparison Mode)\n")
    
    # Show available resorts
    resorts_info = list_resorts()
    print("Available resorts:")
    for i, resort in enumerate(resorts_info, 1):
        print(f"  {i}. {resort['name']} ({resort['country']})")
    
    print()
    
    # Get resort selection (can be multiple or 'all')
    if len(sys.argv) > 1:
        resort_selection = sys.argv[1].lower()
    else:
        resort_selection = "all"  # Default: compare all resorts
    
    # Load resorts
    resorts = []
    weather_forecasts = {}
    
    if resort_selection == "all":
        print("Comparing all resorts...\n")
        for resort_info in resorts_info:
            try:
                resort = get_resort(resort_info['id'])
                resorts.append(resort)
                # Generate mock weather for each resort
                weather_forecasts[resort.id] = generate_mock_weather(days=7)
            except ValueError as e:
                print(f"Warning: Could not load {resort_info['id']}: {e}")
    else:
        # Load specific resorts (comma-separated)
        resort_ids = [r.strip() for r in resort_selection.split(',')]
        print(f"Comparing resorts: {', '.join(resort_ids)}\n")
        
        for resort_id in resort_ids:
            try:
                resort = get_resort(resort_id)
                resorts.append(resort)
                weather_forecasts[resort.id] = generate_mock_weather(days=7)
            except ValueError as e:
                print(f"Error: Unknown resort '{resort_id}'")
                print(f"Available: {', '.join([r['id'] for r in resorts_info])}")
                return 1
    
    if not resorts:
        print("Error: No resorts loaded")
        return 1
    
    print(f"Loaded {len(resorts)} resort(s):")
    for resort in resorts:
        print(f"  - {resort.name} ({resort.country}): {len(resort.pistes)} pistes")
    print()
    
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
    
    # Create skier profile
    skier_profile = SkierProfile(
        skill_level=skill_level,
        preferred_difficulty=None,
        preferred_time=None,
    )
    
    # Get mode (time blocks, daily, or weekly)
    mode = "time_blocks"  # Default
    output_format = "text"  # Default
    
    # Parse remaining arguments
    if len(sys.argv) > 3:
        # Check if argument is a mode or output format
        arg3 = sys.argv[3].lower()
        if arg3 in ["daily", "time_blocks", "weekly"]:
            mode = arg3
            output_format = sys.argv[4].lower() if len(sys.argv) > 4 else "text"
        else:
            output_format = arg3
    
    # Generate recommendations
    engine = ResortRecommendationEngine(resorts, weather_forecasts)
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if mode == "weekly":
        print("Generating weekly resort recommendation (7-day aggregation)...\n")
        recommendation = engine.generate_weekly_resort_recommendations(
            skier_profile=skier_profile,
            start_date=start_date,
            top_n_resorts=min(5, len(resorts)),  # Show top N or all if fewer
            top_n_pistes=3,  # Show top 3 pistes per resort
        )
        
        if output_format == "json":
            output = format_weekly_resort_recommendation_json(recommendation)
            print(output)
        else:
            output = format_weekly_resort_recommendation_text(recommendation)
            print(output)
    elif mode == "daily":
        print("Generating daily resort recommendations (24-hour aggregation)...\n")
        recommendations = engine.generate_daily_resort_recommendations(
            skier_profile=skier_profile,
            start_date=start_date,
            days=7,
            top_n_resorts=min(5, len(resorts)),  # Show top N or all if fewer
            top_n_pistes=3,  # Show top 3 pistes per resort
        )
        
        if output_format == "json":
            output = format_daily_resort_recommendations_json(recommendations)
            print(output)
        else:
            output = format_daily_resort_recommendations_text(recommendations)
            print(output)
    else:
        print("Generating resort recommendations by time blocks...\n")
        recommendations = engine.generate_resort_recommendations(
            skier_profile=skier_profile,
            start_date=start_date,
            days=7,
            top_n_resorts=min(5, len(resorts)),  # Show top N or all if fewer
            top_n_pistes=3,  # Show top 3 pistes per resort
        )
        
        if output_format == "json":
            output = format_resort_recommendations_json(recommendations)
            print(output)
        else:
            output = format_resort_recommendations_text(recommendations)
            print(output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
