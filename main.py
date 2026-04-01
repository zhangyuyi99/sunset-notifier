"""Entry point for sunset-notifier."""
import argparse
import datetime
import logging
import os
import sys

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sunset desktop notifier")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print timezone/sunset diagnostics and exit",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Send a test notification immediately and exit",
    )
    parser.add_argument(
        "--test-weather",
        action="store_true",
        help="Fetch weather, print diagnostics, send a test notification with weather, and exit",
    )
    args = parser.parse_args()

    if args.test_weather:
        import json
        try:
            import requests
        except ImportError:
            print("ERROR: 'requests' is not installed. Run: pip install requests")
            sys.exit(1)
        from notifier.notify import send_notification, play_sound, pick_message

        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={config.LATITUDE}&longitude={config.LONGITUDE}"
            "&current=cloudcover,weathercode"
        )
        print(f"Fetching: {url}\n")
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"ERROR: Weather API request failed: {e}")
            sys.exit(1)

        print("Raw API response:")
        print(json.dumps(data, indent=2))
        cloudcover = data["current"]["cloudcover"]
        print(f"\nCloud cover : {cloudcover}%")

        if config.LANGUAGE == "zh":
            if cloudcover <= 30:
                weather_comment = "☀️ 今天是晴天，绝对值得去看！"
            elif cloudcover <= 70:
                weather_comment = "⛅ 今天有些云，可能有不错的晚霞"
            else:
                weather_comment = "☁️ 今天云比较多，但说不定有惊喜"
        else:
            if cloudcover <= 30:
                weather_comment = "☀️ Clear skies — definitely worth watching!"
            elif cloudcover <= 70:
                weather_comment = "⛅ Partly cloudy — might get some nice colors"
            else:
                weather_comment = "☁️ Pretty cloudy today — but you never know!"
        print(f"Weather message : {weather_comment}")

        base_message = pick_message(config.LANGUAGE)
        full_message = f"{base_message}\n{weather_comment}"
        title = "Test notification — sunset notifier is working"
        print(f"\nFull notification:\n  Title   : {title}\n  Message : {full_message!r}\n")
        send_notification(title, full_message)
        sound_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "chime.wav"))
        if getattr(config, "NOTIFICATION_SOUND", True):
            play_sound(sound_path)
        print("Notification sent.")
        sys.exit(0)

    if args.test:
        from notifier.notify import send_notification, play_sound, pick_message
        sound_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "chime.wav"))
        message = pick_message(config.LANGUAGE)
        title = "Test notification — sunset notifier is working"
        print(f"Sending test notification...")
        send_notification(title, message)
        if getattr(config, "NOTIFICATION_SOUND", True):
            play_sound(sound_path)
        print("Done.")
        sys.exit(0)

    if args.debug:
        from notifier.sunset import get_sunset_time, get_location_tz
        from notifier.scheduler import should_remind_today, seconds_until

        location_tz = get_location_tz(config.LATITUDE, config.LONGITUDE)
        now_location = datetime.datetime.now(location_tz)
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        sunset_local = get_sunset_time(config.LATITUDE, config.LONGITUDE, location_tz)
        sunset_utc = sunset_local.astimezone(datetime.timezone.utc)
        trigger = sunset_local - datetime.timedelta(minutes=config.MINUTES_BEFORE)
        mins_until = seconds_until(trigger) / 60

        print(f"Location timezone  :  {location_tz.key}")
        print(f"Current time (loc) :  {now_location.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Current UTC time   :  {now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"Sunset (location)  :  {sunset_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Sunset (UTC)       :  {sunset_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"Minutes until sunset: {mins_until:.1f}")
        remind_today = should_remind_today(config.REMIND_DAYS, location_tz)
        will_notify = remind_today and mins_until > 0
        print(f"Notification today :  {'YES' if will_notify else 'NO'}", end="")
        if not remind_today:
            print(f"  (today is not a reminder day: REMIND_DAYS={config.REMIND_DAYS!r})", end="")
        elif mins_until <= 0:
            print(f"  (trigger already passed {-mins_until:.1f} min ago)", end="")
        print()
        sys.exit(0)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger(__name__).info("Sunset notifier started.")
    from notifier.scheduler import run_loop
    run_loop(config)
