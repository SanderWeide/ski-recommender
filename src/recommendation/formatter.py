"""Output formatting for recommendations."""

import json
from typing import List
from datetime import datetime
from src.models import DailyRecommendation, PisteScore, TimeOfDay


def format_recommendations_text(
    recommendations: List[DailyRecommendation],
    resort_name: str
) -> str:
    """Format recommendations as human-readable text.
    
    Args:
        recommendations: List of daily recommendations
        resort_name: Name of the resort
    
    Returns:
        Formatted text string
    """
    lines = []
    lines.append(f"=== Ski Piste Recommendations for {resort_name} ===\n")
    
    # Group by date
    by_date = {}
    for rec in recommendations:
        date_key = rec.date.strftime("%Y-%m-%d")
        if date_key not in by_date:
            by_date[date_key] = []
        by_date[date_key].append(rec)
    
    for date_str in sorted(by_date.keys()):
        date_recs = by_date[date_str]
        lines.append(f"\n{'='*60}")
        lines.append(f"Date: {date_str}")
        lines.append(f"{'='*60}\n")
        
        for rec in date_recs:
            time_name = {
                TimeOfDay.MORNING: "Morning (08:00-10:30)",
                TimeOfDay.LATE_MORNING: "Late Morning (10:30-12:30)",
                TimeOfDay.AFTERNOON: "Afternoon (12:30-16:00)",
            }[rec.time_of_day]
            
            lines.append(f"\n{time_name}")
            lines.append(f"{'-'*60}")
            lines.append(f"Conditions: {rec.snow_summary}")
            lines.append(f"Confidence: {rec.confidence.upper()}\n")
            
            if not rec.recommendations:
                lines.append("  No suitable pistes found for these conditions.\n")
                continue
            
            lines.append("Top Recommendations:")
            for i, piste_score in enumerate(rec.recommendations, 1):
                lines.append(f"\n  {i}. {piste_score.piste.name} (Score: {piste_score.score:.0f}/100)")
                lines.append(f"     Difficulty: {piste_score.piste.difficulty.value.upper()}")
                lines.append(f"     Altitude: {piste_score.piste.altitude_min}-{piste_score.piste.altitude_max}m")
                lines.append(f"     Snow State: {piste_score.snow_state.value.replace('_', ' ').title()}")
                lines.append(f"     {piste_score.explanation}")
    
    lines.append(f"\n{'='*60}\n")
    return "\n".join(lines)


def format_recommendations_json(
    recommendations: List[DailyRecommendation],
    resort_name: str
) -> str:
    """Format recommendations as JSON.
    
    Args:
        recommendations: List of daily recommendations
        resort_name: Name of the resort
    
    Returns:
        JSON string
    """
    output = {
        "resort": resort_name,
        "generated_at": datetime.now().isoformat(),
        "recommendations": []
    }
    
    for rec in recommendations:
        rec_dict = {
            "date": rec.date.strftime("%Y-%m-%d"),
            "time_of_day": rec.time_of_day.value,
            "snow_summary": rec.snow_summary,
            "confidence": rec.confidence,
            "pistes": []
        }
        
        for piste_score in rec.recommendations:
            piste_dict = {
                "name": piste_score.piste.name,
                "id": piste_score.piste.id,
                "score": round(piste_score.score, 1),
                "difficulty": piste_score.piste.difficulty.value,
                "altitude_range": [
                    piste_score.piste.altitude_min,
                    piste_score.piste.altitude_max
                ],
                "aspect": piste_score.piste.aspect.value,
                "snow_state": piste_score.snow_state.value,
                "explanation": piste_score.explanation,
            }
            rec_dict["pistes"].append(piste_dict)
        
        output["recommendations"].append(rec_dict)
    
    return json.dumps(output, indent=2)
