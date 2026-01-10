"""Open-Meteo API client for weather forecasts."""

import requests
from datetime import datetime, timedelta
from typing import List, Optional
from src.models import WeatherConditions


class OpenMeteoClient:
    """Client for Open-Meteo weather API."""
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7
    ) -> List[WeatherConditions]:
        """Fetch weather forecast for a location.
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            days: Number of days to forecast (1-7)
        
        Returns:
            List of WeatherConditions for each forecast hour
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": [
                "temperature_2m",
                "snowfall",
                "rain",
                "windspeed_10m",
                "winddirection_10m",
                "cloudcover",
            ],
            "forecast_days": min(days, 7),
            "timezone": "auto",
        }
        
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_forecast(data)
        except requests.RequestException as e:
            print(f"Warning: Failed to fetch weather data: {e}")
            return self._get_mock_forecast(days)
    
    def _parse_forecast(self, data: dict) -> List[WeatherConditions]:
        """Parse API response into WeatherConditions objects."""
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        snowfall = hourly.get("snowfall", [])
        rain = hourly.get("rain", [])
        windspeed = hourly.get("windspeed_10m", [])
        winddir = hourly.get("winddirection_10m", [])
        cloudcover = hourly.get("cloudcover", [])
        
        conditions = []
        for i in range(len(times)):
            temp = temps[i] if i < len(temps) else 0.0
            # Estimate freezing level (simplified: 150m per degree above 0°C)
            freezing_level = max(0, temp * 150)
            
            conditions.append(WeatherConditions(
                timestamp=datetime.fromisoformat(times[i].replace('Z', '+00:00')),
                temperature=temp,
                snowfall=snowfall[i] if i < len(snowfall) else 0.0,
                rainfall=rain[i] if i < len(rain) else 0.0,
                wind_speed=windspeed[i] if i < len(windspeed) else 0.0,
                wind_direction=winddir[i] if i < len(winddir) else 0.0,
                cloud_cover=cloudcover[i] if i < len(cloudcover) else 0.0,
                freezing_level=freezing_level,
            ))
        
        return conditions
    
    def _get_mock_forecast(self, days: int) -> List[WeatherConditions]:
        """Generate mock forecast data as fallback."""
        conditions = []
        start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for day in range(days):
            for hour in range(24):
                timestamp = start + timedelta(days=day, hours=hour)
                
                # Simple mock pattern: cold mornings, warmer afternoons
                base_temp = -5 + (hour - 6) * 0.5 if 6 <= hour <= 14 else -5
                
                conditions.append(WeatherConditions(
                    timestamp=timestamp,
                    temperature=base_temp,
                    snowfall=1.0 if hour < 6 else 0.0,  # Snow overnight
                    rainfall=0.0,
                    wind_speed=5.0,
                    wind_direction=270.0,
                    cloud_cover=50.0,
                    freezing_level=max(0, base_temp * 150),
                ))
        
        return conditions


def get_weather_forecast(latitude: float, longitude: float, days: int = 7) -> List[WeatherConditions]:
    """Convenience function to get weather forecast."""
    client = OpenMeteoClient()
    return client.get_forecast(latitude, longitude, days)
