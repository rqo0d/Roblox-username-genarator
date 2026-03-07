╔══════════════════════════════════════════════════════════════╗
║          🎮  Roblox Username Generator  —  README            ║
╚══════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📁  FILES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Put all files in ONE folder:

    main.py   ← run this
    config.json              ← settings (auto-saved)
    README.txt               ← this file

  After first run:
    free_usernames.txt       ← free usernames saved here

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚙️  REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Python 3.6+  →  https://www.python.org/downloads/

  ⚠️  Windows: check "Add Python to PATH" during install!

  No pip install needed — only built-in Python modules are used.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🚀  HOW TO RUN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Windows:
    1. Shift + Right-click in the folder → "Open PowerShell here"
    2. Type:  python main.py

  Mac / Linux:
    1. Open Terminal, navigate to folder:  cd /path/to/folder
    2. Type:  python3 main.py

  ❌ Do NOT double-click — the window will close instantly!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🖥️  GUI — LEFT PANEL SETTINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  GENERATION
  ───────────
  Username length      Total length of each generated username
  Count                How many usernames to check per batch
  Delay (seconds)      Wait between each request (min 0.5 recommended)
  Cooldown (seconds)   Wait after each batch before starting the next
  Use letters          Include a-z and A-Z in usernames
  Use numbers          Include 0-9 in usernames

  PREFIX
  ───────
  Custom prefix        Fixed text at the start (e.g. user, xX, pro)
  Random prefix        Random letters at the start each time
  Prefix length        How many random letters to use as prefix

  PROXY
  ──────
  Enable proxy         Route requests through a proxy server
  Address              ip:port  or  user:pass@ip:port
                       ⚠️ Free proxies may already be banned by Roblox
                       ✅ Paid private proxies work reliably

  OUTPUT
  ───────
  📄 Save to file      Append free usernames to a .txt file
  📨 Send to Discord   Send each free username to a Discord channel
                       via webhook (see Discord Webhook section below)
  💡 Both options can be enabled at the same time

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📨  DISCORD WEBHOOK SETUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  How to create a webhook:
    1. Open Discord → go to the channel you want
    2. Channel Settings (⚙️) → Integrations → Webhooks
    3. Click "New Webhook" → Copy Webhook URL
    4. Paste the URL into the webhook field in the app

  How to get your Discord User ID (for ping):
    1. Discord Settings → Advanced → turn ON Developer Mode
    2. Right-click your username anywhere → Copy User ID
    3. Paste the ID into the Discord User ID field in the app

  When a free username is found, you will receive:
    • A ping notification (@YourName)
    • An embed card with the username in a code block
      so you can copy it with one click

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔄  HOW BATCHES WORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  The generator runs in a loop — it never stops on its own:

    Batch #1 (checks N usernames)
      → waits Cooldown seconds
    Batch #2 (checks N usernames)
      → waits Cooldown seconds
    ... and so on until you press ■ STOP

  This prevents IP bans by spacing out requests.
  Recommended safe settings (no proxy):

    Count:    10
    Delay:    2.0 sec
    Cooldown: 60 sec

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ❓  LOG STATUSES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅  Free          Username is available — saved/sent
  ❌  Taken         Username is already registered
  ⚠️   No response  No internet, proxy issue, or Roblox rate limit

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💾  CONFIG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  All settings are saved in config.json automatically.
  You can also click "💾 Save config" in the app at any time.
  The Discord webhook URL and User ID are saved automatically
  as you type — no need to press Save.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
