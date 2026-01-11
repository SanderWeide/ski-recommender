"""Resort-level recommendation engine for comparing multiple resorts."""

from datetime import datetime, timedelta
from typing import List, Optional
from src.models import (
    Resort, SkierProfile, WeatherConditions, PisteScore,
    ResortScore, ResortRecommendation, TimeOfDay, DailyResortRecommendation,
    WeeklyResortRecommendation
)
from src.scoring.piste_scorer import score_piste
from src.scoring.time_of_day import list_time_blocks, get_representative_hour
from src.snow_model.freeze_thaw import has_recent_snowfall, evaluate_overnight_refreeze


# Score threshold for suitable pistes
MIN_SCORE_THRESHOLD = 50

# Resort scoring constants
MIN_PISTES_FOR_WEIGHTED_SCORING = 5
TOP_PISTE_WEIGHT = 3
SECOND_PISTE_WEIGHT = 2
THIRD_PISTE_WEIGHT = 1.5
DEFAULT_PISTE_WEIGHT = 1
UNIFORM_TOP_WEIGHT = 2
MAX_VARIETY_BONUS = 10
PISTE_COUNT_MULTIPLIER = 1.5

# Weather history lookback
RECENT_SNOWFALL_HOURS = 12
OVERNIGHT_WEATHER_START_HOUR = 16  # Hours back from current time
OVERNIGHT_WEATHER_END_HOUR = 8     # Hours back from current time


class ResortRecommendationEngine:
    """Engine for generating resort-level recommendations across multiple resorts."""
    
    def __init__(self, resorts: List[Resort], weather_forecasts: dict):
        """Initialize engine with multiple resorts and their weather forecasts.
        
        Args:
            resorts: List of Resort objects
            weather_forecasts: Dictionary mapping resort_id to list of WeatherConditions
        """
        self.resorts = resorts
        self.weather_forecasts = weather_forecasts
    
    def generate_resort_recommendations(
        self,
        skier_profile: SkierProfile,
        start_date: datetime,
        days: int = 7,
        top_n_resorts: int = 3,
        top_n_pistes: int = 3,
    ) -> List[ResortRecommendation]:
        """Generate resort-level recommendations for multiple days.
        
        Args:
            skier_profile: Skier preferences and skill level
            start_date: Start date for recommendations
            days: Number of days to generate recommendations for
            top_n_resorts: Number of top resorts to return per time block
            top_n_pistes: Number of top pistes to include for each resort
        
        Returns:
            List of ResortRecommendation objects
        """
        recommendations = []
        
        for day_offset in range(days):
            date = start_date + timedelta(days=day_offset)
            
            # Generate recommendations for each time block
            for time_block in list_time_blocks():
                # Skip if user has time preference and this doesn't match
                if skier_profile.preferred_time and skier_profile.preferred_time != time_block:
                    continue
                
                resort_rec = self._generate_time_block_resort_recommendations(
                    date,
                    time_block,
                    skier_profile,
                    top_n_resorts,
                    top_n_pistes,
                )
                
                if resort_rec:
                    recommendations.append(resort_rec)
        
        return recommendations
    
    def generate_daily_resort_recommendations(
        self,
        skier_profile: SkierProfile,
        start_date: datetime,
        days: int = 7,
        top_n_resorts: int = 3,
        top_n_pistes: int = 3,
    ) -> List[DailyResortRecommendation]:
        """Generate resort-level recommendations aggregated over 24-hour periods.
        
        Args:
            skier_profile: Skier preferences and skill level
            start_date: Start date for recommendations
            days: Number of days to generate recommendations for
            top_n_resorts: Number of top resorts to return per day
            top_n_pistes: Number of top pistes to include for each resort
        
        Returns:
            List of DailyResortRecommendation objects
        """
        recommendations = []
        
        for day_offset in range(days):
            date = start_date + timedelta(days=day_offset)
            
            daily_rec = self._generate_daily_resort_recommendations(
                date,
                skier_profile,
                top_n_resorts,
                top_n_pistes,
            )
            
            if daily_rec:
                recommendations.append(daily_rec)
        
        return recommendations
    
    def _generate_daily_resort_recommendations(
        self,
        date: datetime,
        skier_profile: SkierProfile,
        top_n_resorts: int,
        top_n_pistes: int,
    ) -> Optional[DailyResortRecommendation]:
        """Generate resort recommendations for an entire 24-hour period.
        
        This aggregates scores across all time blocks (morning, late morning, afternoon)
        to provide a single daily recommendation.
        """
        resort_daily_scores = {}
        
        for resort in self.resorts:
            # Get weather forecast for this resort
            weather_forecast = self.weather_forecasts.get(resort.id, [])
            if not weather_forecast:
                continue
            
            # Filter weather for the specific date
            day_weather = [
                w for w in weather_forecast
                if w.timestamp.date() == date.date()
            ]
            
            if not day_weather:
                continue
            
            # Score resort for each time block and aggregate
            time_block_scores = []
            all_piste_scores_for_day = []
            
            for time_block in list_time_blocks():
                # Get weather for this time block
                representative_hour = get_representative_hour(time_block)
                block_weather = None
                
                for w in day_weather:
                    if w.timestamp.hour == representative_hour:
                        block_weather = w
                        break
                
                if not block_weather:
                    continue
                
                # Get weather history
                weather_index = weather_forecast.index(block_weather)
                recent_weather = weather_forecast[max(0, weather_index - 24):weather_index + 1]
                
                # Score all pistes for this time block
                piste_scores = []
                for piste in resort.pistes:
                    score, snow_state, explanation = score_piste(
                        piste,
                        block_weather,
                        time_block,
                        recent_weather,
                        skier_profile.skill_level,
                    )
                    
                    if score >= MIN_SCORE_THRESHOLD:
                        piste_scores.append(PisteScore(
                            piste=piste,
                            score=score,
                            snow_state=snow_state,
                            explanation=explanation,
                            timestamp=block_weather.timestamp,
                            time_of_day=time_block,
                        ))
                
                if piste_scores:
                    piste_scores.sort(key=lambda x: x.score, reverse=True)
                    all_piste_scores_for_day.extend(piste_scores)
                    
                    # Calculate average score for this time block
                    avg_score = sum(ps.score for ps in piste_scores[:5]) / min(5, len(piste_scores))
                    time_block_scores.append(avg_score)
            
            # If we have scores for this resort across the day
            if time_block_scores and all_piste_scores_for_day:
                # Calculate overall daily score (average across time blocks)
                daily_score = sum(time_block_scores) / len(time_block_scores)
                
                # Get best pistes across entire day (deduplicate by piste id, keep highest score)
                best_pistes_map = {}
                for ps in all_piste_scores_for_day:
                    if ps.piste.id not in best_pistes_map or ps.score > best_pistes_map[ps.piste.id].score:
                        best_pistes_map[ps.piste.id] = ps
                
                best_pistes = sorted(best_pistes_map.values(), key=lambda x: x.score, reverse=True)[:top_n_pistes]
                
                # Get a representative weather snapshot (midday)
                midday_weather = None
                for w in day_weather:
                    if w.timestamp.hour == 12:
                        midday_weather = w
                        break
                if not midday_weather and day_weather:
                    midday_weather = day_weather[len(day_weather) // 2]
                
                if midday_weather:
                    weather_index = weather_forecast.index(midday_weather)
                    recent_weather = weather_forecast[max(0, weather_index - 24):weather_index + 1]
                    
                    snow_summary = self._generate_snow_summary(recent_weather, midday_weather)
                    explanation = self._generate_resort_explanation(
                        resort, len(best_pistes_map), best_pistes, midday_weather
                    )
                    
                    resort_daily_scores[resort.id] = ResortScore(
                        resort=resort,
                        score=daily_score,
                        num_suitable_pistes=len(best_pistes_map),
                        best_piste_scores=best_pistes,
                        snow_summary=snow_summary,
                        explanation=explanation,
                        timestamp=midday_weather.timestamp,
                        time_of_day=TimeOfDay.LATE_MORNING,  # Representative time
                    )
        
        # Sort resorts by score
        sorted_resorts = sorted(resort_daily_scores.values(), key=lambda x: x.score, reverse=True)
        
        # Take top N
        top_resorts = sorted_resorts[:top_n_resorts]
        
        if not top_resorts:
            return None
        
        # Calculate confidence
        confidence = self._calculate_confidence(sorted_resorts)
        
        return DailyResortRecommendation(
            date=date,
            recommendations=top_resorts,
            confidence=confidence,
        )
    
    def generate_weekly_resort_recommendations(
        self,
        skier_profile: SkierProfile,
        start_date: datetime,
        top_n_resorts: int = 3,
        top_n_pistes: int = 3,
    ) -> WeeklyResortRecommendation:
        """Generate resort-level recommendations aggregated over a full week.
        
        Args:
            skier_profile: Skier preferences and skill level
            start_date: Start date for the week
            top_n_resorts: Number of top resorts to return
            top_n_pistes: Number of top pistes to include for each resort
        
        Returns:
            WeeklyResortRecommendation object
        """
        resort_weekly_scores = {}
        end_date = start_date + timedelta(days=6)  # 7-day week
        
        for resort in self.resorts:
            # Get weather forecast for this resort
            weather_forecast = self.weather_forecasts.get(resort.id, [])
            if not weather_forecast:
                continue
            
            # Filter weather for the week
            week_weather = [
                w for w in weather_forecast
                if start_date.date() <= w.timestamp.date() <= end_date.date()
            ]
            
            if not week_weather:
                continue
            
            # Score resort for each day and aggregate
            daily_scores = []
            all_piste_scores_for_week = []
            
            for day_offset in range(7):
                date = start_date + timedelta(days=day_offset)
                
                # Get weather for this day
                day_weather = [
                    w for w in week_weather
                    if w.timestamp.date() == date.date()
                ]
                
                if not day_weather:
                    continue
                
                # Score resort for each time block on this day
                day_time_block_scores = []
                
                for time_block in list_time_blocks():
                    # Get weather for this time block
                    representative_hour = get_representative_hour(time_block)
                    block_weather = None
                    
                    for w in day_weather:
                        if w.timestamp.hour == representative_hour:
                            block_weather = w
                            break
                    
                    if not block_weather:
                        continue
                    
                    # Get weather history
                    weather_index = weather_forecast.index(block_weather)
                    recent_weather = weather_forecast[max(0, weather_index - 24):weather_index + 1]
                    
                    # Score all pistes for this time block
                    piste_scores = []
                    for piste in resort.pistes:
                        score, snow_state, explanation = score_piste(
                            piste,
                            block_weather,
                            time_block,
                            recent_weather,
                            skier_profile.skill_level,
                        )
                        
                        if score >= MIN_SCORE_THRESHOLD:
                            piste_scores.append(PisteScore(
                                piste=piste,
                                score=score,
                                snow_state=snow_state,
                                explanation=explanation,
                                timestamp=block_weather.timestamp,
                                time_of_day=time_block,
                            ))
                    
                    if piste_scores:
                        piste_scores.sort(key=lambda x: x.score, reverse=True)
                        all_piste_scores_for_week.extend(piste_scores)
                        
                        # Calculate average score for this time block
                        avg_score = sum(ps.score for ps in piste_scores[:5]) / min(5, len(piste_scores))
                        day_time_block_scores.append(avg_score)
                
                # Calculate average for this day
                if day_time_block_scores:
                    day_avg_score = sum(day_time_block_scores) / len(day_time_block_scores)
                    daily_scores.append(day_avg_score)
            
            # If we have scores for this resort across the week
            if daily_scores and all_piste_scores_for_week:
                # Calculate overall weekly score (average across days)
                weekly_score = sum(daily_scores) / len(daily_scores)
                
                # Get best pistes across entire week (deduplicate by piste id, keep highest score)
                best_pistes_map = {}
                for ps in all_piste_scores_for_week:
                    if ps.piste.id not in best_pistes_map or ps.score > best_pistes_map[ps.piste.id].score:
                        best_pistes_map[ps.piste.id] = ps
                
                best_pistes = sorted(best_pistes_map.values(), key=lambda x: x.score, reverse=True)[:top_n_pistes]
                
                # Get a representative weather snapshot (mid-week, midday)
                midweek_date = start_date + timedelta(days=3)
                midweek_weather = None
                for w in week_weather:
                    if w.timestamp.date() == midweek_date.date() and w.timestamp.hour == 12:
                        midweek_weather = w
                        break
                
                # Fallback to any midweek weather
                if not midweek_weather:
                    for w in week_weather:
                        if w.timestamp.date() == midweek_date.date():
                            midweek_weather = w
                            break
                
                # Fallback to middle of week weather
                if not midweek_weather and week_weather:
                    midweek_weather = week_weather[len(week_weather) // 2]
                
                if midweek_weather:
                    weather_index = weather_forecast.index(midweek_weather)
                    recent_weather = weather_forecast[max(0, weather_index - 24):weather_index + 1]
                    
                    snow_summary = self._generate_snow_summary(recent_weather, midweek_weather)
                    explanation = self._generate_resort_explanation(
                        resort, len(best_pistes_map), best_pistes, midweek_weather
                    )
                    explanation = f"Average conditions over 7 days, {explanation}"
                    
                    resort_weekly_scores[resort.id] = ResortScore(
                        resort=resort,
                        score=weekly_score,
                        num_suitable_pistes=len(best_pistes_map),
                        best_piste_scores=best_pistes,
                        snow_summary=snow_summary,
                        explanation=explanation,
                        timestamp=midweek_weather.timestamp,
                        time_of_day=TimeOfDay.LATE_MORNING,  # Representative time
                    )
        
        # Sort resorts by score
        sorted_resorts = sorted(resort_weekly_scores.values(), key=lambda x: x.score, reverse=True)
        
        # Take top N
        top_resorts = sorted_resorts[:top_n_resorts]
        
        # Calculate confidence
        confidence = self._calculate_confidence(sorted_resorts) if sorted_resorts else "low"
        
        return WeeklyResortRecommendation(
            start_date=start_date,
            end_date=end_date,
            recommendations=top_resorts,
            confidence=confidence,
        )
    
    def _generate_time_block_resort_recommendations(
        self,
        date: datetime,
        time_block: TimeOfDay,
        skier_profile: SkierProfile,
        top_n_resorts: int,
        top_n_pistes: int,
    ) -> Optional[ResortRecommendation]:
        """Generate resort recommendations for a specific time block."""
        resort_scores = []
        
        for resort in self.resorts:
            # Get weather forecast for this resort
            weather_forecast = self.weather_forecasts.get(resort.id, [])
            if not weather_forecast:
                continue
            
            # Filter weather for the specific date
            day_weather = [
                w for w in weather_forecast
                if w.timestamp.date() == date.date()
            ]
            
            if not day_weather:
                continue
            
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
                continue
            
            # Get weather history (last 24 hours for context)
            weather_index = weather_forecast.index(block_weather)
            recent_weather = weather_forecast[max(0, weather_index - 24):weather_index + 1]
            
            # Score this resort
            resort_score = self._score_resort(
                resort,
                block_weather,
                time_block,
                recent_weather,
                skier_profile,
                top_n_pistes,
            )
            
            if resort_score:
                resort_scores.append(resort_score)
        
        # Sort by score (descending)
        resort_scores.sort(key=lambda x: x.score, reverse=True)
        
        # Take top N resorts
        top_resorts = resort_scores[:top_n_resorts]
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(resort_scores)
        
        return ResortRecommendation(
            date=date,
            time_of_day=time_block,
            recommendations=top_resorts,
            confidence=confidence,
        )
    
    def _score_resort(
        self,
        resort: Resort,
        block_weather: WeatherConditions,
        time_block: TimeOfDay,
        recent_weather: List[WeatherConditions],
        skier_profile: SkierProfile,
        top_n_pistes: int,
    ) -> Optional[ResortScore]:
        """Score a single resort based on its piste conditions."""
        # Score all pistes in the resort
        piste_scores = []
        
        for piste in resort.pistes:
            score, snow_state, explanation = score_piste(
                piste,
                block_weather,
                time_block,
                recent_weather,
                skier_profile.skill_level,
            )
            
            # Only include pistes above threshold
            if score >= MIN_SCORE_THRESHOLD:
                piste_scores.append(PisteScore(
                    piste=piste,
                    score=score,
                    snow_state=snow_state,
                    explanation=explanation,
                    timestamp=block_weather.timestamp,
                    time_of_day=time_block,
                ))
        
        # If no suitable pistes, return None
        if not piste_scores:
            return None
        
        # Sort by score
        piste_scores.sort(key=lambda x: x.score, reverse=True)
        
        # Calculate overall resort score
        # Use weighted average: top pistes count more
        top_pistes = piste_scores[:top_n_pistes]
        num_pistes = len(piste_scores)
        
        if num_pistes >= MIN_PISTES_FOR_WEIGHTED_SCORING:
            # Many good pistes: weight heavily on top scores
            weights = [TOP_PISTE_WEIGHT, SECOND_PISTE_WEIGHT, THIRD_PISTE_WEIGHT] + \
                      [DEFAULT_PISTE_WEIGHT] * (num_pistes - 3)
        elif num_pistes >= 2:
            # Few pistes: more uniform weighting
            weights = [UNIFORM_TOP_WEIGHT] + [DEFAULT_PISTE_WEIGHT] * (num_pistes - 1)
        else:
            # Single piste: just use its score
            weights = [DEFAULT_PISTE_WEIGHT]
        
        weighted_scores = [
            piste_scores[i].score * weights[min(i, len(weights) - 1)]
            for i in range(len(piste_scores))
        ]
        resort_score = sum(weighted_scores) / sum(weights[:len(piste_scores)])
        
        # Bonus for having many suitable pistes
        variety_bonus = min(MAX_VARIETY_BONUS, len(piste_scores) * PISTE_COUNT_MULTIPLIER)
        resort_score = min(100, resort_score + variety_bonus)
        
        # Generate summary
        snow_summary = self._generate_snow_summary(recent_weather, block_weather)
        explanation = self._generate_resort_explanation(
            resort, len(piste_scores), top_pistes, block_weather
        )
        
        return ResortScore(
            resort=resort,
            score=resort_score,
            num_suitable_pistes=len(piste_scores),
            best_piste_scores=top_pistes,
            snow_summary=snow_summary,
            explanation=explanation,
            timestamp=block_weather.timestamp,
            time_of_day=time_block,
        )
    
    def _generate_snow_summary(
        self,
        recent_weather: List[WeatherConditions],
        current_weather: WeatherConditions
    ) -> str:
        """Generate a summary of snow conditions."""
        # Check for recent snowfall
        has_snow, snow_amount = has_recent_snowfall(recent_weather, hours=RECENT_SNOWFALL_HOURS)
        
        # Check overnight refreeze
        overnight = recent_weather[-OVERNIGHT_WEATHER_START_HOUR:-OVERNIGHT_WEATHER_END_HOUR] \
                    if len(recent_weather) >= OVERNIGHT_WEATHER_START_HOUR else []
        refreeze_quality, _ = evaluate_overnight_refreeze(overnight)
        
        # Check temperature trend
        temps = [w.temperature for w in recent_weather[-6:]] if len(recent_weather) >= 6 else []
        temp_trend = "warming" if temps and temps[-1] > temps[0] + 2 else \
                     "cooling" if temps and temps[-1] < temps[0] - 2 else "stable"
        
        parts = []
        
        if has_snow and snow_amount > 2:
            parts.append(f"Fresh snow ({snow_amount:.0f}cm)")
        
        if refreeze_quality in ["excellent", "good"]:
            parts.append(f"{refreeze_quality} overnight refreeze")
        
        parts.append(f"temperatures {temp_trend}")
        
        # Wind
        if current_weather.wind_speed > 15:
            parts.append("windy conditions")
        
        return ", ".join(parts) + "."
    
    def _generate_resort_explanation(
        self,
        resort: Resort,
        num_suitable: int,
        top_pistes: List[PisteScore],
        weather: WeatherConditions,
    ) -> str:
        """Generate explanation for resort score."""
        parts = []
        
        # Number of suitable pistes
        parts.append(f"{num_suitable} suitable piste{'s' if num_suitable != 1 else ''}")
        
        # Altitude range
        if resort.pistes:
            min_alt = min(p.altitude_min for p in resort.pistes)
            max_alt = max(p.altitude_max for p in resort.pistes)
            parts.append(f"altitude range {min_alt}-{max_alt}m")
        
        # Weather conditions
        if weather.temperature < -5:
            parts.append("cold conditions")
        elif weather.temperature > 2:
            parts.append("warm conditions")
        
        # Top piste info
        if top_pistes:
            avg_score = sum(p.score for p in top_pistes) / len(top_pistes)
            parts.append(f"top pistes averaging {avg_score:.0f}/100")
        
        return ", ".join(parts) + "."
    
    def _calculate_confidence(
        self,
        resort_scores: List[ResortScore]
    ) -> str:
        """Calculate confidence level for resort recommendations.
        
        Returns: "high", "medium", or "low"
        """
        if not resort_scores:
            return "low"
        
        # Start with medium
        confidence_score = 0.5
        
        # Good number of suitable resorts
        if len(resort_scores) >= 3:
            confidence_score += 0.2
        elif len(resort_scores) < 2:
            confidence_score -= 0.2
        
        # Check score distribution
        if len(resort_scores) >= 2:
            top_score = resort_scores[0].score
            second_score = resort_scores[1].score
            
            # Clear winner increases confidence
            if top_score - second_score > 15:
                confidence_score += 0.15
            # Very close scores decrease confidence slightly
            elif top_score - second_score < 5:
                confidence_score -= 0.1
        
        # High average scores increase confidence
        avg_score = sum(rs.score for rs in resort_scores) / len(resort_scores)
        if avg_score > 80:
            confidence_score += 0.15
        elif avg_score < 60:
            confidence_score -= 0.15
        
        # Convert to categorical
        if confidence_score >= 0.7:
            return "high"
        elif confidence_score >= 0.4:
            return "medium"
        else:
            return "low"
