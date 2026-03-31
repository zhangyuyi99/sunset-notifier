"""Interactive configuration script for sunset-notifier."""
import sys
import os

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def prompt(text: str, default: str = "") -> str:
    if default:
        result = input(f"{text} [{default}]: ").strip()
        return result if result else default
    return input(f"{text}: ").strip()


def _eval_marker(marker: str) -> bool:
    """Evaluate a simple PEP 508 environment marker (e.g. sys_platform == 'win32')."""
    import platform
    env = {
        "sys_platform": sys.platform,
        "platform_system": platform.system().lower(),
        "python_version": ".".join(str(v) for v in sys.version_info[:2]),
        "os_name": os.name,
    }
    try:
        return bool(eval(marker, {"__builtins__": {}}, env))
    except Exception:
        return True  # if unparseable, assume the package applies


def _check_dependencies() -> None:
    """Read requirements.txt, find missing packages, and offer to install them."""
    import importlib.metadata
    import re
    import subprocess

    req_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    if not os.path.isfile(req_path):
        return

    # Parse requirements, respecting platform markers
    required = []
    with open(req_path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if ";" in line:
                pkg_part, marker = line.split(";", 1)
                if not _eval_marker(marker.strip()):
                    continue  # not applicable on this platform
            else:
                pkg_part = line
            # Strip version specifiers: requests>=2.0 → requests
            pkg_name = re.split(r"[><=!~\s]", pkg_part.strip())[0]
            if pkg_name:
                required.append(pkg_name)

    # Find which are missing
    missing = []
    for pkg in required:
        try:
            importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            missing.append(pkg)

    if not missing:
        print("✓ All dependencies already installed.\n")
        return

    print("The following packages need to be installed:")
    for pkg in missing:
        print(f"  - {pkg}")
    print()

    answer = prompt("Install them now? (yes / no)", "yes").lower()
    print()
    if answer not in ("y", "yes"):
        print("  ⚠ Warning: the app may not work correctly without these packages.")
        print("  To install manually, run:")
        print("    pip install -r requirements.txt")
        print()
        return

    all_ok = True
    for pkg in missing:
        print(f"  Installing {pkg}...", end="", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(" ✓")
        else:
            print(" ✗")
            # Show just the last non-empty line of stderr for brevity
            error_lines = [l for l in result.stderr.splitlines() if l.strip()]
            if error_lines:
                print(f"    {error_lines[-1]}")
            all_ok = False
    print()
    if not all_ok:
        print("  ⚠ Some packages failed to install. The app may not work correctly.")
        print("  Try running:  pip install -r requirements.txt")
        print()


def main():
    print("=== Sunset Notifier Setup ===\n")

    # Step 0 — Dependencies
    _check_dependencies()

    # Step 1 — Location
    print("Step 1 — Location")
    print("  e.g. 'La Jolla, San Diego' or '32.8328,-117.2713'")
    location_str = prompt("Enter your location", "La Jolla, San Diego")

    from notifier.geocode import geocode
    try:
        lat, lng = geocode(location_str)
        print(f"  ✓ Resolved to: ({lat:.4f}, {lng:.4f})\n")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        sys.exit(1)

    # Step 2 — Reminder days
    print("Step 2 — Reminder days")
    print("  1) Weekdays only (Mon–Fri)")
    print("  2) Every day")
    print("  3) Custom (choose days)")
    day_choice = prompt("Which days should I remind you?", "1")

    day_abbrs = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    if day_choice == "1":
        remind_days = "weekdays"
    elif day_choice == "2":
        remind_days = "everyday"
    elif day_choice == "3":
        print("  Available: mon tue wed thu fri sat sun")
        raw = prompt("  Enter days separated by spaces", "mon tue wed thu fri").lower().split()
        remind_days = [d for d in raw if d in day_abbrs]
        if not remind_days:
            print("  No valid days entered, defaulting to weekdays.")
            remind_days = "weekdays"
    else:
        print("  Invalid choice, defaulting to weekdays.")
        remind_days = "weekdays"
    print()

    # Step 3 — Minutes before sunset
    print("Step 3 — Minutes before sunset")
    minutes_str = prompt("How many minutes before sunset?", "5")
    try:
        minutes_before = int(minutes_str)
    except ValueError:
        print("  Invalid input, defaulting to 5.")
        minutes_before = 5
    print()

    # Step 4 — Language
    print("Step 4 — Notification language")
    print("  1) English")
    print("  2) 中文")
    lang_choice = prompt("Language?", "1")
    language = "zh" if lang_choice == "2" else "en"
    print()

    # Step 5 — Sound
    print("Step 5 — Sound")
    sound_raw = prompt("Play a sound with the notification? (yes / no)", "yes").lower()
    notification_sound = sound_raw in ("y", "yes")
    print()

    # Step 6 — Preview
    import datetime
    # Use a fixed example sunset time for preview
    example_sunset = "19:23"
    if language == "zh":
        preview_title = f"🐸 小青蛙提醒你"
        preview_message = f"今天日落时间是 {example_sunset}，还有 {minutes_before} 分钟，放下手里的事去看看吧！"
    else:
        preview_title = f"🌅 Sunset in {minutes_before} minutes"
        preview_message = f"Today's sunset is at {example_sunset}. Go take a look!"

    print("Preview:")
    print(f"  Title:   {preview_title}")
    print(f"  Message: {preview_message}")
    print()
    confirm = prompt("Does this look good?", "Y").strip().lower()
    if confirm not in ("y", "yes", ""):
        print("Setup cancelled.")
        sys.exit(0)

    # Write config.py
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.py")
    if isinstance(remind_days, list):
        remind_days_repr = repr(remind_days)
    else:
        remind_days_repr = repr(remind_days)

    config_content = f'''# Location — latitude and longitude are most accurate
LATITUDE  = {lat}
LONGITUDE = {lng}

# Which days to send reminders
# Options: "weekdays", "everyday", or a list like ["mon","tue","wed","thu","fri","sat"]
REMIND_DAYS = {remind_days_repr}

# How many minutes before sunset to notify
MINUTES_BEFORE = {minutes_before}

# Notification language: "en" or "zh"
LANGUAGE = "{language}"

# Play a chime sound when the notification fires
NOTIFICATION_SOUND = {notification_sound}

# Notification title and message templates
# Use {{sunset_time}} and {{minutes}} as placeholders
NOTIFY_TITLE_EN   = "🌅 Sunset in {{minutes}} minutes"
NOTIFY_MESSAGE_EN = "Today\'s sunset is at {{sunset_time}}. Go take a look!"

NOTIFY_TITLE_ZH   = "🐸 小青蛙提醒你"
NOTIFY_MESSAGE_ZH = "今天日落时间是 {{sunset_time}}，还有 {{minutes}} 分钟，放下手里的事去看看吧！"

MESSAGES_ZH = [
    "太阳要下山了，快去看！",
    "今天的云很好看，不来会后悔的。",
    "去看日落吧，什么烦恼都暂时不重要。",
    "今天的日落是限定款，先到先得！",
    "窗外正在发生今天最美的事。",
    "日落不等人，但它愿意等你5分钟。",
    "科研可以等下继续，日落只有现在哦。",
]

MESSAGES_EN = [
    "The sun is putting on a show. Go watch it.",
    "Golden hour is here. Drop everything. Go.",
    "Best free show in town — happening right now outside your window.",
    "Today\'s sunset is one of a kind. So are you. Go enjoy it together.",
    "The sky is about to do something beautiful. Don\'t miss it.",
    "Your paper can wait 5 minutes. The sunset cannot.",
    "Mandatory sunset break. Doctor\'s orders. 🐸",
]
'''

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)

    print()
    print("✓ Configuration saved.")
    print("Run 'python main.py' to start, or 'python install_autostart.py' to run on boot.")


if __name__ == "__main__":
    main()
