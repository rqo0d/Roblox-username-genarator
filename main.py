import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random, string, urllib.request, json, time, os
import threading, webbrowser, platform, subprocess, csv
from datetime import datetime, timedelta
from collections import deque

CONFIG_FILE = "config.json"


WORD_LIST = [
    "fire","wolf","nova","storm","blade","frost","neon","viper","echo","raven",
    "flux","void","apex","zeal","iron","gale","byte","core","dusk","dawn",
    "peak","kite","bolt","haze","grit","silk","pyre","lynx","onyx","jade",
    "vale","cove","riot","husk","tusk","lark","fern","glow","hilt","knot"
]

THEMES = {
    "dark": {
        "BG":"#0d0d0d","BG2":"#141414","BG3":"#1e1e1e","CARD":"#181818",
        "BORDER":"#2a2a2a","TEXT":"#f0f0f0","TEXT_DIM":"#555555","TEXT_MID":"#888888"
    },
    "light": {
        "BG":"#f0f0f0","BG2":"#e2e2e2","BG3":"#ffffff","CARD":"#ffffff",
        "BORDER":"#cccccc","TEXT":"#1a1a1a","TEXT_DIM":"#aaaaaa","TEXT_MID":"#666666"
    }
}
ACCENT="#e8151b"; ACCENT2="#ff4444"; GREEN="#22c55e"; RED_C="#ef4444"; YELLOW="#f59e0b"
GOLD="#f59e0b"; PURPLE="#a855f7"
FM=("Segoe UI",10); FS=("Segoe UI",9); FMONO=("Consolas",10)

_T = THEMES["dark"]
BG=_T["BG"]; BG2=_T["BG2"]; BG3=_T["BG3"]; CARD=_T["CARD"]
BORDER=_T["BORDER"]; TEXT=_T["TEXT"]; TEXT_DIM=_T["TEXT_DIM"]; TEXT_MID=_T["TEXT_MID"]

DEFAULT_CONFIG = {
    "total_length":5,"count":10,"use_numbers":True,"use_letters":True,
    "delay_seconds":2.0,"cooldown_seconds":60,"save_file":"free_usernames.txt",
    "discord_webhook":"","discord_id":"","theme":"dark",
    "sound_notify":True,"sys_notify":True,"open_roblox":False,
    "gen_mode":"standard","pattern":"LLDD","threads":1,
    "auto_pause_errors":5,"warn_delay":0.5
}

def load_config():
    if not os.path.exists(CONFIG_FILE): return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE,"r",encoding="utf-8") as f: cfg=json.load(f)
        r=DEFAULT_CONFIG.copy(); r.update(cfg); return r
    except: return DEFAULT_CONFIG.copy()

def save_config_file(cfg):
    with open(CONFIG_FILE,"w",encoding="utf-8") as f: json.dump(cfg,f,indent=2)

def load_records():
    return {"best_free":0,"best_session":"—"}

def save_records(rec):
    pass  # stored in memory only

# ── Generation modes ──────────────────────────
VOWELS="aeiouAEIOU"; CONSONANTS="".join(c for c in string.ascii_letters if c not in VOWELS)

def gen_standard(prefix,rand_len,length,use_letters,use_numbers):
    charset=""
    if use_letters: charset+=string.ascii_letters
    if use_numbers: charset+=string.digits
    if not charset: charset=string.ascii_letters
    if rand_len:
        p="".join(random.choices(string.ascii_letters,k=rand_len))
        s=max(0,length-rand_len)
    else:
        p=prefix; s=max(0,length-len(prefix))
    return p+"".join(random.choices(charset,k=s))

def gen_pattern(pattern, prefix=""):
    result=prefix
    for ch in pattern:
        if ch=="L": result+=random.choice(string.ascii_letters)
        elif ch=="U": result+=random.choice(string.ascii_uppercase)
        elif ch=="l": result+=random.choice(string.ascii_lowercase)
        elif ch=="D": result+=random.choice(string.digits)
        elif ch=="_": result+="_"
        else: result+=ch
    return result

def gen_readable(length, prefix=""):
    result=prefix
    toggle=random.choice([True,False])
    while len(result)<length:
        result+=random.choice(VOWELS if toggle else CONSONANTS)
        toggle=not toggle
    return result[:length]

def gen_underscore(prefix,length):
    half=max(1,(length-1)//2)
    a="".join(random.choices(string.ascii_lowercase,k=half))
    b="".join(random.choices(string.ascii_lowercase+string.digits,k=length-half-1))
    return (prefix+a if prefix else a)+"_"+b

def gen_word(prefix,length):
    candidates=[w for w in WORD_LIST if len(prefix)+len(w)<=length]
    if not candidates: candidates=WORD_LIST
    word=random.choice(candidates)
    suffix_len=length-len(prefix)-len(word)
    suffix="".join(random.choices(string.digits,k=max(0,suffix_len)))
    return prefix+word+suffix

# ── API ───────────────────────────────────────
def check_username(username, proxy=None):
    url=(f"https://auth.roblox.com/v1/usernames/validate"
         f"?request.username={username}&request.birthday=2000-01-01")
    try:
        if proxy:
            pu=proxy if proxy.startswith("http") else f"http://{proxy}"
            opener=urllib.request.build_opener(
                urllib.request.ProxyHandler({"http":pu,"https":pu}))
        else: opener=urllib.request.build_opener()
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
        with opener.open(req,timeout=6) as resp:
            return json.loads(resp.read().decode()).get("code")==0
    except: return None

def append_free(username,save_file):
    with open(save_file,"a",encoding="utf-8") as f: f.write(username+"\n")

def send_to_discord(webhook_url,username,discord_id=None):
    if not webhook_url or not webhook_url.startswith("https://discord"):
        return True,"skipped"
    try:
        mention=f"<@{discord_id}> " if discord_id else ""
        body={"content":mention if mention else None,
              "embeds":[{"title":"🎮 Free Roblox Username Found!",
                         "description":f"```\n{username}\n```",
                         "color":0x22c55e,
                         "footer":{"text":"Roblox Username Generator"}}]}
        if not body["content"]: del body["content"]
        payload=json.dumps(body).encode("utf-8")
        req=urllib.request.Request(
            webhook_url.strip(),data=payload,
            headers={"Content-Type":"application/json","User-Agent":"Mozilla/5.0"},
            method="POST")
        with urllib.request.urlopen(req,timeout=8) as resp:
            return resp.status in(200,204),f"HTTP {resp.status}"
    except urllib.error.HTTPError as e: return False,f"HTTP {e.code}"
    except Exception as e: return False,str(e)

def play_sound():
    try:
        if platform.system()=="Windows":
            import winsound; winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        else:
            subprocess.Popen(["afplay","/System/Library/Sounds/Glass.aiff"],
                             stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except: pass

def system_notify(title,message):
    try:
        if platform.system()=="Darwin":
            subprocess.Popen(["osascript","-e",
                f'display notification "{message}" with title "{title}"'],
                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        elif platform.system()=="Linux":
            subprocess.Popen(["notify-send",title,message],
                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except: pass

# ═══════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Roblox Username Generator")
        self.geometry("1000x720"); self.minsize(900,620)
        self.configure(bg=BG)
        self._running=False; self.theme_name="dark"
        self._webhook_url=""
        self._discord_id=""
        self.var_out_discord=tk.BooleanVar(value=False)
        self.free_count=0; self.taken_count=0
        self.error_count=0; self.total_done=0
        self._start_time=None; self._recent=deque(maxlen=30)
        self._consecutive_errors=0
        self._found_list=[]   # for Found tab
        self._build()
        self._load_cfg()
        self._tick()

    # ══════════════════════════════════════════
    def _build(self):
        # Header
        hdr=tk.Frame(self,bg=BG); hdr.pack(fill="x",padx=24,pady=(20,0))
        cv=tk.Canvas(hdr,width=14,height=14,bg=BG,highlightthickness=0)
        cv.create_oval(2,2,12,12,fill=ACCENT,outline=""); cv.pack(side="left",padx=(0,10))
        tk.Label(hdr,text="Roblox Username Generator",
                 font=("Segoe UI",18,"bold"),bg=BG,fg=TEXT).pack(side="left")
        self.lbl_status=tk.Label(hdr,text="● Ready",font=FS,bg=BG,fg=GREEN)
        self.lbl_status.pack(side="right",padx=(10,0))
        self.btn_theme=tk.Button(hdr,text="☀ Light",font=FS,bg=BG3,fg=TEXT_MID,
            activebackground=BORDER,activeforeground=TEXT,relief="flat",bd=0,
            cursor="hand2",padx=10,pady=4,command=self._toggle_theme)
        self.btn_theme.pack(side="right",padx=4)
        tk.Frame(self,bg=BORDER,height=1).pack(fill="x",padx=24,pady=12)

        # Notebook (tabs)
        style=ttk.Style(); style.theme_use("clam")
        style.configure("Dark.TNotebook",background=BG,borderwidth=0)
        style.configure("Dark.TNotebook.Tab",background=BG3,foreground=TEXT_MID,
            padding=[12,6],font=("Segoe UI",9))
        style.map("Dark.TNotebook.Tab",
            background=[("selected",CARD)],foreground=[("selected",TEXT)])
        self.nb=ttk.Notebook(self,style="Dark.TNotebook")
        self.nb.pack(fill="both",expand=True,padx=24,pady=(0,0))

        # Tab 1 — Generator
        self.tab_gen=tk.Frame(self.nb,bg=BG); self.nb.add(self.tab_gen,text="⚙  Generator")
        # Tab 2 — Found
        self.tab_found=tk.Frame(self.nb,bg=BG); self.nb.add(self.tab_found,text="✅  Found")


        self._build_gen_tab()
        self._build_found_tab()


        # Bottom bar — pinned inside main window
        bot=tk.Frame(self,bg=BG2,highlightbackground=BORDER,highlightthickness=1)
        bot.pack(fill="x",side="bottom",before=self.nb)
        btns=tk.Frame(bot,bg=BG2); btns.pack(padx=24,pady=10)
        self.btn_start=tk.Button(btns,text="▶  START",font=("Segoe UI",11,"bold"),
            bg=ACCENT,fg="white",activebackground=ACCENT2,activeforeground="white",
            relief="flat",bd=0,cursor="hand2",padx=28,pady=8,command=self._start)
        self.btn_start.pack(side="left",padx=(0,8))
        self.btn_stop=tk.Button(btns,text="■  STOP",font=("Segoe UI",11,"bold"),
            bg=BG3,fg=TEXT_DIM,activebackground=BORDER,activeforeground=TEXT,
            relief="flat",bd=0,cursor="hand2",padx=28,pady=8,
            state="disabled",command=self._stop)
        self.btn_stop.pack(side="left",padx=(0,20))
        tk.Button(btns,text="💾  Save config",font=FS,bg=BG3,fg=TEXT_MID,
            activebackground=BORDER,activeforeground=TEXT,relief="flat",bd=0,
            cursor="hand2",padx=12,pady=8,command=self._save_cfg).pack(side="left")
        self.lbl_footer=tk.Label(btns,text="",font=FS,bg=BG2,fg=GREEN)
        self.lbl_footer.pack(side="right",padx=10)

    # ── Tab 1: Generator ──────────────────────
    def _build_gen_tab(self):
        cols=tk.Frame(self.tab_gen,bg=BG); cols.pack(fill="both",expand=True)
        # Scrollable left
        lo=tk.Frame(cols,bg=BG,width=290); lo.pack(side="left",fill="y",padx=(0,10))
        lo.pack_propagate(False)
        lc=tk.Canvas(lo,bg=BG,highlightthickness=0); lc.pack(side="left",fill="both",expand=True)
        ls=tk.Scrollbar(lo,orient="vertical",command=lc.yview,bg=BG3,troughcolor=BG,width=6)
        ls.pack(side="right",fill="y"); lc.configure(yscrollcommand=ls.set)
        self.left=tk.Frame(lc,bg=BG)
        wid=lc.create_window((0,0),window=self.left,anchor="nw")
        lc.bind("<Configure>",lambda e,c=lc,w=wid: c.itemconfig(w,width=e.width))
        self.left.bind("<Configure>",lambda e,c=lc: c.configure(scrollregion=c.bbox("all")))
        def _mw(e, c=lc, canvas=lc, inner=self.left):
            # Only scroll if mouse is physically over the left panel canvas
            try:
                cx = canvas.winfo_rootx()
                cy = canvas.winfo_rooty()
                cw = canvas.winfo_width()
                ch = canvas.winfo_height()
                mx = e.x_root
                my = e.y_root
                if cx <= mx <= cx + cw and cy <= my <= cy + ch:
                    canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
            except Exception:
                pass
        self.bind_all("<MouseWheel>", _mw)
        # Right panel
        self.right=tk.Frame(cols,bg=BG); self.right.pack(side="left",fill="both",expand=True)
        self._build_left(); self._build_right()

    def _build_left(self):
        # GENERATION
        self._sec(self.left,"GENERATION")
        r=tk.Frame(self.left,bg=CARD); r.pack(fill="x")
        self._lbl(r,"Username length"); self.var_len=tk.IntVar(value=5); self._spin(r,self.var_len,3,20)
        self._lbl(r,"Count per batch"); self.var_count=tk.IntVar(value=10); self._spin(r,self.var_count,1,500)
        self._lbl(r,"Delay (seconds)"); self.var_delay=tk.DoubleVar(value=2.0)
        tk.Spinbox(r,from_=0.1,to=10.0,increment=0.1,textvariable=self.var_delay,format="%.1f",
            width=10,font=FMONO,bg=BG3,fg=TEXT,insertbackground=TEXT,buttonbackground=BG3,
            relief="flat",highlightthickness=1,highlightbackground=BORDER,
            highlightcolor=ACCENT).pack(anchor="w",padx=14,pady=(0,4))
        self._lbl(r,"Cooldown after batch (sec)"); self.var_cooldown=tk.IntVar(value=60)
        self._spin(r,self.var_cooldown,5,600)
        self._lbl(r,"Threads (parallel checks)"); self.var_threads=tk.IntVar(value=1)
        tk.Spinbox(r,from_=1,to=5,textvariable=self.var_threads,width=10,font=FMONO,
            bg=BG3,fg=TEXT,insertbackground=TEXT,buttonbackground=BG3,relief="flat",
            highlightthickness=1,highlightbackground=BORDER,highlightcolor=ACCENT
            ).pack(anchor="w",padx=14,pady=(0,4))
        self._lbl(r,"Auto-pause after N errors"); self.var_autopause=tk.IntVar(value=5)
        self._spin(r,self.var_autopause,1,20)
        cb=tk.Frame(self.left,bg=CARD); cb.pack(fill="x")
        self.var_letters=tk.BooleanVar(value=True)
        self.var_numbers=tk.BooleanVar(value=True)
        self._chk(cb,"Use letters  (a-z A-Z)",self.var_letters)
        self._chk(cb,"Use numbers  (0-9)",self.var_numbers)
        tk.Frame(self.left,bg=CARD,height=8).pack(fill="x")
        tk.Frame(self.left,bg=BORDER,height=1).pack(fill="x")

        # GENERATION MODE
        self._sec(self.left,"GENERATION MODE")
        gm=tk.Frame(self.left,bg=CARD); gm.pack(fill="x")
        self.var_gen_mode=tk.StringVar(value="standard")
        modes=[("Standard (prefix + random)","standard"),
               ("Pattern  e.g. LLDD","pattern"),
               ("Readable  e.g. KaRoB","readable"),
               ("Underscore  e.g. cool_x1","underscore"),
               ("Word-based  e.g. fire42","word")]
        for txt,val in modes:
            tk.Radiobutton(gm,text=txt,variable=self.var_gen_mode,value=val,
                bg=CARD,fg=TEXT,selectcolor=BG3,activebackground=CARD,
                activeforeground=TEXT,font=FM,command=self._toggle_mode
                ).pack(anchor="w",padx=14,pady=2)
        # Standard prefix
        self.frm_std=tk.Frame(gm,bg=CARD); self.frm_std.pack(fill="x",padx=14)
        tk.Label(self.frm_std,text="Prefix (optional)",bg=CARD,fg=TEXT_MID,font=FS).pack(anchor="w")
        self.entry_prefix=tk.Entry(self.frm_std,font=FMONO,bg=BG3,fg=TEXT,
            insertbackground=TEXT,relief="flat",highlightthickness=1,
            highlightbackground=BORDER,highlightcolor=ACCENT)
        self.entry_prefix.pack(fill="x",pady=(2,6))
        # Pattern input
        self.frm_pat=tk.Frame(gm,bg=CARD); self.frm_pat.pack(fill="x",padx=14)
        tk.Label(self.frm_pat,text="Pattern (L=letter U=upper l=lower D=digit _=underscore)",
            bg=CARD,fg=TEXT_MID,font=("Segoe UI",8),wraplength=220,justify="left"
            ).pack(anchor="w")
        self.entry_pattern=tk.Entry(self.frm_pat,font=FMONO,bg=BG3,fg=TEXT,
            insertbackground=TEXT,relief="flat",highlightthickness=1,
            highlightbackground=BORDER,highlightcolor=ACCENT)
        self.entry_pattern.insert(0,"LLDD")
        self.entry_pattern.pack(fill="x",pady=(2,8))
        tk.Frame(self.left,bg=CARD,height=4).pack(fill="x")
        tk.Frame(self.left,bg=BORDER,height=1).pack(fill="x")
        self._toggle_mode()

        # PREFIX (standard only)
        self._sec(self.left,"PREFIX (STANDARD MODE)")
        pf=tk.Frame(self.left,bg=CARD); pf.pack(fill="x")
        self.var_pmode=tk.StringVar(value="custom")
        tk.Radiobutton(pf,text="Custom prefix",variable=self.var_pmode,value="custom",
            bg=CARD,fg=TEXT,selectcolor=BG3,activebackground=CARD,activeforeground=TEXT,
            font=FM,command=self._toggle_prefix).pack(anchor="w",padx=14,pady=(6,2))
        tk.Radiobutton(pf,text="Random prefix",variable=self.var_pmode,value="random",
            bg=CARD,fg=TEXT,selectcolor=BG3,activebackground=CARD,activeforeground=TEXT,
            font=FM,command=self._toggle_prefix).pack(anchor="w",padx=14,pady=(0,8))
        tk.Label(pf,text="Random prefix length",bg=CARD,fg=TEXT_MID,font=FS).pack(anchor="w",padx=14)
        self.var_rlen=tk.IntVar(value=2)
        self.spin_rlen=tk.Spinbox(pf,from_=1,to=10,textvariable=self.var_rlen,width=10,
            font=FMONO,bg=BG3,fg=TEXT,insertbackground=TEXT,buttonbackground=BG3,
            relief="flat",highlightthickness=1,highlightbackground=BORDER,
            highlightcolor=ACCENT,state="disabled")
        self.spin_rlen.pack(anchor="w",padx=14,pady=(2,10))
        tk.Frame(self.left,bg=BORDER,height=1).pack(fill="x")

        # PROXY
        self._sec(self.left,"PROXY")
        px=tk.Frame(self.left,bg=CARD); px.pack(fill="x")
        self.var_proxy_on=tk.BooleanVar(value=False)
        self._chk(px,"Enable proxy",self.var_proxy_on,cmd=self._toggle_proxy)
        self._chk_proxy_file=tk.BooleanVar(value=False)
        self._chk(px,"Use proxies.txt (auto-rotate)",self._chk_proxy_file)
        tk.Label(px,text="Single proxy  (ip:port)",bg=CARD,fg=TEXT_MID,font=FS
            ).pack(anchor="w",padx=14,pady=(4,0))
        self.entry_proxy=tk.Entry(px,font=FMONO,bg=BG3,fg=TEXT,insertbackground=TEXT,
            relief="flat",highlightthickness=1,highlightbackground=BORDER,
            highlightcolor=ACCENT,state="disabled")
        self.entry_proxy.pack(fill="x",padx=14,pady=(2,10))
        tk.Frame(self.left,bg=BORDER,height=1).pack(fill="x")

        # OUTPUT
        self._sec(self.left,"OUTPUT")
        op=tk.Frame(self.left,bg=CARD); op.pack(fill="x")
        tk.Label(op,text="Where to send free usernames:",bg=CARD,fg=TEXT_MID,font=FS
            ).pack(anchor="w",padx=14,pady=(10,6))
        self.var_out_file=tk.BooleanVar(value=True)
        self._chk(op,"📄  Save to file",self.var_out_file,cmd=self._toggle_out_file)
        self.entry_file=tk.Entry(op,font=FMONO,bg=BG3,fg=TEXT,insertbackground=TEXT,
            relief="flat",highlightthickness=1,highlightbackground=BORDER,highlightcolor=ACCENT)
        self.entry_file.insert(0,"free_usernames.txt")
        self.entry_file.pack(fill="x",padx=28,pady=(3,8))
        tk.Frame(op,bg=CARD,height=8).pack(fill="x")

        # NOTIFICATIONS
        self._sec(self.left,"NOTIFICATIONS")
        nf=tk.Frame(self.left,bg=CARD); nf.pack(fill="x")
        self.var_sound=tk.BooleanVar(value=True)
        def _sound_toggle():
            if self._discord_id:
                self.var_sound.set(False)
                messagebox.showerror(
                    "Sound disabled",
                    "Sound notifications are disabled when Discord ID is set.\n\n"
                    "To enable sound — open config.json and clear the discord_id field:\n"
                    '   "discord_id": ""'
                )
        self._chk(nf,"🔔  Sound when free username found",self.var_sound,cmd=_sound_toggle)
        self.var_sysnotify=tk.BooleanVar(value=False)
        self.var_open_roblox=tk.BooleanVar(value=False)
        self.var_roblox_maxlen=tk.IntVar(value=20)
        tk.Frame(nf,bg=CARD,height=8).pack(fill="x")

    def _build_right(self):
        # Stats row
        stats=tk.Frame(self.right,bg=CARD,highlightbackground=BORDER,highlightthickness=1)
        stats.pack(fill="x",pady=(0,6))
        self.lbl_free =self._stat(stats,"FREE",   "0",    GREEN,  0)
        self.lbl_taken=self._stat(stats,"TAKEN",  "0",    RED_C,  1)
        self.lbl_err  =self._stat(stats,"ERRORS", "0",    YELLOW, 2)
        self.lbl_total=self._stat(stats,"CHECKED","0",    TEXT,   3)
        self.lbl_timer=self._stat(stats,"TIME",   "00:00",TEXT,   4)

        self.lbl_record=tk.Label(self.right,text="")  # removed

        # Progress bar with %
        pf=tk.Frame(self.right,bg=BG); pf.pack(fill="x",pady=(0,6))
        self.prog_var=tk.DoubleVar(value=0)
        sty=ttk.Style(); sty.theme_use("clam")
        sty.configure("R.Horizontal.TProgressbar",troughcolor=BG3,background=ACCENT,
            bordercolor=BORDER,lightcolor=ACCENT2,darkcolor=ACCENT)
        self.prog_bar=ttk.Progressbar(pf,variable=self.prog_var,
            style="R.Horizontal.TProgressbar",mode="determinate",maximum=100)
        self.prog_bar.pack(side="left",fill="x",expand=True,ipady=4)
        self.lbl_pct=tk.Label(pf,text="  0%",font=("Segoe UI",8,"bold"),
            bg=BG,fg=TEXT_MID,width=6); self.lbl_pct.pack(side="left")

        # Log
        lw=tk.Frame(self.right,bg=CARD,highlightbackground=BORDER,highlightthickness=1)
        lw.pack(fill="both",expand=True)
        tb=tk.Frame(lw,bg=CARD); tb.pack(fill="x",padx=14,pady=(10,4))
        tk.Label(tb,text="LOG",font=("Segoe UI",8,"bold"),bg=CARD,fg=TEXT_DIM).pack(side="left")
        tk.Button(tb,text="Clear",font=FS,bg=BG3,fg=TEXT_DIM,activebackground=BORDER,
            activeforeground=TEXT,relief="flat",bd=0,cursor="hand2",padx=8,pady=2,
            command=self._clear_log).pack(side="right")
        tk.Frame(lw,bg=BORDER,height=1).pack(fill="x",padx=14)
        self.log=tk.Text(lw,bg=BG2,fg=TEXT,font=FMONO,relief="flat",bd=0,wrap="none",
            insertbackground=TEXT,selectbackground=ACCENT,state="disabled",padx=10,pady=8)
        self.log.pack(fill="both",expand=True,padx=8,pady=8)
        self.log.tag_config("free",   foreground=GREEN)
        self.log.tag_config("short",  foreground=GOLD)
        self.log.tag_config("rare",   foreground=PURPLE)
        self.log.tag_config("taken",  foreground=RED_C)
        self.log.tag_config("error",  foreground=YELLOW)
        self.log.tag_config("info",   foreground=TEXT_MID)
        self.log.tag_config("header", foreground=ACCENT)
        self.log.tag_config("dim",    foreground=TEXT_DIM)
        self.log.tag_config("warn",   foreground=YELLOW,font=("Segoe UI",9,"bold"))

    # ── Tab 2: Found ──────────────────────────
    def _build_found_tab(self):
        top=tk.Frame(self.tab_found,bg=BG); top.pack(fill="x",padx=16,pady=10)
        tk.Label(top,text="Free usernames found this session",
            font=("Segoe UI",11,"bold"),bg=BG,fg=TEXT).pack(side="left")
        tk.Button(top,text="📥  Export CSV",font=FS,bg=BG3,fg=TEXT_MID,
            activebackground=BORDER,activeforeground=TEXT,relief="flat",bd=0,
            cursor="hand2",padx=10,pady=4,command=self._export_csv).pack(side="right")
        tk.Button(top,text="🗑  Clear all",font=FS,bg=BG3,fg=TEXT_DIM,
            activebackground=BORDER,activeforeground=TEXT,relief="flat",bd=0,
            cursor="hand2",padx=10,pady=4,command=self._clear_found).pack(side="right",padx=6)
        tk.Frame(self.tab_found,bg=BORDER,height=1).pack(fill="x",padx=16)
        self.found_frame=tk.Frame(self.tab_found,bg=BG2)
        self.found_frame.pack(fill="both",expand=True,padx=16,pady=8)
        self.found_canvas=tk.Canvas(self.found_frame,bg=BG2,highlightthickness=0)
        self.found_canvas.pack(side="left",fill="both",expand=True)
        fsb=tk.Scrollbar(self.found_frame,orient="vertical",
            command=self.found_canvas.yview,bg=BG3,troughcolor=BG2,width=6)
        fsb.pack(side="right",fill="y")
        self.found_canvas.configure(yscrollcommand=fsb.set)
        self.found_inner=tk.Frame(self.found_canvas,bg=BG2)
        fwid=self.found_canvas.create_window((0,0),window=self.found_inner,anchor="nw")
        self.found_canvas.bind("<Configure>",
            lambda e,c=self.found_canvas,w=fwid: c.itemconfig(w,width=e.width))
        self.found_inner.bind("<Configure>",
            lambda e,c=self.found_canvas: c.configure(scrollregion=c.bbox("all")))
        self.lbl_no_found=tk.Label(self.found_inner,
            text="No free usernames found yet.\nStart the generator to begin.",
            font=("Segoe UI",11),bg=BG2,fg=TEXT_DIM)
        self.lbl_no_found.pack(pady=40)



    # ── Widget helpers ────────────────────────
    def _sec(self,parent,title):
        f=tk.Frame(parent,bg=CARD); f.pack(fill="x")
        tk.Label(f,text=title,font=("Segoe UI",8,"bold"),bg=CARD,fg=TEXT_DIM
            ).pack(anchor="w",padx=14,pady=(12,4))
        tk.Frame(f,bg=BORDER,height=1).pack(fill="x",padx=14)

    def _lbl(self,parent,text):
        tk.Label(parent,text=text,bg=CARD,fg=TEXT_MID,font=FS
            ).pack(anchor="w",padx=14,pady=(8,1))

    def _spin(self,parent,var,mn,mx):
        tk.Spinbox(parent,from_=mn,to=mx,textvariable=var,width=10,font=FMONO,
            bg=BG3,fg=TEXT,insertbackground=TEXT,buttonbackground=BG3,relief="flat",
            highlightthickness=1,highlightbackground=BORDER,highlightcolor=ACCENT
            ).pack(anchor="w",padx=14,pady=(0,4))

    def _chk(self,parent,text,var,cmd=None,pady=2):
        tk.Checkbutton(parent,text=text,variable=var,bg=CARD,fg=TEXT,selectcolor=BG3,
            activebackground=CARD,activeforeground=TEXT,font=FM,command=cmd
            ).pack(anchor="w",padx=14,pady=pady)

    def _stat(self,parent,label,val,color,col):
        parent.columnconfigure(col,weight=1)
        f=tk.Frame(parent,bg=CARD); f.grid(row=0,column=col,padx=2,pady=10,sticky="nsew")
        lbl=tk.Label(f,text=val,font=("Segoe UI",18,"bold"),bg=CARD,fg=color); lbl.pack()
        tk.Label(f,text=label,font=("Segoe UI",7,"bold"),bg=CARD,fg=TEXT_DIM).pack()
        return lbl

    # ── Toggles ───────────────────────────────
    def _toggle_mode(self):
        mode=self.var_gen_mode.get()
        self.frm_std.pack_forget(); self.frm_pat.pack_forget()
        if mode=="standard": self.frm_std.pack(fill="x",padx=14,pady=(4,8))
        elif mode=="pattern": self.frm_pat.pack(fill="x",padx=14,pady=(4,8))

    def _toggle_prefix(self):
        self.spin_rlen.configure(state="normal" if self.var_pmode.get()=="random" else "disabled")

    def _toggle_proxy(self):
        self.entry_proxy.configure(state="normal" if self.var_proxy_on.get() else "disabled")

    def _toggle_out_file(self):
        self.entry_file.configure(state="normal" if self.var_out_file.get() else "disabled")

    def _toggle_theme(self):
        global BG,BG2,BG3,CARD,BORDER,TEXT,TEXT_DIM,TEXT_MID
        self.theme_name="light" if self.theme_name=="dark" else "dark"
        _T=THEMES[self.theme_name]
        BG=_T["BG"];BG2=_T["BG2"];BG3=_T["BG3"];CARD=_T["CARD"]
        BORDER=_T["BORDER"];TEXT=_T["TEXT"];TEXT_DIM=_T["TEXT_DIM"];TEXT_MID=_T["TEXT_MID"]
        self._apply_theme(self)
        self.btn_theme.config(text="🌙 Dark" if self.theme_name=="light" else "☀ Light")
        cfg=load_config(); cfg["theme"]=self.theme_name; save_config_file(cfg)

    def _apply_theme(self, widget):
        cls = widget.winfo_class()
        # Determine if widget lives in a "card" area or a "bg" area
        is_bg_widget = widget in (
            self, self.right, self.tab_gen, self.tab_found,
            self.nb, self.left
        )
        try:
            if cls in ("Frame", "Tk"):
                widget.configure(bg=BG if is_bg_widget else CARD)
            elif cls == "Label":
                try:
                    parent_bg = widget.master.cget("bg")
                except Exception:
                    parent_bg = CARD
                widget.configure(bg=parent_bg)
                fixed_colors = (ACCENT, GREEN, RED_C, YELLOW, ACCENT2, GOLD, PURPLE)
                if widget.cget("fg") not in fixed_colors:
                    widget.configure(fg=TEXT)
            elif cls == "Entry":
                widget.configure(bg=BG3, fg=TEXT, insertbackground=TEXT,
                                 highlightbackground=BORDER,
                                 disabledbackground=BG3, disabledforeground=TEXT_DIM)
            elif cls in ("Checkbutton", "Radiobutton"):
                try: par_bg = widget.master.cget("bg")
                except: par_bg = CARD
                widget.configure(bg=par_bg, fg=TEXT, selectcolor=BG3,
                                 activebackground=par_bg, activeforeground=TEXT)
            elif cls == "Spinbox":
                widget.configure(bg=BG3, fg=TEXT, buttonbackground=BG3,
                                 insertbackground=TEXT, highlightbackground=BORDER)
            elif cls == "Text":
                widget.configure(bg=BG2, fg=TEXT)
            elif cls == "Canvas":
                widget.configure(bg=BG2 if widget == self.found_canvas else CARD)
            elif cls == "Button":
                if widget == self.btn_start:
                    pass  # keep ACCENT
                elif widget == self.btn_stop and self._running:
                    pass  # keep ACCENT
                else:
                    widget.configure(bg=BG3, fg=TEXT_MID,
                                     activebackground=BORDER, activeforeground=TEXT)
        except Exception:
            pass
        for child in widget.winfo_children():
            self._apply_theme(child)

    def _autosave_id(self):
        pass  # discord id saved via config.json directly

    # ── Config ────────────────────────────────
    def _load_cfg(self):
        cfg=load_config()
        self.var_len.set(cfg.get("total_length",5))
        self.var_count.set(cfg.get("count",10))
        self.var_delay.set(cfg.get("delay_seconds",2.0))
        self.var_cooldown.set(cfg.get("cooldown_seconds",60))
        self.var_letters.set(cfg.get("use_letters",True))
        self.var_numbers.set(cfg.get("use_numbers",True))
        self.var_threads.set(cfg.get("threads",1))
        self.var_autopause.set(cfg.get("auto_pause_errors",5))
        self.var_gen_mode.set(cfg.get("gen_mode","standard"))
        pat=cfg.get("pattern","LLDD")
        self.entry_pattern.delete(0,"end"); self.entry_pattern.insert(0,pat)
        sf=cfg.get("save_file","free_usernames.txt")
        self.entry_file.delete(0,"end"); self.entry_file.insert(0,sf)
        self._webhook_url = cfg.get("discord_webhook","")
        self._discord_id  = cfg.get("discord_id","")
        if self._webhook_url:
            self.var_out_discord.set(True)
        self.var_sound.set(cfg.get("sound_notify",True))
        if self._discord_id:
            self.var_sound.set(False)
        self.var_sysnotify.set(cfg.get("sys_notify",True))
        self.var_open_roblox.set(cfg.get("open_roblox",False))
        self._toggle_mode()
        saved_theme=cfg.get("theme","dark")
        if saved_theme!=self.theme_name: self._toggle_theme()

    def _save_cfg(self):
        wh=self._webhook_url
        save_config_file({
            "total_length":self.var_len.get(),"count":self.var_count.get(),
            "delay_seconds":round(self.var_delay.get(),1),
            "cooldown_seconds":self.var_cooldown.get(),
            "use_letters":self.var_letters.get(),"use_numbers":self.var_numbers.get(),
            "save_file":self.entry_file.get(),"discord_webhook":wh,
            "discord_id":self._discord_id,
            "sound_notify":self.var_sound.get(),"sys_notify":self.var_sysnotify.get(),
            "open_roblox":self.var_open_roblox.get(),"theme":self.theme_name,
            "gen_mode":self.var_gen_mode.get(),"pattern":self.entry_pattern.get(),
            "threads":self.var_threads.get(),"auto_pause_errors":self.var_autopause.get()
        })
        self.lbl_footer.config(text="✓ Config saved!",fg=GREEN)
        self.after(2500,lambda: self.lbl_footer.config(text=""))

    # ── Log ───────────────────────────────────
    def _log(self,text,tag="info"):
        self.log.configure(state="normal")
        self.log.insert("end",text+"\n",tag)
        self.log.see("end"); self.log.configure(state="disabled")

    def _clear_log(self):
        self.log.configure(state="normal"); self.log.delete("1.0","end")
        self.log.configure(state="disabled")

    def _update_stats(self):
        self.lbl_free.config( text=str(self.free_count))
        self.lbl_taken.config(text=str(self.taken_count))
        self.lbl_err.config(  text=str(self.error_count))
        self.lbl_total.config(text=str(self.total_done))
        # speed






    def _tick(self):
        if self._running and self._start_time:
            elapsed=int(time.time()-self._start_time)
            m,s=divmod(elapsed,60)
            t=f"{m:02d}:{s:02d}"
            self.lbl_timer.config(text=t)

            # animate progress bar color during cooldown
        self.after(1000,self._tick)

    # ── Found tab helpers ─────────────────────
    def _add_found_row(self,name,timestamp):
        if self.lbl_no_found.winfo_exists():
            try: self.lbl_no_found.pack_forget()
            except: pass
        row=tk.Frame(self.found_inner,bg=BG3,highlightbackground=BORDER,highlightthickness=1)
        row.pack(fill="x",pady=2,padx=4)
        # colour tag
        tag_color=GREEN
        if len(name)<=4: tag_color=GOLD
        elif len(name)<=5: tag_color=PURPLE
        tk.Label(row,text=name,font=("Consolas",11,"bold"),bg=BG3,fg=tag_color,
            width=22,anchor="w").pack(side="left",padx=12,pady=6)
        tk.Label(row,text=timestamp,font=FS,bg=BG3,fg=TEXT_DIM).pack(side="left",padx=8)
        def _copy(n=name):
            self.clipboard_clear(); self.clipboard_append(n)
            self.lbl_footer.config(text=f"📋 Copied: {n}",fg=GREEN)
            self.after(2000,lambda: self.lbl_footer.config(text=""))
        tk.Button(row,text="📋 Copy",font=FS,bg=CARD,fg=TEXT_MID,
            activebackground=BORDER,activeforeground=TEXT,relief="flat",bd=0,
            cursor="hand2",padx=8,pady=4,command=_copy).pack(side="right",padx=6)
        def _del(r=row,entry=(name,timestamp)):
            r.destroy()
            if entry in self._found_list: self._found_list.remove(entry)
        tk.Button(row,text="🗑",font=FS,bg=CARD,fg=RED_C,
            activebackground=BORDER,activeforeground=TEXT,relief="flat",bd=0,
            cursor="hand2",padx=6,pady=4,command=_del).pack(side="right")

    def _clear_found(self):
        self._found_list.clear()
        for w in self.found_inner.winfo_children(): w.destroy()
        self.lbl_no_found=tk.Label(self.found_inner,
            text="No free usernames found yet.\nStart the generator to begin.",
            font=("Segoe UI",11),bg=BG2,fg=TEXT_DIM)
        self.lbl_no_found.pack(pady=40)

    def _export_csv(self):
        if not self._found_list:
            messagebox.showinfo("Export","No usernames to export yet!"); return
        path=filedialog.asksaveasfilename(defaultextension=".csv",
            filetypes=[("CSV","*.csv")],initialfile="free_usernames.csv")
        if not path: return
        with open(path,"w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(["Username","Found At"])
            for name,ts in self._found_list: w.writerow([name,ts])
        self.lbl_footer.config(text=f"✅ Exported {len(self._found_list)} usernames",fg=GREEN)
        self.after(3000,lambda: self.lbl_footer.config(text=""))

    # ── Start / Stop ──────────────────────────
    def _start(self):
        if self._running: return
        total_length=self.var_len.get()
        count=self.var_count.get()
        delay=round(self.var_delay.get(),1)
        cooldown=self.var_cooldown.get()
        use_letters=self.var_letters.get()
        use_numbers=self.var_numbers.get()
        use_file=self.var_out_file.get()
        save_file=self.entry_file.get().strip() or "free_usernames.txt"
        threads=max(1,self.var_threads.get())
        autopause=self.var_autopause.get()
        gen_mode=self.var_gen_mode.get()
        pattern=self.entry_pattern.get().strip()
        proxy_on=self.var_proxy_on.get()
        use_proxy_file=self._chk_proxy_file.get()
        proxy=None; proxy_list=[]
        if proxy_on:
            if use_proxy_file and os.path.exists("proxies.txt"):
                with open("proxies.txt") as f:
                    proxy_list=[l.strip() for l in f if l.strip()]
                if not proxy_list:
                    messagebox.showerror("Error","proxies.txt is empty!"); return
            else:
                raw=self.entry_proxy.get().strip()
                if raw: proxy=raw
            delay=0.3; count=9_999_999_999; cooldown=max(5,cooldown)
        if self.var_pmode.get()=="custom":
            raw=self.entry_prefix.get().strip(); prefix="" if not raw else raw; rand_len=None
        else:
            prefix=None; rand_len=self.var_rlen.get()
        raw_wh = self._webhook_url
        webhook = raw_wh if (self.var_out_discord.get() and raw_wh
                             and raw_wh.startswith("https://discord")) else None
        raw_id = self._discord_id
        discord_id = raw_id if (raw_id and raw_id.isdigit()) else None
        sound_on=self.var_sound.get(); sysnotify_on=self.var_sysnotify.get()
        open_roblox=self.var_open_roblox.get()
        roblox_maxlen=self.var_roblox_maxlen.get()
        warn_delay=DEFAULT_CONFIG["warn_delay"]
        if delay<warn_delay and not proxy_on:
            if not messagebox.askyesno("⚠️ Warning",
                f"Delay {delay}s is very low — risk of IP ban!\nContinue anyway?"): return
        if not use_letters and not use_numbers:
            messagebox.showerror("Error","Enable at least letters or numbers!"); return
        if not use_file and not webhook:
            messagebox.showerror("Error","Enable at least one output: file or Discord"); return

        self.free_count=self.taken_count=self.error_count=self.total_done=0
        self._consecutive_errors=0
        self._update_stats(); self.prog_var.set(0); self.lbl_pct.config(text="  0%")
        self._running=True; self._start_time=time.time()

        self.btn_start.config(state="disabled",bg=BG3,fg=TEXT_DIM)
        self.btn_stop.config(state="normal",bg=ACCENT,fg="white")
        self.lbl_status.config(text="● Running",fg=ACCENT2)
        self._log("─"*54,"dim")
        self._log(f"  ▶  mode={gen_mode}  len={total_length}  batch={'∞' if proxy_on else count}  delay={delay}s  threads={threads}","header")
        self._log("─"*54,"dim")
        threading.Thread(target=self._loop,daemon=True,
            args=(prefix,rand_len,total_length,count,use_letters,use_numbers,
                  delay,cooldown,save_file,use_file,webhook,discord_id,
                  sound_on,sysnotify_on,open_roblox,roblox_maxlen,proxy,proxy_list,
                  proxy_on,threads,autopause,gen_mode,pattern)).start()

    def _stop(self): self._running=False

    def _generate_name(self,gen_mode,pattern,prefix,rand_len,total_length,use_letters,use_numbers):
        if gen_mode=="pattern":   return gen_pattern(pattern,prefix or "")
        elif gen_mode=="readable": return gen_readable(total_length,prefix or "")
        elif gen_mode=="underscore": return gen_underscore(prefix or "",total_length)
        elif gen_mode=="word":    return gen_word(prefix or "",total_length)
        else: return gen_standard(prefix,rand_len,total_length,use_letters,use_numbers)

    def _loop(self,prefix,rand_len,total_length,count,use_letters,use_numbers,
              delay,cooldown,save_file,use_file,webhook,discord_id,
              sound_on,sysnotify_on,open_roblox,roblox_maxlen,proxy,proxy_list,
              infinite,threads,autopause,gen_mode,pattern):
        proxy_idx=0
        batch_num=0
        while self._running:
            batch_num+=1
            self.after(0,self._log,f"  ── Batch #{batch_num} ──","dim")
            if threads<=1:
                for i in range(1,count+1):
                    if not self._running: break
                    if proxy_list:
                        proxy=proxy_list[proxy_idx%len(proxy_list)]; proxy_idx+=1
                    name=self._generate_name(gen_mode,pattern,prefix,rand_len,
                                             total_length,use_letters,use_numbers)
                    status=check_username(name,proxy)
                    self.total_done+=1
                    if status is True:
                        self._consecutive_errors=0
                        self.free_count+=1
                        # colour tag
                        tag="short" if len(name)<=4 else ("rare" if len(name)<=5 else "free")
                        notes=[]
                        if use_file: append_free(name,save_file); notes.append("📄")
                        if webhook:
                            ok,_=send_to_discord(webhook,name,discord_id)
                            notes.append("📨" if ok else "⚠️Discord")
                        if sound_on: threading.Thread(target=play_sound,daemon=True).start()
                        if sysnotify_on: threading.Thread(target=system_notify,args=("🎮 Free!",f"Found: {name}"),daemon=True).start()
                        if open_roblox and len(name)<=roblox_maxlen: webbrowser.open(f"https://www.roblox.com/")
                        note_str="  "+" ".join(notes) if notes else ""
                        self.after(0,self._log,f"  ✅  {name:<22} Free{note_str}",tag)
                        ts=datetime.now().strftime("%H:%M:%S")
                        entry=(name,ts)
                        self._found_list.append(entry)
                        self.after(0,self._add_found_row,name,ts)
                        # check record
                        rec=load_records()
                        if self.free_count>rec["best_free"]:
                            rec["best_free"]=self.free_count
                            rec["best_session"]=datetime.now().strftime("%d.%m.%Y %H:%M")
                            save_records(rec)
                            self.after(0,self.lbl_record.config,
                                {"text":f'{rec["best_free"]} free  —  {rec["best_session"]}'})
                    elif status is False:
                        self._consecutive_errors=0
                        self.taken_count+=1
                        self.after(0,self._log,f"  ❌  {name:<22} Taken","taken")
                    else:
                        self.error_count+=1
                        self._consecutive_errors+=1
                        self.after(0,self._log,f"  ⚠️   {name:<22} No response","error")
                        if self._consecutive_errors>=autopause:
                            self.after(0,self._log,
                                f"  🛑 Auto-paused: {autopause} consecutive errors. Waiting 30s...","warn")
                            self.after(0,self.lbl_status.config,{"text":"● Paused (errors)","fg":RED_C})
                            for _ in range(30):
                                if not self._running: break
                                time.sleep(1)
                            self._consecutive_errors=0
                            self.after(0,self.lbl_status.config,{"text":"● Running","fg":ACCENT2})
                    self.after(0,self._update_stats)
                    pct=(i%100) if infinite else (i/count*100)
                    self.after(0,self.prog_var.set,pct)
                    self.after(0,self.lbl_pct.config,{"text":f"{int(pct):3d}%"})
                    if i<count and self._running:
                        time.sleep(delay*random.uniform(0.7,1.3))
            else:
                # Multi-threaded batch
                names=[self._generate_name(gen_mode,pattern,prefix,rand_len,
                    total_length,use_letters,use_numbers) for _ in range(min(count,500))]
                results={}; lock=threading.Lock()
                def check_worker(n,px):
                    s=check_username(n,px)
                    with lock: results[n]=s
                batch_proxy=proxy
                thr_list=[threading.Thread(target=check_worker,args=(n,batch_proxy),daemon=True) for n in names]
                for i,t in enumerate(thr_list):
                    if not self._running: break
                    t.start()
                    if(i+1)%threads==0:
                        for tt in thr_list[max(0,i-threads+1):i+1]: tt.join()
                        time.sleep(delay)
                for t in thr_list: t.join()
                for n,s in results.items():
                    self.total_done+=1
                    if s is True:
                        self.free_count+=1; tag="short" if len(n)<=4 else("rare" if len(n)<=5 else"free")
                        if use_file: append_free(n,save_file)
                        if webhook: send_to_discord(webhook,n,discord_id)
                        self.after(0,self._log,f"  ✅  {n:<22} Free",tag)
                        ts=datetime.now().strftime("%H:%M:%S"); self._found_list.append((n,ts))
                        self.after(0,self._add_found_row,n,ts)
                    elif s is False:
                        self.taken_count+=1; self.after(0,self._log,f"  ❌  {n:<22} Taken","taken")
                    else:
                        self.error_count+=1; self.after(0,self._log,f"  ⚠️   {n:<22} No response","error")
                self.after(0,self._update_stats)

            if not self._running: break
            # Cooldown
            self.after(0,self._log,f"  ⏳ Cooldown {cooldown}s...","info")
            for sec in range(cooldown,0,-1):
                if not self._running: break
                self.after(0,self.lbl_status.config,{"text":f"● Cooldown {sec}s","fg":YELLOW})
                self.after(0,self.prog_var.set,(sec/cooldown)*100)
                self.after(0,self.lbl_pct.config,{"text":f"{int((sec/cooldown)*100):3d}%"})
                time.sleep(1)
            if not self._running: break
            self.after(0,self.lbl_status.config,{"text":"● Running","fg":ACCENT2})
            self.after(0,self._log,"  ▶ Resuming...","header")
        self.after(0,self._finish)

    def _finish(self):
        self._running=False
        self.btn_start.config(state="normal",bg=ACCENT,fg="white")
        self.btn_stop.config(state="disabled",bg=BG3,fg=TEXT_DIM)
        self.lbl_status.config(text="● Ready",fg=GREEN)
        self.prog_var.set(100); self.lbl_pct.config(text="100%")
        self._log("─"*54,"dim")
        self._log(f"  ✅ {self.free_count} free   ❌ {self.taken_count} taken   ⚠️  {self.error_count} errors","info")
        self._log("─"*54,"dim")


if __name__=="__main__":
    try:
        app=App(); app.mainloop()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure Python is installed with tkinter support.")
        print("Download: https://www.python.org/downloads/")
        input("\nPress Enter to exit...")
