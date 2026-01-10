"""Tests for core models."""

import pytest
from datetime import datetime
from src.models import (
    Piste, Difficulty, Aspect, SkillLevel,
    WeatherConditions, SkierProfile, SnowState
)


def test_piste_creation():
    """Test creating a piste."""
    piste = Piste(
        id="test_1",
        name="Test Piste",
        difficulty=Difficulty.BLUE,
        altitude_min=2000,
        altitude_max=2500,
        aspect=Aspect.N,
        groomed=True,
        snowmaking=True,
    )
    
    assert piste.name == "Test Piste"
    assert piste.difficulty == Difficulty.BLUE
    assert piste.altitude_mid == 2250


def test_weather_conditions():
    """Test weather conditions model."""
    weather = WeatherConditions(
        timestamp=datetime.now(),
        temperature=-5.0,
        snowfall=2.0,
        rainfall=0.0,
        wind_speed=10.0,
        wind_direction=270.0,
        cloud_cover=50.0,
        freezing_level=0.0,
    )
    
    assert weather.temperature == -5.0
    assert weather.snowfall == 2.0


def test_skier_profile():
    """Test skier profile."""
    profile = SkierProfile(
        skill_level=SkillLevel.INTERMEDIATE,
        preferred_difficulty=Difficulty.RED,
    )
    
    assert profile.skill_level == SkillLevel.INTERMEDIATE
    assert profile.preferred_difficulty == Difficulty.RED
