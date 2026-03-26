import re


def geocode(location_str: str) -> tuple:
    """Return (lat, lng) for a given location string.

    Accepts:
    - A city/address string (uses Nominatim geocoder via geopy)
    - A direct "lat,lng" string (parsed without network access)
    """
    # Try parsing as "lat,lng" directly first
    match = re.match(r"^\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*$", location_str)
    if match:
        return float(match.group(1)), float(match.group(2))

    # Use geopy Nominatim (free, no API key)
    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="sunset-notifier/1.0")
        result = geolocator.geocode(location_str, timeout=10)
        if result is None:
            raise ValueError(
                f"Could not find '{location_str}'. "
                "Try using latitude,longitude directly (e.g. '32.8328,-117.2713')"
            )
        return result.latitude, result.longitude
    except ImportError:
        raise RuntimeError("geopy is not installed. Run: pip install geopy")
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise RuntimeError(
            f"Could not find '{location_str}'. "
            "Try using latitude,longitude directly (e.g. '32.8328,-117.2713')"
        ) from e
