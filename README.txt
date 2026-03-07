╔══════════════════════════════════════════════════════════════╗
║          🎮  Roblox Username Generator  —  README            ║
╚══════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📁  FILES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Put all files in ONE folder:

    main.py              ← run this
    config.json          ← all settings
    README.txt           ← this file

  Created automatically after first run:
    free_usernames.txt   ← free usernames saved here

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚙️  REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Python 3.6+  →  https://www.python.org/downloads/
  ⚠️  Windows: check "Add Python to PATH" during install!
  No pip install needed — only built-in Python modules.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🚀  HOW TO RUN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Windows:
    Shift + Right-click in folder → "Open PowerShell here"
    Type:  python main.py

  ❌ Do NOT double-click — the window will close instantly!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📨  DISCORD WEBHOOK SETUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Discord Webhook and Discord ID are set in config.json
  directly — open it with Notepad and fill in the values.

  ── How to get Webhook URL ─────────────────────────────────

    1. Open Discord
    2. Go to the channel where you want to receive usernames
    3. Click ⚙️ (Edit Channel) → Integrations → Webhooks
    4. Click "New Webhook"
    5. Give it a name (e.g. Roblox Gen)
    6. Click "Copy Webhook URL"
    7. Paste it into config.json:

       "discord_webhook": "https://discord.com/api/webhooks/..."

  ── How to get your Discord User ID (for ping) ─────────────

    1. Open Discord Settings (bottom left ⚙️)
    2. Go to Advanced
    3. Turn ON "Developer Mode"
    4. Close settings
    5. Right-click your own username anywhere in Discord
    6. Click "Copy User ID"
    7. Paste it into config.json:

       "discord_id": "123456789012345678"

  ── Enable Discord output in the app ───────────────────────

    After filling config.json:
    1. Run main.py
    2. Scroll down in the left panel to OUTPUT
    3. Check the box "📨 Send to Discord webhook"
    4. Click "💾 Save config"

  When a free username is found you will receive:
    • A ping (@YourName) if discord_id is set
    • An embed card with the username in a copyable code block

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🖥️  GUI SETTINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  GENERATION
    Username length     Total characters in each username
    Count per batch     How many to check before cooldown
    Delay (seconds)     Wait between each request
    Cooldown (sec)      Wait after each batch
    Threads             Parallel checks (1-5)
    Auto-pause errors   Pause if N errors in a row

  GENERATION MODE
    Standard            Prefix + random characters
    Pattern             e.g. LLDD → KfX3  (L=letter D=digit)
                        U=uppercase  l=lowercase  _=underscore
    Readable            Alternating vowels/consonants: KaRoB
    Underscore          e.g. cool_x1
    Word-based          e.g. fire42, wolf9

  OUTPUT
    📄 Save to file     Append to free_usernames.txt
    📨 Discord webhook  Send to Discord (set URL in config.json)

  NOTIFICATIONS
    🔔 Sound            Plays a sound when free username found
    🌐 Open Roblox      Opens Roblox register page automatically

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔄  HOW BATCHES WORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Generator runs in a loop forever until you press ■ STOP:

    Batch #1 → checks N usernames
    → waits cooldown seconds
    Batch #2 → checks N usernames
    → ... and so on

  Safe settings without proxy:
    count: 10  |  delay: 2.0s  |  cooldown: 60s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅  FOUND TAB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Shows all free usernames found this session.
  Each row has:
    📋 Copy    — copies username to clipboard
    🗑         — removes from list
  📥 Export CSV — saves the full list as a .csv file

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ❓  LOG COLOURS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🟢 Green        Free username (standard)
  🟡 Gold         Free username (≤4 chars — very rare!)
  🟣 Purple       Free username (5 chars — rare)
  🔴 Red          Taken
  🟡 Yellow       No response / error

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
