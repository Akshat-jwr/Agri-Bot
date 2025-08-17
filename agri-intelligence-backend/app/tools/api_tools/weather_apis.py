"""
Weather API Tools for Agricultural Intelligence
Integrates with IMD, OpenWeatherMap, and other weather services
"""
import aiohttp
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class WeatherAPITool:
    def __init__(self):
        self.imd_base_url = "https://api.imd.gov.in"  # IMD API
        self.openweather_base_url = "http://api.openweathermap.org/data/2.5"
        self.openweather_api_key = "your_openweather_api_key"  # From env
        
    async def get_current_weather(self, location: Dict[str, float]) -> Dict:
        """Get current weather for given location"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.openweather_base_url}/weather"
                params = {
                    'lat': location['latitude'],
                    'lon': location['longitude'],
                    'appid': self.openweather_api_key,
                    'units': 'metric'
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'temperature': data['main']['temp'],
                            'humidity': data['main']['humidity'],
                            'rainfall': data.get('rain', {}).get('1h', 0),
                            'wind_speed': data['wind']['speed'],
                            'weather_condition': data['weather'][0]['description'],
                            'timestamp': datetime.now().isoformat()
                        }
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return {'error': str(e)}

    async def get_weather_forecast(self, location: Dict[str, float], days: int = 7) -> List[Dict]:
        """Get weather forecast for next N days"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.openweather_base_url}/forecast"
                params = {
                    'lat': location['latitude'],
                    'lon': location['longitude'],
                    'appid': self.openweather_api_key,
                    'units': 'metric',
                    'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        forecasts = []
                        
                        for item in data['list'][:days*8:8]:  # Daily forecasts
                            forecasts.append({
                                'date': item['dt_txt'].split()[0],
                                'temperature_max': item['main']['temp_max'],
                                'temperature_min': item['main']['temp_min'],
                                'humidity': item['main']['humidity'],
                                'rainfall_probability': item.get('pop', 0) * 100,
                                'wind_speed': item['wind']['speed'],
                                'weather_condition': item['weather'][0]['description']
                            })
                        
                        return forecasts
        except Exception as e:
            logger.error(f"Forecast API error: {e}")
            return [{'error': str(e)}]

    async def get_agricultural_weather_advisory(self, location: Dict, crop: str) -> Dict:
        """Get crop-specific weather advisory"""
        weather_data = await self.get_current_weather(location)
        forecast_data = await self.get_weather_forecast(location, 7)
        
        # Agricultural weather analysis
        advisory = {
            'current_conditions': weather_data,
            'forecast': forecast_data,
            'agricultural_advice': self._generate_weather_advice(weather_data, forecast_data, crop)
        }
        
        return advisory
    
    def _generate_weather_advice(self, current: Dict, forecast: List[Dict], crop: str) -> str:
        """Generate crop-specific weather advice"""
        advice = []
        
        # Temperature analysis
        if current.get('temperature', 0) > 35:
            advice.append(f"High temperature alert for {crop}. Consider irrigation scheduling.")
        
        # Rainfall analysis
        total_rainfall = sum(day.get('rainfall_probability', 0) for day in forecast[:3])
        if total_rainfall < 20:
            advice.append(f"Low rainfall expected. Plan irrigation for {crop}.")
        elif total_rainfall > 80:
            advice.append(f"Heavy rainfall likely. Check drainage for {crop} fields.")
        
        # Wind analysis
        if current.get('wind_speed', 0) > 15:
            advice.append("Strong winds expected. Secure crop support structures.")
        
        return ' '.join(advice) if advice else f"Weather conditions are suitable for {crop} cultivation."

# Global weather tool instance
weather_tool = WeatherAPITool()
