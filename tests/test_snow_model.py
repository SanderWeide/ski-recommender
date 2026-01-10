"""Tests for snow surface state modeling."""

import pytest
from datetime import datetime
from src.models import Piste, WeatherConditions, Aspect, Difficulty, SnowState
from src.snow_model.surface_state import (
    determine_snow_state, is_sun_exposed, get_sun_exposure_factor
)


def test_is_sun_exposed():
    """Test sun exposure determination."""
    # Morning: East-facing gets sun
    assert is_sun_exposed(Aspect.E, "morning")
    assert not is_sun_exposed(Aspect.W, "morning")
    
    # Afternoon: West-facing gets sun
    assert is_sun_exposed(Aspect.W, "afternoon")
    assert not is_sun_exposed(Aspect.N, "afternoon")


def test_sun_exposure_factor():
    """Test sun exposure factor calculation."""
    # Morning: East should have high factor
    factor = get_sun_exposure_factor(Aspect.E, "morning")
    assert factor > 0.8
    
    # Morning: West should have low factor
    factor = get_sun_exposure_factor(Aspect.W, "morning")
    assert factor < 0.3


def test_determine_snow_state_cold_morning():
    """Test snow state in cold morning conditions."""
    piste = Piste(
        id="test",
        name="Test",
        difficulty=Difficulty.BLUE,
        altitude_min=2500,
        altitude_max=2700,
        aspect=Aspect.N,
        groomed=True,
    )
    
    current = WeatherConditions(
        timestamp=datetime.now(),
        temperature=-8.0,
        snowfall=0.0,
        rainfall=0.0,
        wind_speed=5.0,
        wind_direction=270.0,
        cloud_cover=30.0,
        freezing_level=0.0,
    )
    
    # Create cold overnight conditions
    recent = [
        WeatherConditions(
            timestamp=datetime.now(),
            temperature=-10.0,
            snowfall=0.5,
            rainfall=0.0,
            wind_speed=5.0,
            wind_direction=270.0,
            cloud_cover=30.0,
            freezing_level=0.0,
        ) for _ in range(24)
    ]
    
    state = determine_snow_state(piste, current, "morning", recent)
    
    # Cold groomed morning should be firm or packed powder
    assert state in [SnowState.FIRM_GROOMED, SnowState.PACKED_POWDER]


def test_determine_snow_state_warm_afternoon():
    """Test snow state in warm afternoon conditions."""
    piste = Piste(
        id="test",
        name="Test",
        difficulty=Difficulty.BLUE,
        altitude_min=2000,
        altitude_max=2200,
        aspect=Aspect.S,  # South-facing, sun-exposed
        groomed=True,
    )
    
    current = WeatherConditions(
        timestamp=datetime.now(),
        temperature=5.0,  # Warm
        snowfall=0.0,
        rainfall=0.0,
        wind_speed=5.0,
        wind_direction=270.0,
        cloud_cover=30.0,
        freezing_level=750.0,
    )
    
    recent = [current] * 24
    
    state = determine_snow_state(piste, current, "afternoon", recent)
    
    # Warm sunny afternoon should be soft or slushy
    assert state in [SnowState.SOFT, SnowState.SLUSHY]
