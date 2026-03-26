import ephem
import datetime


def get_sunset_time(lat: float, lng: float) -> datetime.datetime:
    """Return today's sunset as a timezone-aware datetime in local time."""
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lng)
    observer.elevation = 0
    # Suppress refraction effects to match standard civil sunset definition
    observer.pressure = 0
    observer.horizon = "-0:34"  # standard solar dip for sunset

    # Set observer date to today at noon UTC to ensure we get today's sunset
    today = datetime.date.today()
    observer.date = ephem.Date(today)

    sun = ephem.Sun()
    sunset_utc = observer.next_setting(sun).datetime()

    # Convert UTC to local time using system timezone
    utc_offset = datetime.datetime.now().astimezone().utcoffset()
    local_tz = datetime.timezone(utc_offset)

    sunset_local = sunset_utc.replace(tzinfo=datetime.timezone.utc).astimezone(local_tz)
    return sunset_local
