import datetime
import logging
import time

from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

# Abbreviated weekday names matching Python's date.strftime("%a").lower()
DAY_ABBR = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
WEEKDAY_INDICES = {0, 1, 2, 3, 4}  # Monday=0 … Friday=4


def should_remind_today(remind_days, tz: ZoneInfo) -> bool:
    """Return True if today (in the location's timezone) is a reminder day."""
    now = datetime.datetime.now(tz)
    weekday = now.weekday()          # 0=Mon … 6=Sun, locale-independent
    abbr = DAY_ABBR[weekday]         # canonical English abbreviation
    if remind_days == "weekdays":
        return weekday in WEEKDAY_INDICES
    if remind_days == "everyday":
        return True
    # List of abbreviated day names
    return abbr in {d.lower() for d in remind_days}


def seconds_until(target: datetime.datetime) -> float:
    """Return seconds until target datetime. Negative if target is in the past."""
    now = datetime.datetime.now(target.tzinfo)
    delta = target - now
    return delta.total_seconds()


def _sleep_until_tomorrow_midnight(tz: ZoneInfo) -> None:
    """Sleep until 00:01 tomorrow in the location's timezone."""
    now = datetime.datetime.now(tz)
    tomorrow = (now + datetime.timedelta(days=1)).replace(
        hour=0, minute=1, second=0, microsecond=0
    )
    secs = (tomorrow - now).total_seconds()
    logger.info("Sleeping %.0f seconds until tomorrow 00:01", secs)
    time.sleep(max(secs, 0))


def run_loop(config) -> None:
    """Main scheduler loop. Runs forever, sending a notification each eligible day."""
    from notifier.sunset import get_sunset_time, get_location_tz
    from notifier.notify import send_notification, play_sound, pick_message
    import os

    sound_path = os.path.join(os.path.dirname(__file__), "..", "assets", "chime.wav")
    sound_path = os.path.normpath(sound_path)

    location_tz = get_location_tz(config.LATITUDE, config.LONGITUDE)
    logger.info("Location timezone: %s", location_tz.key)

    while True:
        if not should_remind_today(config.REMIND_DAYS, location_tz):
            logger.info("Not a reminder day. Sleeping until tomorrow.")
            _sleep_until_tomorrow_midnight(location_tz)
            continue

        sunset = get_sunset_time(config.LATITUDE, config.LONGITUDE, location_tz)
        trigger = sunset - datetime.timedelta(minutes=config.MINUTES_BEFORE)

        secs = seconds_until(trigger)
        if secs > 0:
            logger.info(
                "Sunset at %s — will notify at %s (%.0f seconds away)",
                sunset.strftime("%H:%M"),
                trigger.strftime("%H:%M"),
                secs,
            )
            time.sleep(secs)

            message = pick_message(config.LANGUAGE)
            if config.LANGUAGE == "zh":
                title = config.NOTIFY_TITLE_ZH.format(
                    sunset_time=sunset.strftime("%H:%M"),
                    minutes=config.MINUTES_BEFORE,
                )
            else:
                title = config.NOTIFY_TITLE_EN.format(
                    sunset_time=sunset.strftime("%H:%M"),
                    minutes=config.MINUTES_BEFORE,
                )

            send_notification(title, message)
            play_sound(sound_path)
        else:
            logger.info("Sunset trigger already passed today (%.0f s ago). Skipping.", -secs)

        _sleep_until_tomorrow_midnight(location_tz)
