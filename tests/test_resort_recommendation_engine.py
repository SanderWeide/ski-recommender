"""Tests for the resort recommendation engine."""

import pytest
from datetime import datetime, timedelta
from src.models import (
    Resort, Piste, WeatherConditions, SkierProfile,
    Difficulty, Aspect, SkillLevel
)
from src.recommendation.resort_engine import ResortRecommendationEngine


# Fixed date for deterministic tests
TEST_DATE = datetime(2024, 1, 15, 0, 0, 0, 0)


def create_test_resorts():
    """Create multiple test resorts with sample pistes."""
    resort1 = Resort(
        id="test_resort_1",
        name="Test Resort 1",
        country="Test",
        latitude=45.0,
        longitude=7.0,
        pistes=[
            Piste(
                id="r1_p1",
                name="Easy Green",
                difficulty=Difficulty.GREEN,
                altitude_min=2000,
                altitude_max=2200,
                aspect=Aspect.N,
                groomed=True,
            ),
            Piste(
                id="r1_p2",
                name="Blue Run",
                difficulty=Difficulty.BLUE,
                altitude_min=2200,
                altitude_max=2500,
                aspect=Aspect.E,
                groomed=True,
            ),
            Piste(
                id="r1_p3",
                name="Red Challenge",
                difficulty=Difficulty.RED,
                altitude_min=2500,
                altitude_max=2800,
                aspect=Aspect.S,
                groomed=True,
            ),
        ],
    )
    
    resort2 = Resort(
        id="test_resort_2",
        name="Test Resort 2",
        country="Test",
        latitude=46.0,
        longitude=8.0,
        pistes=[
            Piste(
                id="r2_p1",
                name="Mountain Blue",
                difficulty=Difficulty.BLUE,
                altitude_min=2400,
                altitude_max=2700,
                aspect=Aspect.N,
                groomed=True,
            ),
            Piste(
                id="r2_p2",
                name="Peak Red",
                difficulty=Difficulty.RED,
                altitude_min=2700,
                altitude_max=3000,
                aspect=Aspect.NE,
                groomed=True,
            ),
        ],
    )
    
    return [resort1, resort2]


def create_test_weather(days=7):
    """Create test weather forecast."""
    weather = []
    start = TEST_DATE
    
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


def test_resort_recommendation_engine_creation():
    """Test creating a resort recommendation engine."""
    resorts = create_test_resorts()
    weather1 = create_test_weather()
    weather2 = create_test_weather()
    
    weather_forecasts = {
        "test_resort_1": weather1,
        "test_resort_2": weather2,
    }
    
    engine = ResortRecommendationEngine(resorts, weather_forecasts)
    
    assert len(engine.resorts) == 2
    assert len(engine.weather_forecasts) == 2


def test_generate_resort_recommendations():
    """Test generating resort recommendations."""
    resorts = create_test_resorts()
    weather1 = create_test_weather(days=3)
    weather2 = create_test_weather(days=3)
    
    weather_forecasts = {
        "test_resort_1": weather1,
        "test_resort_2": weather2,
    }
    
    engine = ResortRecommendationEngine(resorts, weather_forecasts)
    
    profile = SkierProfile(skill_level=SkillLevel.INTERMEDIATE)
    start_date = TEST_DATE
    
    recommendations = engine.generate_resort_recommendations(
        skier_profile=profile,
        start_date=start_date,
        days=3,
        top_n_resorts=2,
        top_n_pistes=3,
    )
    
    assert len(recommendations) > 0
    
    # Check recommendation structure
    for rec in recommendations:
        assert rec.date
        assert rec.time_of_day
        assert rec.confidence in ["high", "medium", "low"]
        assert isinstance(rec.recommendations, list)
        
        # Check resort scores
        for resort_score in rec.recommendations:
            assert resort_score.resort
            assert 0 <= resort_score.score <= 100
            assert resort_score.num_suitable_pistes >= 0
            assert resort_score.snow_summary
            assert resort_score.explanation
            assert isinstance(resort_score.best_piste_scores, list)


def test_resort_recommendations_ranked_by_score():
    """Test that resorts are ranked by score."""
    resorts = create_test_resorts()
    weather1 = create_test_weather(days=1)
    weather2 = create_test_weather(days=1)
    
    weather_forecasts = {
        "test_resort_1": weather1,
        "test_resort_2": weather2,
    }
    
    engine = ResortRecommendationEngine(resorts, weather_forecasts)
    
    profile = SkierProfile(skill_level=SkillLevel.INTERMEDIATE)
    start_date = TEST_DATE
    
    recommendations = engine.generate_resort_recommendations(
        skier_profile=profile,
        start_date=start_date,
        days=1,
        top_n_resorts=2,
        top_n_pistes=3,
    )
    
    # Check that recommendations are sorted by score
    for rec in recommendations:
        scores = [rs.score for rs in rec.recommendations]
        assert scores == sorted(scores, reverse=True)


def test_resort_recommendations_top_n_limit():
    """Test that only top N resorts are returned."""
    resorts = create_test_resorts()
    weather1 = create_test_weather(days=1)
    weather2 = create_test_weather(days=1)
    
    weather_forecasts = {
        "test_resort_1": weather1,
        "test_resort_2": weather2,
    }
    
    engine = ResortRecommendationEngine(resorts, weather_forecasts)
    
    profile = SkierProfile(skill_level=SkillLevel.INTERMEDIATE)
    start_date = TEST_DATE
    
    recommendations = engine.generate_resort_recommendations(
        skier_profile=profile,
        start_date=start_date,
        days=1,
        top_n_resorts=1,  # Only top 1
        top_n_pistes=3,
    )
    
    # Check that at most 1 resort per time block
    for rec in recommendations:
        assert len(rec.recommendations) <= 1


def test_resort_recommendations_include_piste_details():
    """Test that resort scores include top piste information."""
    resorts = create_test_resorts()
    weather1 = create_test_weather(days=1)
    weather2 = create_test_weather(days=1)
    
    weather_forecasts = {
        "test_resort_1": weather1,
        "test_resort_2": weather2,
    }
    
    engine = ResortRecommendationEngine(resorts, weather_forecasts)
    
    profile = SkierProfile(skill_level=SkillLevel.INTERMEDIATE)
    start_date = TEST_DATE
    
    recommendations = engine.generate_resort_recommendations(
        skier_profile=profile,
        start_date=start_date,
        days=1,
        top_n_resorts=2,
        top_n_pistes=2,
    )
    
    # Check that resort scores include piste information
    for rec in recommendations:
        for resort_score in rec.recommendations:
            # Should have at most top_n_pistes
            assert len(resort_score.best_piste_scores) <= 2
            
            # Piste scores should be sorted by score
            piste_scores = [ps.score for ps in resort_score.best_piste_scores]
            assert piste_scores == sorted(piste_scores, reverse=True)
