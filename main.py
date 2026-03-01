import random
import string
import urllib.request
import json
import sys
import time
import os

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Файл {CONFIG_FILE} не найден! / {CONFIG_FILE} not found!")
        sys.exit(1)
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        required = ["total_length", "count", "use_numbers", "use_letters", "delay_seconds", "save_file"]
        for key in required:
            if key not in cfg:
                print(f"❌ В config.json отсутствует поле: '{key}' / Missing field in config.json: '{key}'")
                sys.exit(1)
        return cfg
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка в config.json / Error in config.json: {e}")
        sys.exit(1)


def T(lang, eng, ru):
    return eng if lang == "eng" else ru


def choose_language():
    print()
    print("  What language do you prefer? / Какой язык вы предпочитаете?")
    print("  (eng / ru)")
    print()
    while True:
        lang = input("  >>> ").strip().lower()
        if lang in ("eng", "ru"):
            return lang
        print("  Please enter 'eng' or 'ru' / Введите 'eng' или 'ru'")


def choose_proxy(lang):
    print()
    print(f"  {T(lang, 'Do you want to use a proxy? (y/n)', 'Хотите использовать прокси? (y/n)')}")
    print(f"  {T(lang, 'With proxy: speed is maximized, count set to 9999999999', 'С прокси: скорость максимальная, количество = 9999999999')}")
    print()
    while True:
        choice = input("  >>> ").strip().lower()
        if choice in ("y", "n"):
            break
        print(f"  {T(lang, 'Please enter y or n', 'Введите y или n')}")

    if choice == "n":
        return None, False

    print()
    print(f"  {T(lang, 'Enter proxy address (format: ip:port or user:pass@ip:port):', 'Введите адрес прокси (формат: ip:port или user:pass@ip:port):')}")
    print(f"  {T(lang, 'Example: 123.45.67.89:8080', 'Пример: 123.45.67.89:8080')}")
    print()
    while True:
        proxy = input("  >>> ").strip()
        if proxy:
            # Проверяем базовый формат
            if ":" in proxy:
                return proxy, True
        print(f"  {T(lang, 'Invalid format! Example: 123.45.67.89:8080', 'Неверный формат! Пример: 123.45.67.89:8080')}")


def choose_prefix(lang, total_length):
    print()
    print(f"  {T(lang, 'Choose prefix type:', 'Выберите тип префикса:')}")
    print(f"  1 — {T(lang, 'Enter your own prefix (e.g. user, xX, cool)', 'Ввести свой префикс (например user, xX, cool)')}")
    print(f"  2 — {T(lang, 'Random letters as prefix', 'Случайные буквы в качестве префикса')}")
    print()
    while True:
        choice = input("  >>> ").strip()
        if choice == "1":
            print()
            prompt = T(lang, "  Enter prefix: ", "  Введите префикс: ")
            while True:
                prefix = input(prompt).strip()
                if not prefix:
                    print(f"  {T(lang, 'Prefix cannot be empty!', 'Префикс не может быть пустым!')}")
                    continue
                if len(prefix) >= total_length:
                    print(f"  {T(lang, f'Prefix must be shorter than {total_length} characters!', f'Префикс должен быть короче {total_length} символов!')}")
                    continue
                return prefix, None
        elif choice == "2":
            print()
            prompt = T(lang,
                f"  How many random letters for prefix? (1-{total_length - 1}): ",
                f"  Сколько случайных букв в префиксе? (1-{total_length - 1}): ")
            while True:
                try:
                    n = int(input(prompt).strip())
                    if 1 <= n <= total_length - 1:
                        return None, n
                    print(f"  {T(lang, f'Enter a number from 1 to {total_length - 1}', f'Введите число от 1 до {total_length - 1}')}")
                except ValueError:
                    print(f"  {T(lang, 'Enter a number!', 'Введите число!')}")
        else:
            print(f"  {T(lang, 'Enter 1 or 2', 'Введите 1 или 2')}")


def generate_username(prefix, random_prefix_len, total_length, use_letters, use_numbers):
    charset = ""
    if use_letters:
        charset += string.ascii_letters
    if use_numbers:
        charset += string.digits
    if not charset:
        print("❌ Error / Ошибка: enable at least use_numbers or use_letters in config.json!")
        sys.exit(1)

    if random_prefix_len:
        actual_prefix = "".join(random.choices(string.ascii_letters, k=random_prefix_len))
        suffix_len = total_length - random_prefix_len
    else:
        actual_prefix = prefix
        suffix_len = total_length - len(prefix)

    if suffix_len < 0:
        suffix_len = 0

    return actual_prefix + "".join(random.choices(charset, k=suffix_len))


def check_username(username, proxy=None):
    url = (
        "https://auth.roblox.com/v1/usernames/validate"
        f"?request.username={username}&request.birthday=2000-01-01"
    )
    try:
        if proxy:
            # Добавляем схему если её нет
            proxy_url = proxy if proxy.startswith("http") else f"http://{proxy}"
            proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
            opener = urllib.request.build_opener(proxy_handler)
        else:
            opener = urllib.request.build_opener()

        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with opener.open(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())
            return data.get("code") == 0
    except Exception:
        return None


def save_username(username, save_file):
    with open(save_file, "a", encoding="utf-8") as f:
        f.write(username + "\n")


def main():
    cfg = load_config()

    TOTAL_LENGTH  = cfg["total_length"]
    COUNT         = cfg["count"]
    USE_NUMBERS   = cfg["use_numbers"]
    USE_LETTERS   = cfg["use_letters"]
    DELAY_SECONDS = cfg["delay_seconds"]
    SAVE_FILE     = cfg["save_file"]

    lang = choose_language()
    proxy, use_proxy = choose_proxy(lang)
    prefix, random_prefix_len = choose_prefix(lang, TOTAL_LENGTH)

    # Прокси-режим: минимальная задержка и огромный count
    if use_proxy:
        DELAY_SECONDS = 0.3
        COUNT = 9999999999

    free_count  = 0
    taken_count = 0
    error_count = 0

    existing = 0
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            existing = sum(1 for line in f if line.strip())

    if random_prefix_len:
        prefix_display = T(lang, f"Random ({random_prefix_len} letters)", f"Случайный ({random_prefix_len} букв)")
    else:
        prefix_display = f'"{prefix}"'

    proxy_display = proxy if use_proxy else T(lang, "Disabled", "Отключён")

    print()
    print("╔══════════════════════════════════════════════╗")
    print("║     🎮  Roblox Username Generator  🎮        ║")
    print("╠══════════════════════════════════════════════╣")
    print(f"║  {T(lang, 'Prefix', 'Префикс'):<10}: {prefix_display:<33}║")
    print(f"║  {T(lang, 'Length', 'Длина'):<10}: {str(TOTAL_LENGTH):<33}║")
    print(f"║  {T(lang, 'Checks', 'Проверок'):<10}: {str(COUNT):<33}║")
    print(f"║  {T(lang, 'Delay', 'Пауза'):<10}: {str(DELAY_SECONDS) + T(lang, ' sec', ' сек'):<33}║")
    print(f"║  {T(lang, 'Proxy', 'Прокси'):<10}: {proxy_display:<33}║")
    print(f"║  {T(lang, 'File', 'Файл'):<10}: {SAVE_FILE:<33}║")
    if existing:
        already = T(lang, f"{existing} usernames already in file", f"{existing} юзернеймов уже в файле")
        print(f"║  {already:<44}║")
    print("╚══════════════════════════════════════════════╝")
    print()

    if use_proxy:
        print(f"  🔀 {T(lang, 'Proxy mode: running until stopped (Ctrl+C)', 'Прокси-режим: работает до остановки (Ctrl+C)')}")
        print()

    for i in range(1, COUNT + 1):
        name = generate_username(prefix, random_prefix_len, TOTAL_LENGTH, USE_LETTERS, USE_NUMBERS)
        status = check_username(name, proxy)

        if status is True:
            label = T(lang, "✅ Free", "✅ Свободен")
            save_username(name, SAVE_FILE)
            free_count += 1
        elif status is False:
            label = T(lang, "❌ Taken", "❌ Занят")
            taken_count += 1
        else:
            label = T(lang, "⚠️  No response", "⚠️  Нет ответа")
            error_count += 1

        progress = int((i % 1000) / 1000 * 20) if use_proxy else int((i / COUNT) * 20)
        bar = "█" * progress + "░" * (20 - progress)
        count_display = "∞" if use_proxy else str(COUNT)

        print(f"  {i:>7}/{count_display:<12} [{bar}]  {name:<22} {label}")

        if i < COUNT:
            time.sleep(DELAY_SECONDS)

    # Финальная статистика (достигается только без прокси)
    print()
    print("══════════════════════════════════════════════")
    print(f"  {T(lang, '✅ Free    :', '✅ Свободных :')} {free_count}")
    print(f"  {T(lang, '❌ Taken   :', '❌ Занятых   :')} {taken_count}")
    print(f"  {T(lang, '⚠️  Errors  :', '⚠️  Ошибок    :')} {error_count}")
    print("──────────────────────────────────────────────")
    if free_count > 0:
        saved_msg = T(lang, f"💾 Saved to: {SAVE_FILE}", f"💾 Сохранено в: {SAVE_FILE}")
        print(f"  {saved_msg}")
    else:
        print(f"  {T(lang, 'No free usernames found.', 'Свободных юзернеймов не найдено.')}")
    print("══════════════════════════════════════════════")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  ⛔ {T('eng', 'Stopped. Found usernames are already saved.', 'Остановлено. Найденные юзернеймы уже сохранены.')}")
    except Exception as e:
        print(f"\n❌ Error / Ошибка: {e}")
