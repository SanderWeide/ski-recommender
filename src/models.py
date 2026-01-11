"""Core data models for the ski recommender system."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


class SkillLevel(Enum):
    """Skier skill levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Difficulty(Enum):
    """Piste difficulty levels."""
    GREEN = "green"
    BLUE = "blue"
    RED = "red"
    BLACK = "black"


class Aspect(Enum):
    """Slope aspect (direction the slope faces)."""
    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"
    NW = "NW"
    FLAT = "FLAT"


class SnowState(Enum):
    """Snow surface state."""
    ICY = "icy"
    FIRM_GROOMED = "firm_groomed"
    PACKED_POWDER = "packed_powder"
    SOFT = "soft"
    SLUSHY = "slushy"


class TimeOfDay(Enum):
    """Time blocks for the day."""
    MORNING = "morning"  # 08:00-10:30
    LATE_MORNING = "late_morning"  # 10:30-12:30
    AFTERNOON = "afternoon"  # 12:30-16:00


@dataclass
class Piste:
    """Represents a ski piste."""
    id: str
    name: str
    difficulty: Difficulty
    altitude_min: int  # meters
    altitude_max: int  # meters
    aspect: Aspect
    groomed: bool = True
    snowmaking: bool = False
    
    @property
    def altitude_mid(self) -> int:
        """Get the mid-point altitude."""
        return (self.altitude_min + self.altitude_max) // 2


@dataclass
class WeatherConditions:
    """Weather conditions for a specific time."""
    timestamp: datetime
    temperature: float  # Celsius
    snowfall: float  # mm
    rainfall: float  # mm
    wind_speed: float  # m/s
    wind_direction: float  # degrees
    cloud_cover: float  # 0-100 %
    freezing_level: float  # meters


@dataclass
class SkierProfile:
    """User preferences and skill level."""
    skill_level: SkillLevel
    preferred_difficulty: Optional[Difficulty] = None
    preferred_time: Optional[TimeOfDay] = None


@dataclass
class PisteScore:
    """Score for a piste at a specific time."""
    piste: Piste
    score: float  # 0-100
    snow_state: SnowState
    explanation: str
    timestamp: datetime
    time_of_day: TimeOfDay


@dataclass
class DailyRecommendation:
    """Recommendations for a specific day and time block."""
    date: datetime
    time_of_day: TimeOfDay
    recommendations: List[PisteScore]
    snow_summary: str
    confidence: str  # "high", "medium", "low"


@dataclass
class Resort:
    """Represents a ski resort."""
    id: str
    name: str
    country: str
    latitude: float
    longitude: float
    pistes: List[Piste]


@dataclass
class ResortScore:
    """Score for a resort at a specific time."""
    resort: Resort
    score: float  # 0-100, aggregate score
    num_suitable_pistes: int
    best_piste_scores: List[PisteScore]  # Top pistes at the resort
    snow_summary: str
    explanation: str
    timestamp: datetime
    time_of_day: TimeOfDay


@dataclass
class ResortRecommendation:
    """Recommendations for resorts on a specific day and time block."""
    date: datetime
    time_of_day: TimeOfDay
    recommendations: List[ResortScore]
    confidence: str  # "high", "medium", "low"


@dataclass
class DailyResortRecommendation:
    """Recommendations for resorts aggregated over a full 24-hour period."""
    date: datetime
    recommendations: List[ResortScore]
    confidence: str  # "high", "medium", "low"
