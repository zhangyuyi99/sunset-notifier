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


def main():
    print("=== Sunset Notifier Setup ===\n")

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

    # Step 5 — Preview
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
