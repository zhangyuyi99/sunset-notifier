"""Platform-specific autostart installer for sunset-notifier."""
import os
import platform
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_PY = os.path.join(SCRIPT_DIR, "main.py")
PYTHON_EXE = sys.executable


def _pythonw_exe() -> str:
    """Return path to pythonw.exe on Windows (no console window)."""
    # sys.executable is typically C:\...\python.exe; swap the binary name.
    exe_dir = os.path.dirname(sys.executable)
    pythonw = os.path.join(exe_dir, "pythonw.exe")
    if os.path.isfile(pythonw):
        return pythonw
    # Fallback: replace trailing 'python.exe' in the path string.
    if sys.executable.lower().endswith("python.exe"):
        candidate = sys.executable[:-10] + "pythonw.exe"
        if os.path.isfile(candidate):
            return candidate
    # Last resort: rely on PATH.
    return "pythonw.exe"


def install_windows():
    task_name = "SunsetNotifier"
    pythonw = _pythonw_exe()
    cmd = [
        "schtasks", "/create",
        "/tn", task_name,
        "/tr", f'"{pythonw}" "{MAIN_PY}"',
        "/sc", "onlogon",
        "/rl", "limited",
        "/f",  # overwrite if exists
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Task Scheduler entry '{task_name}' created.")
            print(f"  Executable: {pythonw}")
            print(f"  main.py will run automatically at each login (no terminal window).")
        else:
            print(f"✗ Failed to create Task Scheduler entry.")
            print(result.stderr.strip())
    except FileNotFoundError:
        print("✗ schtasks not found. Are you running on Windows?")


def install_macos():
    plist_dir = os.path.expanduser("~/Library/LaunchAgents")
    os.makedirs(plist_dir, exist_ok=True)
    plist_path = os.path.join(plist_dir, "com.sunset-notifier.plist")

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.sunset-notifier</string>
    <key>RunAtLoad</key>
    <true/>
    <key>ProgramArguments</key>
    <array>
        <string>{PYTHON_EXE}</string>
        <string>{MAIN_PY}</string>
    </array>
    <key>StandardOutPath</key>
    <string>{os.path.join(SCRIPT_DIR, 'sunset-notifier.log')}</string>
    <key>StandardErrorPath</key>
    <string>{os.path.join(SCRIPT_DIR, 'sunset-notifier.log')}</string>
</dict>
</plist>
"""
    with open(plist_path, "w") as f:
        f.write(plist_content)

    try:
        subprocess.run(["launchctl", "load", plist_path], check=True)
        print(f"✓ LaunchAgent installed at {plist_path}")
        print(f"  main.py will run automatically at each login.")
    except subprocess.CalledProcessError as e:
        print(f"✗ launchctl load failed: {e}")
    except FileNotFoundError:
        print("✗ launchctl not found. Are you running on macOS?")


def install_linux():
    autostart_dir = os.path.expanduser("~/.config/autostart")
    os.makedirs(autostart_dir, exist_ok=True)
    desktop_path = os.path.join(autostart_dir, "sunset-notifier.desktop")

    desktop_content = f"""[Desktop Entry]
Type=Application
Name=Sunset Notifier
Comment=Remind you to watch the sunset
Exec={PYTHON_EXE} {MAIN_PY}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
    with open(desktop_path, "w") as f:
        f.write(desktop_content)

    print(f"✓ Autostart entry written to {desktop_path}")
    print(f"  main.py will run automatically at next desktop login.")


def main():
    system = platform.system()
    print(f"Detected platform: {system}\n")

    if system == "Windows":
        install_windows()
    elif system == "Darwin":
        install_macos()
    elif system == "Linux":
        install_linux()
    else:
        print(f"✗ Unsupported platform: {system}")
        print("  Manually add the following to your startup programs:")
        print(f"  {PYTHON_EXE} {MAIN_PY}")
        sys.exit(1)


if __name__ == "__main__":
    main()
