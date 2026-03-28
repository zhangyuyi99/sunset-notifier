import datetime

import ephem
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo

_tf = TimezoneFinder()


def get_location_tz(lat: float, lng: float) -> ZoneInfo:
    """Return the IANA timezone for the given coordinates."""
    tz_name = _tf.timezone_at(lat=lat, lng=lng)
    if tz_name is None:
        raise ValueError(f"Could not determine timezone for ({lat}, {lng})")
    return ZoneInfo(tz_name)


def get_sunset_time(lat: float, lng: float, tz: ZoneInfo = None) -> datetime.datetime:
    """Return today's sunset as a timezone-aware datetime in the location's timezone."""
    location_tz = tz if tz is not None else get_location_tz(lat, lng)

    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lng)
    observer.elevation = 0
    # Suppress refraction effects to match standard civil sunset definition
    observer.pressure = 0
    observer.horizon = "-0:34"  # standard solar dip for sunset

    # Use midnight of today in the location's own timezone, converted to UTC.
    # ephem treats all dates as UTC; anchoring to location-local midnight ensures
    # next_setting() finds today's sunset for that location regardless of the OS timezone.
    today = datetime.datetime.now(location_tz).date()
    local_midnight = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=location_tz)
    local_midnight_utc = local_midnight.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    observer.date = ephem.Date(local_midnight_utc)

    sun = ephem.Sun()
    sunset_utc = observer.next_setting(sun).datetime()

    sunset_local = sunset_utc.replace(tzinfo=datetime.timezone.utc).astimezone(location_tz)
    return sunset_local
