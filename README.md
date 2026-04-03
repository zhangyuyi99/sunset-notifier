# 🌅 sunset-notifier

A tiny background script that reminds you to go watch the sunset.

Runs on Windows, macOS, and Linux. No API key. Completely free.

---

## What it does

Every day, a few minutes before sunset, your desktop shows a notification like:

> 🐸 小青蛙提醒你 — 19:23
> 今天的日落是限定款，先到先得！
> ⛅ 今天有些云，可能有不错的晚霞

Messages rotate randomly every day — you never know which one you'll get. The notification also includes a real-time **weather comment** based on current cloud cover, so you know whether it's worth heading outside.

---

## Requirements

- **Python 3.8+** — [download here](https://www.python.org/downloads/)
- Works on Windows, macOS, and Linux
- No API keys, no accounts, no subscriptions

---

## Quick start

### 1. Clone the repo

```bash
git clone https://github.com/zhangyuyi99/sunset-notifier.git
cd sunset-notifier
```

### 2. Configure

```bash
python setup.py
```

`setup.py` will automatically install any missing dependencies, then ask you:

- Your location (city name or latitude/longitude)
- Which days to remind you (weekdays / every day / custom)
- How many minutes before sunset
- Notification language (English / 中文)
- Whether to play a chime sound with the notification

### 3. Start

```bash
python main.py
```

### 4. Run on boot (recommended)

```bash
python install_autostart.py
```

Works on Windows (Task Scheduler), macOS (launchd), and Linux (systemd / autostart).

> **Windows users:** run this command as Administrator.

That's it. 🎉

---

## Customisation

Run `setup.py` again anytime to change your settings:

```bash
python setup.py
```

Or edit `config.py` directly:

```python
LATITUDE  = 32.8328       # Your coordinates
LONGITUDE = -117.2713
REMIND_DAYS = "weekdays"  # "weekdays", "everyday", or ["mon","wed","fri"]
MINUTES_BEFORE = 5        # How many minutes before sunset
LANGUAGE = "zh"           # "en" or "zh"
NOTIFICATION_SOUND = True # Set to False to disable the chime
```

Want to add your own messages? Edit `MESSAGES_EN` or `MESSAGES_ZH` in `config.py` —
one message is picked randomly each day.

---

## Features

- **Weather-aware notifications** — fetches live cloud cover from [Open-Meteo](https://open-meteo.com/) (free, no API key) and appends a comment like "Clear skies — definitely worth watching!" to each notification. Fails gracefully if there's no internet.
- **Optional chime sound** — plays a soft `.wav` chime when the notification fires. Can be disabled via `NOTIFICATION_SOUND = False` in `config.py` or during setup.
- **Auto-installs dependencies** — `setup.py` detects missing packages and offers to install them for you.
- **Bilingual** — all notifications and weather comments are available in English and Chinese (中文).
- **Flexible schedule** — weekdays only, every day, or a custom list of days.

---

## Command-line flags

```bash
python main.py --test           # Send a test notification immediately and exit
python main.py --test-weather   # Fetch weather, print diagnostics, send a test notification, and exit
python main.py --debug          # Print timezone/sunset diagnostics and exit
```

---

## Troubleshooting

**No notification appears**
- Windows: Settings → System → Notifications → make sure Python is allowed
- macOS: System Preferences → Notifications → Python
- Linux: install `libnotify-bin` (`sudo apt install libnotify-bin`)

**Wrong sunset time**
- Check your coordinates in `config.py`
- Make sure your system clock and timezone are correct

**`install_autostart.py` says "Access is denied" on Windows**
- Run PowerShell as Administrator, then try again

**Sound doesn't play on Linux**
- Install `alsa-utils`: `sudo apt install alsa-utils`

**Weather comment doesn't appear**
- The weather fetch is best-effort — if it fails (e.g. no internet), the notification still fires without it

---

## Why I made this

San Diego sunsets are genuinely beautiful.
I kept missing them because I was staring at my screen.

Now I don't. 🐸

---

## Contributing

Found a bug or want to add more languages / message packs? Open an issue or PR!

This project was built with [Claude Code](https://claude.ai/code).

---

## License

MIT — do whatever you want with it.
