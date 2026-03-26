# 🌅 sunset-notifier

A tiny background script that reminds you to go watch the sunset.

Runs on Windows, macOS, and Linux. No internet required. No API key. Completely free.

---

## What it does

Every day, a few minutes before sunset, your desktop shows a notification like:

> 🐸 Sunset in 5 min — 19:23
> 今天的日落是限定款，先到先得！

With a soft chime. Then it goes back to sleep until tomorrow.

Messages rotate randomly every day — you never know which one you'll get.

---

## Quick start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR-USERNAME/sunset-notifier.git
cd sunset-notifier
```

### 2. Install and configure

```bash
pip install -r requirements.txt
python setup.py
```

`setup.py` will ask you:
- Your location (city name or latitude/longitude)
- Which days to remind you (weekdays / every day / custom)
- How many minutes before sunset
- Notification language (English / 中文)

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
```

Want to add your own messages? Edit `MESSAGES_EN` or `MESSAGES_ZH` in `config.py` —
one message is picked randomly each day.

---

## Requirements

- Python 3.8+
- Works on Windows, macOS, Linux
- No internet connection needed at runtime
- No API keys, no accounts, no subscriptions

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
