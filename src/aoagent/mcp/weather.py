"""Weather forecasting MCP server for AOAgent.

This server provides real-time weather data and forecasts using OpenWeatherMap API.
Requires OPENWEATHER_API_KEY environment variable to be set.

Available tools:
- get_current_weather: Get current conditions for any city
- get_weather_forecast: Get 24-hour forecast with 3-hour intervals

Example usage:
- get_current_weather("London", "metric") -> "London, GB: 15.2°C, light rain, 85% humidity"
- get_weather_forecast("Manchester") -> Shows next 24 hours with times and conditions
"""

import json
import os
from pathlib import Path

import requests
from mcp.server.fastmcp import FastMCP

weather_mcp = FastMCP("Weather")

API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Load config
config_path = Path(__file__).parent / "config" / "weather.json"
try:
    with open(config_path) as f:
        WEATHER_CONFIG = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    raise RuntimeError(f"Failed to load weather configuration: {e}")


@weather_mcp.tool()
def get_current_weather(city: str, units: str = "metric") -> str:
    """Get current weather conditions for a city.

    Returns concise current weather including temperature, conditions, and humidity.

    Args:
        city: City name (e.g. 'San Francisco' or 'London,UK')
        units: Temperature units ('metric', 'imperial', or 'kelvin')

    Example:
        get_current_weather("Liverpool", "metric")
        -> "Liverpool, GB: 12.5°C, overcast clouds, 78% humidity"
    """
    if not API_KEY:
        return "Weather API key not configured. Please set OPENWEATHER_API_KEY."

    try:
        response = requests.get(
            f"{WEATHER_CONFIG['api']['base_url']}/weather",
            params={"q": city, "appid": API_KEY, "units": units},
            timeout=WEATHER_CONFIG['api']['timeout']
        )
        response.raise_for_status()
        data = response.json()

        weather = data["weather"][0]
        main = data["main"]
        temp_unit = WEATHER_CONFIG['units'][units]['temperature']
        location = f"{data['name']}, {data['sys']['country']}"

        return (f"{location}: {main['temp']:.1f}°{temp_unit}, "
                f"{weather['description']}, {main['humidity']}% humidity")

    except requests.RequestException as e:
        return f"Error fetching weather data: {str(e)}"


@weather_mcp.tool()
def get_weather_forecast(city: str, units: str = "metric") -> str:
    """Get 24-hour weather forecast for a city.

    Returns upcoming weather with 3-hour intervals showing time, temperature, and conditions.

    Args:
        city: City name (e.g. 'San Francisco' or 'London,UK')
        units: Temperature units ('metric', 'imperial', or 'kelvin')

    Example:
        get_weather_forecast("Manchester", "metric")
        -> "24-hour forecast for Manchester, GB:
            14:00: 13.2°C, light rain
            17:00: 12.8°C, overcast clouds
            ..."
    """
    if not API_KEY:
        return "Weather API key not configured. Please set OPENWEATHER_API_KEY."

    try:
        response = requests.get(
            f"{WEATHER_CONFIG['api']['base_url']}/forecast",
            params={"q": city, "appid": API_KEY, "units": units},
            timeout=WEATHER_CONFIG['api']['timeout']
        )
        response.raise_for_status()
        data = response.json()

        temp_unit = WEATHER_CONFIG['units'][units]['temperature']
        city_info = data["city"]
        forecasts = data["list"][:8]  # Next 24 hours (3-hour intervals)

        result = f"24-hour forecast for {city_info['name']}, {city_info['country']}:\n"
        for forecast in forecasts:
            time = forecast["dt_txt"][11:16]
            temp = forecast["main"]["temp"]
            desc = forecast["weather"][0]["description"]
            result += f"{time}: {temp:.1f}°{temp_unit}, {desc}\n"

        return result.strip()

    except requests.RequestException as e:
        return f"Error fetching forecast data: {str(e)}"