"""Tests for resort data."""

import pytest
from src.data.resorts import get_resort, list_resorts, get_sample_pistes
from src.models import Difficulty


def test_list_resorts():
    """Test listing all resorts."""
    resorts = list_resorts()
    
    assert len(resorts) == 7
    assert any(r['id'] == 'val_thorens' for r in resorts)
    assert any(r['id'] == 'zermatt' for r in resorts)
    assert any(r['id'] == 'silvretta_arena' for r in resorts)


def test_get_resort():
    """Test getting a specific resort."""
    resort = get_resort("val_thorens")
    
    assert resort.name == "Val Thorens"
    assert resort.country == "France"
    assert resort.latitude == 45.2974
    assert len(resort.pistes) > 0


def test_get_resort_invalid():
    """Test getting an invalid resort."""
    with pytest.raises(ValueError):
        get_resort("invalid_resort")


def test_sample_pistes():
    """Test that sample pistes have required attributes."""
    pistes = get_sample_pistes("val_thorens")
    
    assert len(pistes) > 0
    
    for piste in pistes:
        assert piste.name
        assert piste.id
        assert piste.difficulty in [Difficulty.GREEN, Difficulty.BLUE, Difficulty.RED, Difficulty.BLACK]
        assert piste.altitude_min < piste.altitude_max
        assert piste.altitude_min > 0
