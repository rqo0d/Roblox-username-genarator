╔══════════════════════════════════════════════════════════════╗
║          🎮  Roblox Username Generator  🎮                   ║
║                          README                              ║
╚══════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📁  FILE STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  All files must be placed in ONE folder:

  📁 folder/
    ├── roblox_username_gen.py   ← main script
    ├── config.json              ← settings
    ├── requirements.txt         ← dependencies
    └── README.txt               ← this file

  After launch, this file will appear:
    └── free_usernames.txt       ← saved free usernames

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚙️  INSTALLING PYTHON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Requires Python 3.6 or newer.

  🔗 Download: https://www.python.org/downloads/

  ⚠️  On Windows, make sure to check "Add Python to PATH"
      during installation, otherwise the script won't run!

  Check your version:
    > python --version

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🚀  HOW TO RUN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [Windows]
    1. Open the folder with the script
    2. Hold Shift + Right-click on an empty area in the folder
    3. Select "Open PowerShell window here" or "Open Terminal"
    4. Type the command:
         python roblox_username_gen.py

  [Mac / Linux]
    1. Open Terminal
    2. Navigate to the folder:
         cd /path/to/folder
    3. Run:
         python3 roblox_username_gen.py

  ❌ Do NOT run by double-clicking — the window will close instantly!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🛠️  SETTINGS  (config.json)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Open config.json with any text editor (Notepad, VS Code, etc.)
  and change the values as you like.

  Parameter                  Description
  ─────────────────────────────────────────────────────────────
  "total_length": 5          Total length of the username
  "count": 20                How many usernames to check
  "use_numbers": true        Include digits (0-9)
  "use_letters": true        Include letters (a-zA-Z)
  "delay_seconds": 1.0       Delay between requests in seconds
                             ⚠️  Do not set below 0.5 without proxy!
  "save_file": "..."         File name to save free usernames

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔀  PROXY MODE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  On launch the script will ask:
    "Do you want to use a proxy? (y/n)"

  If y:
    - Enter your proxy address:
        Format:        ip:port
        Example:       123.45.67.89:8080
        With auth:     user:pass@123.45.67.89:8080
    - Delay is automatically set to 0.3 sec (minimum)
    - Count is set to 9999999999 (runs until you press Ctrl+C)

  If n:
    - Settings from config.json are used as normal

  ⚠️  Free proxies are often unstable and already banned by Roblox.
  ✅  Paid private proxies work reliably and reduce ban risk.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💾  RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Free usernames are automatically saved to free_usernames.txt
  (or whatever file name you set in config.json).

  Each new run APPENDS to the file — nothing gets overwritten.

  Press Ctrl+C to stop at any time — all found usernames are
  already saved and will not be lost.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ❓  STATUS MEANINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅ Free          Username is available — saved to file
  ❌ Taken         Username is already registered
  ⚠️  No response  No internet connection, proxy not working,
                   or Roblox temporarily blocked the requests

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📦  DEPENDENCIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  No third-party packages required — no pip install needed!

  The script only uses built-in Python modules:
    random, string, urllib, json, sys, time, os

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
