import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import urllib.request
import json
import time
import os
import threading

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "total_length": 5,
    "count": 10,
    "use_numbers": True,
    "use_letters": True,
    "delay_seconds": 2.0,
    "cooldown_seconds": 60,
    "save_file": "free_usernames.txt",
    "discord_webhook": ""
}

BG       = "#0d0d0d"
BG2      = "#141414"
BG3      = "#1e1e1e"
CARD     = "#181818"
BORDER   = "#2a2a2a"
ACCENT   = "#e8151b"
ACCENT2  = "#ff4444"
TEXT     = "#f0f0f0"
TEXT_DIM = "#555555"
TEXT_MID = "#888888"
GREEN    = "#22c55e"
RED_C    = "#ef4444"
YELLOW   = "#f59e0b"
FM       = ("Segoe UI", 10)
FB       = ("Segoe UI", 10, "bold")
FS       = ("Segoe UI", 9)
FMONO    = ("Consolas", 10)


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        r = DEFAULT_CONFIG.copy()
        r.update(cfg)
        return r
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config_file(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def generate_username(prefix, rand_len, total_length, use_letters, use_numbers):
    charset = ""
    if use_letters:
        charset += string.ascii_letters
    if use_numbers:
        charset += string.digits
    if not charset:
        charset = string.ascii_letters
    if rand_len:
        p = "".join(random.choices(string.ascii_letters, k=rand_len))
        s = max(0, total_length - rand_len)
    else:
        p = prefix
        s = max(0, total_length - len(prefix))
    return p + "".join(random.choices(charset, k=s))


def check_username(username, proxy=None):
    url = (
        "https://auth.roblox.com/v1/usernames/validate"
        f"?request.username={username}&request.birthday=2000-01-01"
    )
    try:
        if proxy:
            pu = proxy if proxy.startswith("http") else f"http://{proxy}"
            opener = urllib.request.build_opener(
                urllib.request.ProxyHandler({"http": pu, "https": pu}))
        else:
            opener = urllib.request.build_opener()
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with opener.open(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())
            return data.get("code") == 0
    except Exception:
        return None


def append_free(username, save_file):
    with open(save_file, "a", encoding="utf-8") as f:
        f.write(username + "\n")


def send_to_discord(webhook_url, username, discord_id=None):
    if not webhook_url or not webhook_url.startswith("https://discord"):
        return True, "skipped (no webhook)"
    try:
        mention = f"<@{discord_id}> " if discord_id else ""
        body = {
            "content": mention if mention else None,
            "embeds": [{
                "title": "🎮 Free Roblox Username Found!",
                "description": f"```\n{username}\n```",
                "color": 0x22c55e,
                "footer": {"text": "Roblox Username Generator"}
            }]
        }
        # Remove content key if no mention
        if not body["content"]:
            del body["content"]
        payload = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            webhook_url.strip(), data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            }, method="POST")
        with urllib.request.urlopen(req, timeout=8) as resp:
            ok = resp.status in (200, 204)
            return ok, f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"URL error: {e.reason}"
    except Exception as e:
        return False, str(e)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Roblox Username Generator")
        self.geometry("900x700")
        self.minsize(820, 600)
        self.configure(bg=BG)

        self._running    = False
        self.free_count  = 0
        self.taken_count = 0
        self.error_count = 0
        self.total_done  = 0

        self._build()
        self._load_cfg()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        cv = tk.Canvas(hdr, width=14, height=14, bg=BG, highlightthickness=0)
        cv.create_oval(2, 2, 12, 12, fill=ACCENT, outline="")
        cv.pack(side="left", padx=(0, 10))
        tk.Label(hdr, text="Roblox Username Generator",
                 font=("Segoe UI", 18, "bold"), bg=BG, fg=TEXT).pack(side="left")
        self.lbl_status = tk.Label(hdr, text="● Ready", font=FS, bg=BG, fg=GREEN)
        self.lbl_status.pack(side="right")
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=24, pady=12)

        # Columns
        cols = tk.Frame(self, bg=BG)
        cols.pack(fill="both", expand=True, padx=24)

        # Left — scrollable
        left_outer = tk.Frame(cols, bg=BG, width=284)
        left_outer.pack(side="left", fill="y", padx=(0, 10))
        left_outer.pack_propagate(False)
        left_canvas = tk.Canvas(left_outer, bg=BG, highlightthickness=0)
        left_canvas.pack(side="left", fill="both", expand=True)
        left_sb = tk.Scrollbar(left_outer, orient="vertical",
                               command=left_canvas.yview,
                               bg=BG3, troughcolor=BG, width=6)
        left_sb.pack(side="right", fill="y")
        left_canvas.configure(yscrollcommand=left_sb.set)
        self.left = tk.Frame(left_canvas, bg=BG)
        _win_id = left_canvas.create_window((0, 0), window=self.left, anchor="nw")
        def _on_canvas_resize(e, cid=_win_id, cv=left_canvas):
            cv.itemconfig(cid, width=e.width)
        left_canvas.bind("<Configure>", _on_canvas_resize)
        def _on_inner_resize(e, cv=left_canvas):
            cv.configure(scrollregion=cv.bbox("all"))
        self.left.bind("<Configure>", _on_inner_resize)
        def _mousewheel(e, cv=left_canvas):
            # Only scroll if mouse is over the left panel
            x, y = self.winfo_pointerxy()
            w = self.winfo_containing(x, y)
            # Walk up widget tree to check if it's inside left_canvas
            try:
                while w:
                    if w == left_canvas or w == self.left:
                        cv.yview_scroll(int(-1 * (e.delta / 120)), "units")
                        break
                    w = w.master
            except Exception:
                pass
        self.bind_all("<MouseWheel>", _mousewheel)

        # Right
        self.right = tk.Frame(cols, bg=BG)
        self.right.pack(side="left", fill="both", expand=True)

        self._build_left()
        self._build_right()

        # Bottom bar
        bot = tk.Frame(self, bg=BG2, highlightbackground=BORDER, highlightthickness=1)
        bot.pack(fill="x", side="bottom")
        btns = tk.Frame(bot, bg=BG2)
        btns.pack(padx=24, pady=12)
        self.btn_start = tk.Button(btns, text="▶  START",
                                   font=("Segoe UI", 11, "bold"),
                                   bg=ACCENT, fg="white",
                                   activebackground=ACCENT2, activeforeground="white",
                                   relief="flat", bd=0, cursor="hand2",
                                   padx=28, pady=10, command=self._start)
        self.btn_start.pack(side="left", padx=(0, 8))
        self.btn_stop = tk.Button(btns, text="■  STOP",
                                  font=("Segoe UI", 11, "bold"),
                                  bg=BG3, fg=TEXT_DIM,
                                  activebackground=BORDER, activeforeground=TEXT,
                                  relief="flat", bd=0, cursor="hand2",
                                  padx=28, pady=10, state="disabled",
                                  command=self._stop)
        self.btn_stop.pack(side="left", padx=(0, 20))
        tk.Button(btns, text="💾  Save config", font=FS,
                  bg=BG3, fg=TEXT_MID,
                  activebackground=BORDER, activeforeground=TEXT,
                  relief="flat", bd=0, cursor="hand2",
                  padx=12, pady=10, command=self._save_cfg).pack(side="left")
        self.lbl_footer = tk.Label(btns, text="", font=FS, bg=BG2, fg=GREEN)
        self.lbl_footer.pack(side="right", padx=10)

    def _build_left(self):
        # GENERATION
        self._section(self.left, "GENERATION")
        row = tk.Frame(self.left, bg=CARD)
        row.pack(fill="x")
        self._field_label(row, "Username length")
        self.var_len = tk.IntVar(value=5)
        self._spinbox(row, self.var_len, 3, 20)
        self._field_label(row, "Count")
        self.var_count = tk.IntVar(value=10)
        self._spinbox(row, self.var_count, 1, 9999)
        self._field_label(row, "Delay (seconds)")
        self.var_delay = tk.DoubleVar(value=2.0)
        tk.Spinbox(row, from_=0.1, to=10.0, increment=0.1,
                   textvariable=self.var_delay, format="%.1f",
                   width=10, font=FMONO, bg=BG3, fg=TEXT,
                   insertbackground=TEXT, buttonbackground=BG3, relief="flat",
                   highlightthickness=1, highlightbackground=BORDER,
                   highlightcolor=ACCENT).pack(anchor="w", padx=14, pady=(0, 4))
        self._field_label(row, "Cooldown after batch (sec)")
        self.var_cooldown = tk.IntVar(value=60)
        tk.Spinbox(row, from_=5, to=300, textvariable=self.var_cooldown,
                   width=10, font=FMONO, bg=BG3, fg=TEXT,
                   insertbackground=TEXT, buttonbackground=BG3, relief="flat",
                   highlightthickness=1, highlightbackground=BORDER,
                   highlightcolor=ACCENT).pack(anchor="w", padx=14, pady=(0, 4))
        self.var_letters = tk.BooleanVar(value=True)
        self.var_numbers = tk.BooleanVar(value=True)
        cb = tk.Frame(self.left, bg=CARD)
        cb.pack(fill="x")
        self._checkbox(cb, "Use letters  (a-z A-Z)", self.var_letters)
        self._checkbox(cb, "Use numbers  (0-9)", self.var_numbers)
        tk.Frame(self.left, bg=CARD, height=10).pack(fill="x")
        tk.Frame(self.left, bg=BORDER, height=1).pack(fill="x")

        # PREFIX
        self._section(self.left, "PREFIX")
        pf = tk.Frame(self.left, bg=CARD)
        pf.pack(fill="x")
        self.var_pmode = tk.StringVar(value="custom")
        tk.Radiobutton(pf, text="Custom prefix", variable=self.var_pmode,
                       value="custom", bg=CARD, fg=TEXT, selectcolor=BG3,
                       activebackground=CARD, activeforeground=TEXT,
                       font=FM, command=self._toggle_prefix
                       ).pack(anchor="w", padx=14, pady=(6, 2))
        tk.Radiobutton(pf, text="Random prefix", variable=self.var_pmode,
                       value="random", bg=CARD, fg=TEXT, selectcolor=BG3,
                       activebackground=CARD, activeforeground=TEXT,
                       font=FM, command=self._toggle_prefix
                       ).pack(anchor="w", padx=14, pady=(0, 8))
        tk.Label(pf, text="Prefix text", bg=CARD, fg=TEXT_MID,
                 font=FS).pack(anchor="w", padx=14)
        self.entry_prefix = tk.Entry(pf, font=FMONO, bg=BG3, fg=TEXT_DIM,
                                     insertbackground=TEXT, relief="flat",
                                     highlightthickness=1,
                                     highlightbackground=BORDER,
                                     highlightcolor=ACCENT)
        self.entry_prefix.pack(fill="x", padx=14, pady=(2, 8))
        self._placeholder(self.entry_prefix, "e.g.  user   xX   pro")
        tk.Label(pf, text="Random prefix length", bg=CARD, fg=TEXT_MID,
                 font=FS).pack(anchor="w", padx=14)
        self.var_rlen = tk.IntVar(value=2)
        self.spin_rlen = tk.Spinbox(pf, from_=1, to=10,
                                    textvariable=self.var_rlen,
                                    width=10, font=FMONO, bg=BG3, fg=TEXT,
                                    insertbackground=TEXT, buttonbackground=BG3,
                                    relief="flat", highlightthickness=1,
                                    highlightbackground=BORDER,
                                    highlightcolor=ACCENT, state="disabled")
        self.spin_rlen.pack(anchor="w", padx=14, pady=(2, 10))
        tk.Frame(self.left, bg=BORDER, height=1).pack(fill="x")

        # PROXY
        self._section(self.left, "PROXY")
        px = tk.Frame(self.left, bg=CARD)
        px.pack(fill="x")
        self.var_proxy_on = tk.BooleanVar(value=False)
        self._checkbox(px, "Enable proxy", self.var_proxy_on, cmd=self._toggle_proxy)
        tk.Label(px, text="Address  (ip:port)", bg=CARD, fg=TEXT_MID,
                 font=FS).pack(anchor="w", padx=14, pady=(4, 0))
        self.entry_proxy = tk.Entry(px, font=FMONO, bg=BG3, fg=TEXT_DIM,
                                    insertbackground=TEXT, relief="flat",
                                    highlightthickness=1,
                                    highlightbackground=BORDER,
                                    highlightcolor=ACCENT, state="disabled")
        self.entry_proxy.pack(fill="x", padx=14, pady=(2, 10))
        self._placeholder(self.entry_proxy, "123.45.67.89:8080")
        tk.Frame(self.left, bg=BORDER, height=1).pack(fill="x")

        # OUTPUT
        self._section(self.left, "OUTPUT")
        op = tk.Frame(self.left, bg=CARD)
        op.pack(fill="x")

        tk.Label(op, text="Where to send free usernames:",
                 bg=CARD, fg=TEXT_MID, font=FS
                 ).pack(anchor="w", padx=14, pady=(10, 6))

        # --- File ---
        self.var_out_file = tk.BooleanVar(value=True)
        tk.Checkbutton(op, text="📄  Save to file",
                       variable=self.var_out_file, bg=CARD, fg=TEXT,
                       selectcolor=BG3, activebackground=CARD,
                       activeforeground=TEXT, font=FM,
                       command=self._toggle_out_file
                       ).pack(anchor="w", padx=14)
        self.entry_file = tk.Entry(op, font=FMONO, bg=BG3, fg=TEXT,
                                   insertbackground=TEXT, relief="flat",
                                   highlightthickness=1,
                                   highlightbackground=BORDER,
                                   highlightcolor=ACCENT)
        self.entry_file.insert(0, "free_usernames.txt")
        self.entry_file.pack(fill="x", padx=28, pady=(3, 10))

        tk.Frame(op, bg=BORDER, height=1).pack(fill="x", padx=14, pady=2)

        # --- Discord ---
        self.var_out_discord = tk.BooleanVar(value=False)
        tk.Checkbutton(op, text="📨  Send to Discord webhook",
                       variable=self.var_out_discord, bg=CARD, fg=TEXT,
                       selectcolor=BG3, activebackground=CARD,
                       activeforeground=TEXT, font=FM,
                       command=self._toggle_out_discord
                       ).pack(anchor="w", padx=14, pady=(8, 0))
        self.entry_webhook = tk.Entry(op, font=FMONO, bg=BG3, fg=TEXT,
                                      insertbackground=TEXT, relief="flat",
                                      highlightthickness=1,
                                      highlightbackground=BORDER,
                                      highlightcolor=ACCENT)
        self.entry_webhook.pack(fill="x", padx=28, pady=(3, 4))
        self._placeholder(self.entry_webhook, "https://discord.com/api/webhooks/...")

        self.lbl_wh_status = tk.Label(op, text="", bg=CARD, fg=TEXT_DIM, font=FS)
        self.lbl_wh_status.pack(anchor="w", padx=28, pady=(0, 4))

        tk.Label(op, text="Your Discord User ID (for ping)",
                 bg=CARD, fg=TEXT_MID, font=FS
                 ).pack(anchor="w", padx=28, pady=(4, 0))
        self.entry_discord_id = tk.Entry(op, font=FMONO,
                                         bg=BG3, fg=TEXT,
                                         insertbackground=TEXT, relief="flat",
                                         highlightthickness=1,
                                         highlightbackground=BORDER,
                                         highlightcolor=ACCENT)
        self.entry_discord_id.pack(fill="x", padx=28, pady=(2, 2))

        # Auto-save ID to config on every keystroke
        def _save_id(e=None):
            val = self.entry_discord_id.get().strip()
            cfg = load_config()
            cfg["discord_id"] = val
            save_config_file(cfg)
        self.entry_discord_id.bind("<KeyRelease>", _save_id)
        self.entry_discord_id.bind("<<Paste>>",    lambda e: self.after(10, _save_id))

        tk.Label(op, text="How to get: Settings > Advanced > Developer Mode ON\nthen right-click your name > Copy User ID",
                 bg=CARD, fg=TEXT_DIM, font=("Segoe UI", 8),
                 justify="left"
                 ).pack(anchor="w", padx=28, pady=(2, 6))

        def _wh_check(e=None):
            raw = self.entry_webhook.get().strip()
            ph  = "https://discord.com/api/webhooks/..."
            if raw and raw != ph:
                if raw.startswith("https://discord.com/api/webhooks/"):
                    self.lbl_wh_status.config(text="✅ Valid webhook", fg=GREEN)
                else:
                    self.lbl_wh_status.config(text="⚠️  Invalid URL", fg=YELLOW)
            else:
                self.lbl_wh_status.config(text="")
        self.entry_webhook.bind("<KeyRelease>", _wh_check)
        self.entry_webhook.bind("<FocusOut>",   _wh_check)

        tk.Label(op, text="💡 Both can be enabled at the same time",
                 bg=CARD, fg=TEXT_DIM, font=("Segoe UI", 8)
                 ).pack(anchor="w", padx=14, pady=(4, 12))

    def _build_right(self):
        # Stats
        stats = tk.Frame(self.right, bg=CARD,
                         highlightbackground=BORDER, highlightthickness=1)
        stats.pack(fill="x", pady=(0, 8))
        self.lbl_free  = self._stat_box(stats, "FREE",    "0", GREEN,  0)
        self.lbl_taken = self._stat_box(stats, "TAKEN",   "0", RED_C,  1)
        self.lbl_err   = self._stat_box(stats, "ERRORS",  "0", YELLOW, 2)
        self.lbl_total = self._stat_box(stats, "CHECKED", "0", TEXT,   3)

        # Progress
        self.prog_var = tk.DoubleVar(value=0)
        sty = ttk.Style()
        sty.theme_use("clam")
        sty.configure("R.Horizontal.TProgressbar",
                      troughcolor=BG3, background=ACCENT,
                      bordercolor=BORDER, lightcolor=ACCENT2, darkcolor=ACCENT)
        ttk.Progressbar(self.right, variable=self.prog_var,
                        style="R.Horizontal.TProgressbar",
                        mode="determinate", maximum=100
                        ).pack(fill="x", ipady=3, pady=(0, 8))

        # Log
        log_wrap = tk.Frame(self.right, bg=CARD,
                            highlightbackground=BORDER, highlightthickness=1)
        log_wrap.pack(fill="both", expand=True)
        top_bar = tk.Frame(log_wrap, bg=CARD)
        top_bar.pack(fill="x", padx=14, pady=(10, 4))
        tk.Label(top_bar, text="LOG", font=("Segoe UI", 8, "bold"),
                 bg=CARD, fg=TEXT_DIM).pack(side="left")
        tk.Button(top_bar, text="Clear", font=FS, bg=BG3, fg=TEXT_DIM,
                  activebackground=BORDER, activeforeground=TEXT,
                  relief="flat", bd=0, cursor="hand2", padx=8, pady=2,
                  command=self._clear_log).pack(side="right")
        tk.Frame(log_wrap, bg=BORDER, height=1).pack(fill="x", padx=14)
        self.log = tk.Text(log_wrap, bg=BG2, fg=TEXT, font=FMONO,
                           relief="flat", bd=0, wrap="none",
                           insertbackground=TEXT, selectbackground=ACCENT,
                           state="disabled", padx=10, pady=8)
        self.log.pack(fill="both", expand=True, padx=8, pady=8)
        sb = tk.Scrollbar(log_wrap, command=self.log.yview, bg=BG3)
        self.log.configure(yscrollcommand=sb.set)
        self.log.tag_config("free",   foreground=GREEN)
        self.log.tag_config("taken",  foreground=RED_C)
        self.log.tag_config("error",  foreground=YELLOW)
        self.log.tag_config("info",   foreground=TEXT_MID)
        self.log.tag_config("header", foreground=ACCENT)
        self.log.tag_config("dim",    foreground=TEXT_DIM)

    # Helpers
    def _section(self, parent, title):
        f = tk.Frame(parent, bg=CARD)
        f.pack(fill="x")
        tk.Label(f, text=title, font=("Segoe UI", 8, "bold"),
                 bg=CARD, fg=TEXT_DIM).pack(anchor="w", padx=14, pady=(12, 4))
        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", padx=14)

    def _field_label(self, parent, text):
        tk.Label(parent, text=text, bg=CARD, fg=TEXT_MID,
                 font=FS).pack(anchor="w", padx=14, pady=(8, 1))

    def _spinbox(self, parent, var, mn, mx):
        tk.Spinbox(parent, from_=mn, to=mx, textvariable=var,
                   width=10, font=FMONO, bg=BG3, fg=TEXT,
                   insertbackground=TEXT, buttonbackground=BG3, relief="flat",
                   highlightthickness=1, highlightbackground=BORDER,
                   highlightcolor=ACCENT).pack(anchor="w", padx=14, pady=(0, 4))

    def _checkbox(self, parent, text, var, cmd=None):
        tk.Checkbutton(parent, text=text, variable=var, bg=CARD, fg=TEXT,
                       selectcolor=BG3, activebackground=CARD,
                       activeforeground=TEXT, font=FM, command=cmd
                       ).pack(anchor="w", padx=14, pady=2)

    def _placeholder(self, entry, ph):
        entry.insert(0, ph)
        entry.config(fg=TEXT_DIM)
        def fi(e):
            if entry.get() == ph:
                entry.delete(0, "end")
                entry.config(fg=TEXT)
        def fo(e):
            if not entry.get():
                entry.insert(0, ph)
                entry.config(fg=TEXT_DIM)
        entry.bind("<FocusIn>",  fi)
        entry.bind("<FocusOut>", fo)

    def _stat_box(self, parent, label, val, color, col):
        parent.columnconfigure(col, weight=1)
        f = tk.Frame(parent, bg=CARD)
        f.grid(row=0, column=col, padx=4, pady=12, sticky="nsew")
        lbl = tk.Label(f, text=val, font=("Segoe UI", 22, "bold"),
                       bg=CARD, fg=color)
        lbl.pack()
        tk.Label(f, text=label, font=("Segoe UI", 7, "bold"),
                 bg=CARD, fg=TEXT_DIM).pack()
        return lbl

    # Toggles
    def _toggle_prefix(self):
        if self.var_pmode.get() == "custom":
            self.entry_prefix.configure(state="normal")
            self.spin_rlen.configure(state="disabled")
        else:
            self.entry_prefix.configure(state="disabled")
            self.spin_rlen.configure(state="normal")

    def _toggle_proxy(self):
        self.entry_proxy.configure(
            state="normal" if self.var_proxy_on.get() else "disabled")

    def _toggle_out_file(self):
        self.entry_file.configure(
            state="normal" if self.var_out_file.get() else "disabled")

    def _toggle_out_discord(self):
        pass  # webhook entry is always editable

    # Config
    def _load_cfg(self):
        cfg = load_config()
        self.var_len.set(cfg.get("total_length", 5))
        self.var_count.set(cfg.get("count", 10))
        self.var_delay.set(cfg.get("delay_seconds", 2.0))
        self.var_cooldown.set(cfg.get("cooldown_seconds", 60))
        self.var_letters.set(cfg.get("use_letters", True))
        self.var_numbers.set(cfg.get("use_numbers", True))
        sf = cfg.get("save_file", "free_usernames.txt")
        self.entry_file.delete(0, "end")
        self.entry_file.insert(0, sf)
        self.entry_file.config(fg=TEXT)
        wh = cfg.get("discord_webhook", "")
        if wh:
            self.entry_webhook.delete(0, "end")
            self.entry_webhook.insert(0, wh)
            self.var_out_discord.set(True)
            self.lbl_wh_status.config(text="✅ Valid webhook", fg=GREEN)
        did = cfg.get("discord_id", "")
        if did:
            self.entry_discord_id.delete(0, "end")
            self.entry_discord_id.insert(0, did)
            self.entry_discord_id.config(fg=TEXT)

    def _save_cfg(self):
        wh = self.entry_webhook.get().strip()
        save_config_file({
            "total_length":    self.var_len.get(),
            "count":           self.var_count.get(),
            "delay_seconds":   round(self.var_delay.get(), 1),
            "cooldown_seconds": self.var_cooldown.get(),
            "use_letters":     self.var_letters.get(),
            "use_numbers":     self.var_numbers.get(),
            "save_file":       self.entry_file.get(),
            "discord_webhook": wh,
            "discord_id": self.entry_discord_id.get().strip()
                          if self.entry_discord_id.get().strip() not in
                             ("e.g.  123456789012345678", "") else ""
        })
        self.lbl_footer.config(text="✓ Config saved!", fg=GREEN)
        self.after(2500, lambda: self.lbl_footer.config(text=""))

    # Log
    def _log(self, text, tag="info"):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _update_stats(self):
        self.lbl_free.config( text=str(self.free_count))
        self.lbl_taken.config(text=str(self.taken_count))
        self.lbl_err.config(  text=str(self.error_count))
        self.lbl_total.config(text=str(self.total_done))

    # Start / Stop
    def _start(self):
        if self._running:
            return

        total_length = self.var_len.get()
        count        = self.var_count.get()
        delay        = round(self.var_delay.get(), 1)
        cooldown     = self.var_cooldown.get()
        use_letters  = self.var_letters.get()
        use_numbers  = self.var_numbers.get()
        use_file     = self.var_out_file.get()
        save_file    = self.entry_file.get().strip() or "free_usernames.txt"
        proxy_on     = self.var_proxy_on.get()
        proxy        = None

        if proxy_on:
            raw = self.entry_proxy.get().strip()
            ph  = "123.45.67.89:8080"
            proxy = raw if raw and raw != ph else None
            delay    = 0.3
            count    = 9_999_999_999
            cooldown = max(5, cooldown)

        if self.var_pmode.get() == "custom":
            raw      = self.entry_prefix.get().strip()
            ph       = "e.g.  user   xX   pro"
            prefix   = "" if (raw == ph or not raw) else raw
            rand_len = None
        else:
            prefix   = None
            rand_len = self.var_rlen.get()

        # Output
        raw_wh  = self.entry_webhook.get().strip()
        use_discord = self.var_out_discord.get()
        webhook = raw_wh if (use_discord and raw_wh
                             and raw_wh.startswith("https://discord")) else None
        raw_id  = self.entry_discord_id.get().strip()
        discord_id = raw_id if (raw_id and raw_id.isdigit()) else None

        if not use_letters and not use_numbers:
            messagebox.showerror("Error", "Enable at least letters or numbers!")
            return
        if not use_file and not webhook:
            messagebox.showerror("Error",
                "Please enable at least one output:\n📄 Save to file   or   📨 Discord webhook")
            return
        if use_discord and not webhook:
            messagebox.showerror("Error",
                "Discord webhook is enabled but the URL is missing or invalid!")
            return

        self.free_count = self.taken_count = self.error_count = self.total_done = 0
        self._update_stats()
        self.prog_var.set(0)
        self._running = True
        self.btn_start.config(state="disabled", bg=BG3, fg=TEXT_DIM)
        self.btn_stop.config(state="normal", bg=ACCENT, fg="white")
        self.lbl_status.config(text="● Running", fg=ACCENT2)

        out_info = []
        if use_file:    out_info.append("📄 file")
        if webhook:     out_info.append("📨 Discord")

        self._log("─" * 54, "dim")
        cnt_label = "∞" if proxy_on else str(count)
        self._log(f"  ▶  length={total_length}  batch={cnt_label}  delay={delay}s  cooldown={cooldown}s", "header")
        self._log(f"  Output: {' + '.join(out_info)}", "info")
        if proxy:
            self._log(f"  🔀 Proxy: {proxy}", "info")
        self._log("─" * 54, "dim")

        threading.Thread(
            target=self._loop,
            args=(prefix, rand_len, total_length, count,
                  use_letters, use_numbers, delay, cooldown,
                  save_file, use_file, webhook, discord_id, proxy, proxy_on),
            daemon=True
        ).start()

    def _stop(self):
        self._running = False

    def _loop(self, prefix, rand_len, total_length, count,
              use_letters, use_numbers, delay, cooldown,
              save_file, use_file, webhook, discord_id, proxy, infinite):
        batch_num = 0
        while self._running:
            batch_num += 1
            self.after(0, self._log,
                       f"  ── Batch #{batch_num} ──", "dim")

            for i in range(1, count + 1):
                if not self._running:
                    break

                name   = generate_username(prefix, rand_len, total_length,
                                           use_letters, use_numbers)
                status = check_username(name, proxy)
                self.total_done += 1

                if status is True:
                    self.free_count += 1
                    tag, icon, label = "free", "✅", "Free"
                    notes = []
                    if use_file:
                        append_free(name, save_file)
                        notes.append("📄")
                    if webhook:
                        ok, disc_msg = send_to_discord(webhook, name, discord_id)
                        if ok:
                            notes.append("📨")
                        else:
                            notes.append(f"⚠️ Discord err: {disc_msg}")
                    note_str = "  " + " ".join(notes) if notes else ""
                    self.after(0, self._log,
                               f"  {icon}  {name:<22} {label}{note_str}", tag)
                elif status is False:
                    self.taken_count += 1
                    tag, icon, label = "taken", "❌", "Taken"
                    self.after(0, self._log,
                               f"  {icon}  {name:<22} {label}", tag)
                else:
                    self.error_count += 1
                    tag, icon, label = "error", "⚠️ ", "No response"
                    self.after(0, self._log,
                               f"  {icon}  {name:<22} {label}", tag)

                self.after(0, self._update_stats)
                pct = (i % 100) if infinite else (i / count * 100)
                self.after(0, self.prog_var.set, pct)

                if i < count and self._running:
                    jitter = delay * random.uniform(0.7, 1.3)
                    time.sleep(jitter)

            if not self._running:
                break

            # Cooldown
            self.after(0, self._log,
                       f"  ⏳ Cooldown {cooldown}s...", "info")
            for sec in range(cooldown, 0, -1):
                if not self._running:
                    break
                self.after(0, self.lbl_status.config,
                           {"text": f"● Cooldown {sec}s", "fg": YELLOW})
                self.after(0, self.prog_var.set, (sec / cooldown) * 100)
                time.sleep(1)

            if not self._running:
                break
            self.after(0, self.lbl_status.config,
                       {"text": "● Running", "fg": ACCENT2})
            self.after(0, self._log, "  ▶ Resuming...", "header")

        self.after(0, self._finish)

    def _finish(self):
        self._running = False
        self.btn_start.config(state="normal",  bg=ACCENT, fg="white")
        self.btn_stop.config(state="disabled", bg=BG3,    fg=TEXT_DIM)
        self.lbl_status.config(text="● Ready", fg=GREEN)
        self.prog_var.set(100)
        self._log("─" * 54, "dim")
        self._log(f"  ✅ {self.free_count} free   ❌ {self.taken_count} taken   ⚠️  {self.error_count} errors", "info")
        self._log("─" * 54, "dim")


if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure Python is installed with tkinter support.")
        print("Download: https://www.python.org/downloads/")
        input("\nPress Enter to exit...")
