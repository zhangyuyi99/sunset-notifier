import datetime
import logging
import time

logger = logging.getLogger(__name__)

# Abbreviated weekday names matching Python's date.strftime("%a").lower()
WEEKDAYS = {"mon", "tue", "wed", "thu", "fri"}
DAY_ABBR = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def should_remind_today(remind_days) -> bool:
    """Return True if today is a reminder day."""
    today = datetime.date.today().strftime("%a").lower()
    if remind_days == "weekdays":
        return today in WEEKDAYS
    if remind_days == "everyday":
        return True
    # List of abbreviated day names
    return today in {d.lower() for d in remind_days}


def seconds_until(target: datetime.datetime) -> float:
    """Return seconds until target datetime. Negative if target is in the past."""
    now = datetime.datetime.now().astimezone()
    delta = target - now
    return delta.total_seconds()


def _sleep_until_tomorrow_midnight() -> None:
    """Sleep until 00:01 tomorrow."""
    now = datetime.datetime.now()
    tomorrow = (now + datetime.timedelta(days=1)).replace(
        hour=0, minute=1, second=0, microsecond=0
    )
    secs = (tomorrow - now).total_seconds()
    logger.info("Sleeping %.0f seconds until tomorrow 00:01", secs)
    time.sleep(max(secs, 0))


def run_loop(config) -> None:
    """Main scheduler loop. Runs forever, sending a notification each eligible day."""
    from notifier.sunset import get_sunset_time
    from notifier.notify import send_notification, play_sound, pick_message
    import os

    sound_path = os.path.join(os.path.dirname(__file__), "..", "assets", "chime.wav")
    sound_path = os.path.normpath(sound_path)

    while True:
        if not should_remind_today(config.REMIND_DAYS):
            logger.info("Not a reminder day. Sleeping until tomorrow.")
            _sleep_until_tomorrow_midnight()
            continue

        sunset = get_sunset_time(config.LATITUDE, config.LONGITUDE)
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

        _sleep_until_tomorrow_midnight()
