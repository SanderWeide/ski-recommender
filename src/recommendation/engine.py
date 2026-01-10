"""Main recommendation engine."""

from datetime import datetime, timedelta
from typing import List, Optional
from src.models import (
    Resort, SkierProfile, WeatherConditions, PisteScore,
    DailyRecommendation, TimeOfDay, Piste, Difficulty
)
from src.scoring.piste_scorer import score_piste, SKILL_DIFFICULTY_MAP
from src.scoring.time_of_day import list_time_blocks, get_representative_hour
from src.snow_model.freeze_thaw import has_recent_snowfall, evaluate_overnight_refreeze


# Score threshold for recommendations
MIN_SCORE_THRESHOLD = 50


class RecommendationEngine:
    """Main engine for generating piste recommendations."""
    
    def __init__(self, resort: Resort, weather_forecast: List[WeatherConditions]):
        self.resort = resort
        self.weather_forecast = weather_forecast
    
    def generate_recommendations(
        self,
        skier_profile: SkierProfile,
        start_date: datetime,
        days: int = 7,
        top_n: int = 5,
    ) -> List[DailyRecommendation]:
        """Generate recommendations for multiple days.
        
        Args:
            skier_profile: Skier preferences and skill level
            start_date: Start date for recommendations
            days: Number of days to generate recommendations for
            top_n: Number of top pistes to return per time block
        
        Returns:
            List of DailyRecommendation objects
        """
        recommendations = []
        
        # Group weather by day
        weather_by_day = self._group_weather_by_day(start_date, days)
        
        for day_offset in range(days):
            date = start_date + timedelta(days=day_offset)
            day_weather = weather_by_day.get(day_offset, [])
            
            if not day_weather:
                continue
            
            # Generate recommendations for each time block
            for time_block in list_time_blocks():
                # Skip if user has time preference and this doesn't match
                if skier_profile.preferred_time and skier_profile.preferred_time != time_block:
                    continue
                
                daily_rec = self._generate_time_block_recommendations(
                    date,
                    time_block,
                    day_weather,
                    skier_profile,
                    top_n,
                )
                
                if daily_rec:
                    recommendations.append(daily_rec)
        
        return recommendations
    
    def _generate_time_block_recommendations(
        self,
        date: datetime,
        time_block: TimeOfDay,
        day_weather: List[WeatherConditions],
        skier_profile: SkierProfile,
        top_n: int,
    ) -> Optional[DailyRecommendation]:
        """Generate recommendations for a specific time block."""
        # Get weather for this time block
        representative_hour = get_representative_hour(time_block)
        block_weather = None
        
        for w in day_weather:
            if w.timestamp.hour == representative_hour:
                block_weather = w
                break
        
        if not block_weather:
            # Use closest weather data
            block_weather = day_weather[len(day_weather) // 2] if day_weather else None
        
        if not block_weather:
            return None
        
        # Get weather history (last 24 hours for context)
        weather_index = self.weather_forecast.index(block_weather)
        recent_weather = self.weather_forecast[max(0, weather_index - 24):weather_index + 1]
        
        # Score all pistes
        piste_scores = []
        
        for piste in self.resort.pistes:
            # Filter by skill level
            suitable_difficulties = SKILL_DIFFICULTY_MAP[skier_profile.skill_level]
            
            # Allow slightly broader range but score less suitable pistes lower
            if skier_profile.preferred_difficulty:
                # If user has preference, prioritize but don't strictly filter
                pass
            
            score, snow_state, explanation = score_piste(
                piste,
                block_weather,
                time_block,
                recent_weather,
                skier_profile.skill_level,
            )
            
            # Apply threshold
            if score >= MIN_SCORE_THRESHOLD:
                piste_scores.append(PisteScore(
                    piste=piste,
                    score=score,
                    snow_state=snow_state,
                    explanation=explanation,
                    timestamp=block_weather.timestamp,
                    time_of_day=time_block,
                ))
        
        # Sort by score (descending)
        piste_scores.sort(key=lambda x: x.score, reverse=True)
        
        # Take top N
        top_pistes = piste_scores[:top_n]
        
        # Generate summary and confidence
        snow_summary = self._generate_snow_summary(recent_weather, block_weather)
        confidence = self._calculate_confidence(recent_weather, block_weather, len(top_pistes))
        
        return DailyRecommendation(
            date=date,
            time_of_day=time_block,
            recommendations=top_pistes,
            snow_summary=snow_summary,
            confidence=confidence,
        )
    
    def _group_weather_by_day(
        self,
        start_date: datetime,
        days: int
    ) -> dict:
        """Group weather forecast by day offset."""
        weather_by_day = {}
        
        for weather in self.weather_forecast:
            day_offset = (weather.timestamp.date() - start_date.date()).days
            
            if 0 <= day_offset < days:
                if day_offset not in weather_by_day:
                    weather_by_day[day_offset] = []
                weather_by_day[day_offset].append(weather)
        
        return weather_by_day
    
    def _generate_snow_summary(
        self,
        recent_weather: List[WeatherConditions],
        current_weather: WeatherConditions
    ) -> str:
        """Generate a summary of snow conditions."""
        # Check for recent snowfall
        has_snow, snow_amount = has_recent_snowfall(recent_weather, hours=12)
        
        # Check overnight refreeze
        overnight = recent_weather[-16:-8] if len(recent_weather) >= 16 else []
        refreeze_quality, _ = evaluate_overnight_refreeze(overnight)
        
        # Check temperature trend
        temps = [w.temperature for w in recent_weather[-6:]] if len(recent_weather) >= 6 else []
        temp_trend = "warming" if temps and temps[-1] > temps[0] + 2 else \
                     "cooling" if temps and temps[-1] < temps[0] - 2 else "stable"
        
        parts = []
        
        if has_snow and snow_amount > 2:
            parts.append(f"Fresh snow ({snow_amount:.0f}cm in last 12h)")
        
        if refreeze_quality in ["excellent", "good"]:
            parts.append(f"{refreeze_quality} overnight refreeze")
        elif refreeze_quality == "none":
            parts.append("no overnight refreeze")
        
        parts.append(f"temperatures {temp_trend}")
        
        # Wind
        if current_weather.wind_speed > 15:
            parts.append("windy conditions")
        
        return ", ".join(parts) + "."
    
    def _calculate_confidence(
        self,
        recent_weather: List[WeatherConditions],
        current_weather: WeatherConditions,
        num_recommendations: int
    ) -> str:
        """Calculate confidence level for recommendations.
        
        Returns: "high", "medium", or "low"
        """
        # Start with medium
        confidence_score = 0.5
        
        # Good number of suitable pistes
        if num_recommendations >= 3:
            confidence_score += 0.2
        elif num_recommendations < 2:
            confidence_score -= 0.2
        
        # Stable weather
        temps = [w.temperature for w in recent_weather[-6:]] if len(recent_weather) >= 6 else []
        if temps:
            temp_variance = max(temps) - min(temps)
            if temp_variance < 3:
                confidence_score += 0.1
            elif temp_variance > 8:
                confidence_score -= 0.15
        
        # Good snow conditions
        has_snow, _ = has_recent_snowfall(recent_weather, hours=12)
        if has_snow:
            confidence_score += 0.1
        
        # Rain degrades confidence
        recent_rain = sum(w.rainfall for w in recent_weather[-6:]) if len(recent_weather) >= 6 else 0
        if recent_rain > 1:
            confidence_score -= 0.2
        
        # High winds reduce confidence
        if current_weather.wind_speed > 20:
            confidence_score -= 0.15
        
        # Convert to categorical
        if confidence_score >= 0.7:
            return "high"
        elif confidence_score >= 0.4:
            return "medium"
        else:
            return "low"
