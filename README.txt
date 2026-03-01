╔══════════════════════════════════════════════════════════════╗
║          🎮  Roblox Username Generator  🎮                   ║
║                      README / ИНСТРУКЦИЯ                     ║
╚══════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📁  СТРУКТУРА ФАЙЛОВ / FILE STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Все файлы должны лежать в ОДНОЙ папке / All files must be in ONE folder:

  📁 папка/
    ├── roblox_username_gen.py   ← главный скрипт / main script
    ├── config.json              ← настройки / settings
    ├── requirements.txt         ← зависимости / dependencies
    └── README.txt               ← этот файл / this file

  После запуска появится / After launch will appear:
    └── free_usernames.txt       ← свободные юзернеймы / free usernames

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚙️  УСТАНОВКА PYTHON / INSTALLING PYTHON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Требуется Python 3.6 или новее / Requires Python 3.6 or newer.

  🔗 Скачать / Download: https://www.python.org/downloads/

  ⚠️  При установке на Windows обязательно поставь галочку:
      "Add Python to PATH" / Check "Add Python to PATH" on install!

  Проверить версию / Check version:
    > python --version

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🚀  КАК ЗАПУСТИТЬ / HOW TO RUN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [Windows]
    1. Открой папку со скриптом
    2. Зажми Shift + ПКМ в пустом месте папки
    3. Выбери "Открыть окно PowerShell здесь" или "Открыть терминал"
    4. Введи команду:
         python roblox_username_gen.py

  [Mac / Linux]
    1. Открой Терминал
    2. Перейди в папку:
         cd /путь/до/папки
    3. Запусти:
         python3 roblox_username_gen.py

  ❌ НЕ запускай двойным кликом — окно сразу закроется!
  ❌ Do NOT run by double-clicking — the window will close instantly!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🛠️  НАСТРОЙКИ / SETTINGS  (config.json)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Открой config.json любым текстовым редактором (Блокнот, VS Code и т.д.)
  Open config.json with any text editor (Notepad, VS Code, etc.)

  Параметр / Parameter       Описание / Description
  ─────────────────────────────────────────────────────────────
  "total_length": 5          Длина юзернейма / Username length
  "count": 20                Сколько проверить / How many to check
  "use_numbers": true        Использовать цифры / Use digits (0-9)
  "use_letters": true        Использовать буквы / Use letters (a-zA-Z)
  "delay_seconds": 1.0       Пауза между запросами / Delay between requests
                             ⚠️  Не меньше 0.5 без прокси!
                             ⚠️  Not less than 0.5 without proxy!
  "save_file": "..."         Файл для сохранения / Output file name

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔀  РЕЖИМ ПРОКСИ / PROXY MODE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  При запуске скрипт спросит / On launch the script will ask:
    "Хотите использовать прокси? / Do you want to use a proxy? (y/n)"

  Если y / If y:
    - Введи адрес прокси / Enter proxy address:
        Формат / Format:  ip:port
        Пример / Example: 123.45.67.89:8080
        С паролем / With auth: user:pass@123.45.67.89:8080
    - Задержка автоматически = 0.3 сек / Delay auto-set to 0.3 sec
    - Количество = 9999999999 (работает до Ctrl+C / runs until Ctrl+C)

  Если n / If n:
    - Используются настройки из config.json / Uses settings from config.json

  ⚠️  Бесплатные прокси часто нестабильны и уже забанены Roblox.
  ⚠️  Free proxies are often unstable and already banned by Roblox.
  ✅  Платные приватные прокси работают надёжно.
  ✅  Paid private proxies work reliably.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💾  РЕЗУЛЬТАТЫ / RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Свободные юзернеймы сохраняются в файл (по умолчанию free_usernames.txt).
  Free usernames are saved to a file (default: free_usernames.txt).

  Каждый новый запуск ДОПИСЫВАЕТ в конец файла, не перезаписывает.
  Each new run APPENDS to the file, does not overwrite.

  Нажми Ctrl+C чтобы остановить в любой момент — результаты сохранятся.
  Press Ctrl+C to stop at any time — results will be saved.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ❓  СТАТУСЫ / STATUSES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅ Свободен / Free       — юзернейм свободен, сохранён в файл
                             username is free, saved to file
  ❌ Занят / Taken         — юзернейм уже занят
                             username is already taken
  ⚠️  Нет ответа / No resp — нет интернета, прокси не работает
                             или Roblox временно заблокировал запросы
                             no internet, proxy not working,
                             or Roblox temporarily blocked requests

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📦  ЗАВИСИМОСТИ / DEPENDENCIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Сторонних пакетов нет — pip install не нужен!
  No third-party packages — no pip install needed!

  Скрипт использует только встроенные модули Python:
  Script uses only built-in Python modules:
    random, string, urllib, json, sys, time, os

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
