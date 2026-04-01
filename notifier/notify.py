import logging
import platform
import random
import subprocess

try:
    import requests as _requests
except ImportError:
    _requests = None

logger = logging.getLogger(__name__)

APP_NAME = "🐸 Sunset Notifier"


def send_notification(title: str, message: str) -> None:
    """Send a desktop notification.

    On Windows, plyer's app_name has no effect — the OS always labels the
    notification with the executable name ("Python").  We use winotify
    instead, which supports a custom app_id shown as the notification title.

    On macOS / Linux, plyer's app_name parameter works correctly.
    """
    if platform.system() == "Windows":
        _notify_windows(title, message)
    else:
        _notify_plyer(title, message)


def _notify_windows(title: str, message: str) -> None:
    try:
        from winotify import Notification
        toast = Notification(
            app_id=APP_NAME,
            title=title,
            msg=message,
            duration="long",
        )
        toast.show()
    except ImportError:
        logger.warning("winotify not installed — install it with: pip install winotify")
        _notify_plyer(title, message)
    except Exception as e:
        logger.error("Failed to send Windows notification: %s", e)


def _notify_plyer(title: str, message: str) -> None:
    try:
        from plyer import notification
        notification.notify(
            app_name=APP_NAME,
            title=title,
            message=message,
            timeout=30,
        )
    except Exception as e:
        logger.error("Failed to send notification: %s", e)


def play_sound(path: str) -> None:
    """Play a sound file. Fails gracefully — notification is more important."""
    system = platform.system()
    try:
        if system == "Windows":
            import winsound
            winsound.PlaySound(path, winsound.SND_FILENAME)
        elif system == "Darwin":
            subprocess.run(["afplay", path], check=True)
        else:
            # Linux: try aplay, fall back to paplay
            try:
                subprocess.run(["aplay", path], check=True, capture_output=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                subprocess.run(["paplay", path], check=True)
    except Exception as e:
        logger.error("Sound playback failed: %s", e)


def pick_message(language: str) -> str:
    """Return a random notification body message for the given language."""
    from config import MESSAGES_EN, MESSAGES_ZH
    if language == "zh":
        return random.choice(MESSAGES_ZH)
    return random.choice(MESSAGES_EN)


def get_weather_comment(latitude: float, longitude: float, language: str) -> str:
    """Fetch cloud cover from Open-Meteo and return a short weather comment.

    Returns an empty string if the request fails for any reason.
    """
    if _requests is None:
        return ""
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}"
            "&current=cloudcover,weathercode"
        )
        resp = _requests.get(url, timeout=5)
        resp.raise_for_status()
        cloudcover = resp.json()["current"]["cloudcover"]

        if language == "zh":
            if cloudcover <= 30:
                return "☀️ 今天是晴天，绝对值得去看！"
            elif cloudcover <= 70:
                return "⛅ 今天有些云，可能有不错的晚霞"
            else:
                return "☁️ 今天云比较多，但说不定有惊喜"
        else:
            if cloudcover <= 30:
                return "☀️ Clear skies — definitely worth watching!"
            elif cloudcover <= 70:
                return "⛅ Partly cloudy — might get some nice colors"
            else:
                return "☁️ Pretty cloudy today — but you never know!"
    except Exception as e:
        logger.debug("Weather fetch failed (skipping): %s", e)
        return ""
