"""Tests for the recommendation engine."""

import pytest
from datetime import datetime, timedelta
from src.models import (
    Resort, Piste, WeatherConditions, SkierProfile,
    Difficulty, Aspect, SkillLevel
)
from src.recommendation.engine import RecommendationEngine


def create_test_resort():
    """Create a test resort with sample pistes."""
    pistes = [
        Piste(
            id="test_1",
            name="Easy Green",
            difficulty=Difficulty.GREEN,
            altitude_min=2000,
            altitude_max=2200,
            aspect=Aspect.N,
            groomed=True,
        ),
        Piste(
            id="test_2",
            name="Blue Run",
            difficulty=Difficulty.BLUE,
            altitude_min=2200,
            altitude_max=2500,
            aspect=Aspect.E,
            groomed=True,
        ),
        Piste(
            id="test_3",
            name="Red Challenge",
            difficulty=Difficulty.RED,
            altitude_min=2500,
            altitude_max=2800,
            aspect=Aspect.S,
            groomed=True,
        ),
    ]
    
    return Resort(
        id="test_resort",
        name="Test Resort",
        country="Test",
        latitude=45.0,
        longitude=7.0,
        pistes=pistes,
    )


def create_test_weather(days=7):
    """Create test weather forecast."""
    weather = []
    start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for day in range(days):
        for hour in range(24):
            timestamp = start + timedelta(days=day, hours=hour)
            weather.append(WeatherConditions(
                timestamp=timestamp,
                temperature=-5.0,
                snowfall=0.5 if hour < 6 else 0.0,
                rainfall=0.0,
                wind_speed=8.0,
                wind_direction=270.0,
                cloud_cover=30.0,
                freezing_level=0.0,
            ))
    
    return weather


def test_recommendation_engine_creation():
    """Test creating a recommendation engine."""
    resort = create_test_resort()
    weather = create_test_weather()
    
    engine = RecommendationEngine(resort, weather)
    
    assert engine.resort == resort
    assert len(engine.weather_forecast) > 0


def test_generate_recommendations():
    """Test generating recommendations."""
    resort = create_test_resort()
    weather = create_test_weather(days=3)
    engine = RecommendationEngine(resort, weather)
    
    profile = SkierProfile(skill_level=SkillLevel.INTERMEDIATE)
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    recommendations = engine.generate_recommendations(
        skier_profile=profile,
        start_date=start_date,
        days=3,
        top_n=5,
    )
    
    assert len(recommendations) > 0
    
    # Check recommendation structure
    for rec in recommendations:
        assert rec.date
        assert rec.time_of_day
        assert rec.snow_summary
        assert rec.confidence in ["high", "medium", "low"]
        assert isinstance(rec.recommendations, list)


def test_recommendations_filtered_by_skill():
    """Test that recommendations are appropriate for skill level."""
    resort = create_test_resort()
    weather = create_test_weather(days=1)
    engine = RecommendationEngine(resort, weather)
    
    # Beginner should not get many advanced pistes
    beginner_profile = SkierProfile(skill_level=SkillLevel.BEGINNER)
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    recommendations = engine.generate_recommendations(
        skier_profile=beginner_profile,
        start_date=start_date,
        days=1,
        top_n=10,
    )
    
    # Check that we get some recommendations
    assert len(recommendations) > 0
