import logging
import platform
import random
import subprocess

logger = logging.getLogger(__name__)


def send_notification(title: str, message: str) -> None:
    """Send a desktop notification using plyer."""
    try:
        from plyer import notification
        notification.notify(title=title, message=message, timeout=30)
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
