import logging
import platform
import random
import subprocess

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
