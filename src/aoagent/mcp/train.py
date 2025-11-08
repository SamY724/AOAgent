"""UK train timetable MCP server for AOAgent.

This server provides live UK train departure information and journey planning using Huxley2 API.
No API key required - uses free National Rail Enquiries data.

Available tools:
- get_train_departures: Live departure board for any UK station
- get_train_journey: Direct services between two stations

Example usage:
- get_train_departures("Liverpool", "Manchester", 3) -> Shows next 3 trains to Manchester
- get_train_journey("LIV", "MAN") -> Next direct services Liverpool to Manchester

Supports common station codes (LIV, MAN, EUS) or full names (Liverpool Lime Street).
"""

import json
import os
from pathlib import Path

import requests
from mcp.server.fastmcp import FastMCP

train_mcp = FastMCP("UKTrains")

BASE_URL = "https://huxley2.azurewebsites.net"

# Load station mappings from config
config_path = Path(__file__).parent / "config" / "stations.json"
with open(config_path) as f:
    STATION_CONFIG = json.load(f)


@train_mcp.tool()
def get_train_departures(station: str, destination: str = "", num_services: int = 5) -> str:
    """Get live train departure information for a UK station.

    Shows live departure board with scheduled times, delays, platforms, and operators.

    Args:
        station: Station name or 3-letter code (e.g. 'Liverpool Lime Street' or 'LIV')
        destination: Optional destination filter (e.g. 'Manchester' or 'MAN')
        num_services: Number of services to return (default: 5)

    Example:
        get_train_departures("Liverpool", "Manchester", 3)
        -> "Departures from Liverpool Lime Street:
            14:15 to Manchester Piccadilly (Platform 7) - On time [Northern Rail]
            14:45 to Manchester Piccadilly (Platform 6) - Expected 14:50 [TransPennine Express]"
    """
    try:
        url = f"{BASE_URL}/departures/{_get_station_code(station)}"
        params = {"numServices": num_services}

        if destination:
            params["filterCrs"] = _get_station_code(destination)

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("trainServices"):
            return f"No train services found from {station}"

        station_name = data.get("locationName", station)
        result = f"Departures from {station_name}:\n"

        for service in data["trainServices"]:
            scheduled = service["std"]
            estimated = service.get("etd", scheduled)
            platform = service.get("platform", "TBC")
            operator = service.get("operator", "Unknown")
            destination_name = service.get("destination", [{}])[0].get("locationName", "Unknown")

            status = "On time" if estimated == scheduled else f"Expected {estimated}"
            result += f"{scheduled} to {destination_name} (Platform {platform}) - {status} [{operator}]\n"

        return result.strip()

    except requests.RequestException as e:
        return f"Error fetching train data: {str(e)}"
    except (KeyError, IndexError) as e:
        return f"Error parsing train data: {str(e)}"


@train_mcp.tool()
def get_train_journey(origin: str, destination: str, num_services: int = 3) -> str:
    """Get train journey information between two UK stations.

    Shows direct services between origin and destination with departure times and operators.

    Args:
        origin: Origin station name or code (e.g. 'Liverpool' or 'LIV')
        destination: Destination station name or code (e.g. 'Manchester' or 'MAN')
        num_services: Number of services to return (default: 3)

    Example:
        get_train_journey("Liverpool", "Manchester")
        -> "Next trains from Liverpool Lime Street to Manchester:
            14:15 - On time [Northern Rail]
            14:45 - Expected 14:50 [TransPennine Express]
            15:15 - On time [Northern Rail]"
    """
    try:
        origin_code = _get_station_code(origin)
        dest_code = _get_station_code(destination)

        url = f"{BASE_URL}/departures/{origin_code}/to/{dest_code}"
        params = {"numServices": num_services}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("trainServices"):
            return f"No direct services found from {origin} to {destination}"

        result = f"Next trains from {data.get('locationName', origin)} to {destination}:\n"

        for service in data["trainServices"]:
            departure = service["std"]
            estimated_dep = service.get("etd", departure)
            operator = service.get("operator", "Unknown")

            status = "On time" if estimated_dep == departure else f"Expected {estimated_dep}"
            result += f"{departure} - {status} [{operator}]\n"

        return result.strip()

    except requests.RequestException as e:
        return f"Error fetching journey data: {str(e)}"
    except (KeyError, IndexError) as e:
        return f"Error parsing journey data: {str(e)}"


def _get_station_code(station: str) -> str:
    """Convert station name to 3-letter code or return if already a code."""
    if len(station) == 3 and station.isupper():
        return station

    station_lower = station.lower()
    return STATION_CONFIG["stations"].get(station_lower, station.upper()[:3])