# 🌅 sunset-notifier

A lightweight background script that reminds you to go watch the sunset.
Runs on Windows, macOS, and Linux. No server, no internet required after setup.

**Default:** weekdays only, La Jolla San Diego, 5 minutes before sunset.

---

## What it does

Every day, at the right moment, your desktop shows:

> 🐸 小青蛙提醒你：
> 今天日落时间是 19:23
> 还有 5 分钟，放下手里的事去看看吧！

With a soft chime sound.

Then it goes back to sleep until tomorrow.

---

## How it works

```
Boot / manual start
       ↓
Calculate today's sunset time (from your coordinates, no API needed)
       ↓
Is today a reminder day? (weekday / weekend / every day)
       ↓  yes
Sleep until (sunset - reminder_minutes)
       ↓
Desktop notification + sound
       ↓
Sleep until tomorrow 00:01, repeat
```

No internet required. Sunset times are calculated locally using
the `ephem` library (astronomical calculations).

---

## Quick start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR-USERNAME/sunset-notifier.git
cd sunset-notifier
```

### 2. Install dependencies and run setup

```bash
pip install -r requirements.txt
python setup.py
```

`setup.py` will ask you:
- Your location (city name or latitude/longitude)
- Which days to remind you (weekdays / every day / custom)
- How many minutes before sunset
- Notification language (English / 中文)

### 3. Start the notifier

```bash
python main.py
```

### 4. Set it to start on boot (optional but recommended)

**Windows:**
```powershell
python install_autostart.py
```
Adds the script to Windows Task Scheduler to run at login.

**macOS:**
```bash
python install_autostart.py
```
Creates a launchd plist in `~/Library/LaunchAgents/`.

**Linux:**
```bash
python install_autostart.py
```
Creates a systemd user service or adds to `~/.config/autostart/`.

---

## Project structure

```
sunset-notifier/
├── main.py                  # Entry point: the main loop
├── setup.py                 # Interactive configuration
├── install_autostart.py     # Platform-specific autostart installer
├── config.py                # User configuration (written by setup.py)
├── notifier/
│   ├── sunset.py            # Sunset time calculation (ephem)
│   ├── scheduler.py         # Sleep logic, day-of-week filtering
│   ├── notify.py            # Cross-platform desktop notification + sound
│   └── geocode.py           # Address → lat/lng (geopy, offline fallback)
├── assets/
│   └── chime.wav            # Default notification sound
├── requirements.txt
└── README.md
```

---

## Configuration (config.py)

Written automatically by `setup.py`. You can also edit it directly.

```python
# Location — latitude and longitude are most accurate
LATITUDE  = 32.8328    # La Jolla, San Diego (default)
LONGITUDE = -117.2713

# Which days to send reminders
# Options: "weekdays", "everyday", or a list like ["mon","tue","wed","thu","fri","sat"]
REMIND_DAYS = "weekdays"

# How many minutes before sunset to notify
MINUTES_BEFORE = 5

# Notification language: "en" or "zh"
LANGUAGE = "en"

# Notification title and message templates
# Use {sunset_time} and {minutes} as placeholders
NOTIFY_TITLE_EN   = "🌅 Sunset in {minutes} minutes"
NOTIFY_MESSAGE_EN = "Today's sunset is at {sunset_time}. Go take a look!"

NOTIFY_TITLE_ZH   = "🐸 小青蛙提醒你"
NOTIFY_MESSAGE_ZH = "今天日落时间是 {sunset_time}，还有 {minutes} 分钟，放下手里的事去看看吧！"
```

---

## Implementation — phase by phase

### Phase 1 — Sunset calculation (`notifier/sunset.py`)

Use the `ephem` library to calculate today's sunset time.

```python
def get_sunset_time(lat: float, lng: float) -> datetime:
    """Return today's sunset as a timezone-aware datetime in local time."""
```

- Use `ephem.Observer` with the given lat/lng
- Set `observer.date` to today
- Use `ephem.Sun` and `observer.next_setting()` to get sunset UTC time
- Convert to local time using the system timezone
- Return a `datetime` object

**Done when:** `python -c "from notifier.sunset import get_sunset_time; print(get_sunset_time(32.8328, -117.2713))"` prints today's correct sunset time for La Jolla.

---

### Phase 2 — Cross-platform notification (`notifier/notify.py`)

Send a desktop notification and play a sound.

```python
def send_notification(title: str, message: str) -> None:
def play_sound(path: str) -> None:
```

**Notification — use `plyer`:**
```python
from plyer import notification
notification.notify(title=title, message=message, timeout=30)
```

**Sound — platform-specific:**
- Windows: `winsound.PlaySound(path, winsound.SND_FILENAME)`
- macOS: `subprocess.run(["afplay", path])`
- Linux: `subprocess.run(["aplay", path])` with fallback to `paplay`

Use `platform.system()` to detect the OS.

If sound playback fails, log the error but do NOT crash — the
notification is more important than the sound.

**Done when:** Running `python -c "from notifier.notify import send_notification; send_notification('Test', 'Hello!')"` shows a desktop notification.

---

### Phase 3 — Scheduler (`notifier/scheduler.py`)

The main timing loop.

```python
def should_remind_today(remind_days: str | list) -> bool:
def seconds_until(target: datetime) -> float:
def run_loop(config) -> None:
```

**`should_remind_today` logic:**
- `"weekdays"` → Monday–Friday only
- `"everyday"` → always True
- `list` → check if today's abbreviated weekday name is in the list

**`run_loop` logic:**
```
while True:
    wait until 00:01 if it's past midnight (start of new day)
    if should_remind_today():
        sunset = get_sunset_time(lat, lng)
        trigger = sunset - timedelta(minutes=MINUTES_BEFORE)
        if trigger > now:
            sleep until trigger
            send_notification(...)
            play_sound(...)
        else:
            log "Sunset already passed today, skipping"
    sleep until tomorrow 00:01
```

**Done when:** Setting `MINUTES_BEFORE = 0` and running `main.py` sends a notification at the exact sunset time.

---

### Phase 4 — Geocoding (`notifier/geocode.py`)

Convert a city name or address to lat/lng.

```python
def geocode(location_str: str) -> tuple[float, float]:
    """Return (lat, lng) for a given location string."""
```

- Use `geopy` with the `Nominatim` geocoder (free, no API key)
- If geocoding fails (no internet, bad address), raise a clear error:
  `"Could not find '{location_str}'. Try using latitude,longitude directly (e.g. '32.8328,-117.2713')"`
- Also accept direct `"lat,lng"` input and parse it without geocoding

**Done when:** `python -c "from notifier.geocode import geocode; print(geocode('La Jolla, San Diego'))"` prints approximately `(32.83, -117.27)`.

---

### Phase 5 — setup.py

Interactive configuration script.

Ask the user:

**Step 1 — Location:**
```
Enter your location (city name or lat,lng):
e.g. 'La Jolla, San Diego' or '32.8328,-117.2713'
[La Jolla, San Diego]:
```
- Geocode it → show the resolved coordinates for confirmation
- Save lat/lng (not the string) to config.py

**Step 2 — Reminder days:**
```
Which days should I remind you?
  1) Weekdays only (Mon–Fri)
  2) Every day
  3) Custom (choose days)
[1]:
```

**Step 3 — Minutes before sunset:**
```
How many minutes before sunset? [5]:
```

**Step 4 — Language:**
```
Notification language?
  1) English
  2) 中文
[1]:
```

**Step 5 — Preview:**
Show a preview of what the notification will look like:
```
Preview:
  Title:   🌅 Sunset in 5 minutes
  Message: Today's sunset is at 19:23. Go take a look!

Does this look good? [Y/n]:
```

Then write config.py and print:
```
✓ Configuration saved.
Run 'python main.py' to start, or 'python install_autostart.py' to run on boot.
```

---

### Phase 6 — Autostart (`install_autostart.py`)

Platform-specific autostart setup.

**Windows:** Use `schtasks` to create a Task Scheduler entry:
```
schtasks /create /tn "SunsetNotifier" /tr "python path\to\main.py" /sc onlogon /rl limited
```

**macOS:** Write a launchd plist to `~/Library/LaunchAgents/com.sunset-notifier.plist`:
```xml
<key>RunAtLoad</key><true/>
<key>ProgramArguments</key>
<array><string>python3</string><string>/path/to/main.py</string></array>
```

**Linux:** Write a `.desktop` file to `~/.config/autostart/sunset-notifier.desktop`.

Detect platform with `platform.system()`.
Print clear success/failure message for each step.

---

## Dependencies (requirements.txt)

```
ephem
plyer
geopy
```

No Anthropic API key needed. No internet needed at runtime.

---

## Cost

**Free.** No API calls, no cloud services, no subscriptions.

---

## Troubleshooting

**No notification appears**
- Windows: check that notifications are enabled in Settings → System → Notifications
- macOS: check System Preferences → Notifications → Python
- Linux: make sure `libnotify` is installed (`sudo apt install libnotify-bin`)

**Wrong sunset time**
- Double-check your coordinates in `config.py`
- Make sure your system clock and timezone are correct

**Sound doesn't play on Linux**
- Install `alsa-utils`: `sudo apt install alsa-utils`
- Or install `pulseaudio-utils` for `paplay`

---

## Instructions for Claude Code

Read this README and implement phase by phase, starting with Phase 1.

Confirm each phase works before proceeding:
- Phase 1 ✓ when: correct sunset time prints for La Jolla
- Phase 2 ✓ when: test notification appears on screen with sound
- Phase 3 ✓ when: scheduler correctly calculates sleep time and triggers notification
- Phase 4 ✓ when: "La Jolla, San Diego" resolves to correct coordinates
- Phase 5 ✓ when: setup.py runs end-to-end and writes correct config.py
- Phase 6 ✓ when: autostart is installed and main.py launches on next login

Ask before making any decisions not covered in this README.
