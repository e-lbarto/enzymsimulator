"""
Enzymaktivität – Abhängigkeit von der Substratkonzentration
Interaktive Simulation  |  tkinter  |  Python 3.9+

Verbesserungen v3:
  • Theme-System: Dunkel (Matrix-Neon) + Hell (Papier & Gezeichnet)
  • Theme-Umschalter unter dem Sim-Speed Slider (links)
  • Graph: X = Substratkonzentration [S], Y = Reaktionsrate (Michaelis-Menten)
  • Temperaturregler bis 100 °C  |  Denaturierung ab 50/80 °C
  • Checkbox für thermostabile Enzyme  |  Zoom +30%
"""


import tkinter as tk
from tkinter import ttk
import math, random, time

# ═══════════════════════════════  KONSTANTEN  ═══════════════════════════════
BEAKER_X     = 60
BEAKER_Y     = 55
BEAKER_W     = 380
BEAKER_H     = 395
BEAKER_FLOOR = BEAKER_Y + BEAKER_H

BASE_SPEED   = 3.6
BASE_TEMP    = 25.0
TEMP_MAX     = 100

DENATURE_NORMAL = 50
DENATURE_THERMO = 80

ENZYME_R    = 28
SUBSTRATE_R = 9
COLL_DIST   = ENZYME_R + SUBSTRATE_R + 8

TICK_MS     = 30

# ═══════════════════════════════  THEME-SYSTEM  ══════════════════════════════
THEMES = {
    "dark": {
        "C_BG":        "#070b0f",
        "C_PANEL":     "#0c1520",
        "C_BORDER":    "#1a3a2a",
        "C_ACCENT":    "#00ff41",
        "C_BLUE":      "#00d4ff",
        "C_TEXT":      "#b8ffcc",
        "C_MUTED":     "#3d7a55",
        "C_WATER":     "#051a28",
        "C_ENZ_A":     "#00bfff",
        "C_ENZ_B":     "#0070c0",
        "C_ENZ_D":     "#3d3028",
        "C_ENZ_OL":    "#001a10",
        "C_ENZ_DOL":   "#1f1510",
        "C_SUB":       "#ffe000",
        "C_PROD":      "#ff6600",
        "C_GBG":       "#040810",
        "C_GGRID":     "#092015",
        "C_VMAX":      "#ff4040",
        "C_BTN_BG":    "#081808",
        "C_BTN_SEL":   "#001828",
        "C_ENTRY_BG":  "#081808",
        "C_START_BG":  "#001808",
        "C_RESET_BG":  "#001020",
        "C_CLEAR_BG":  "#180010",
        "C_CLEAR_FG":  "#ff4080",
        "C_PAUSE_BG":  "#181000",
        "C_PAUSE_FG":  "#ffcc00",
        "C_DONE_BG":   "#001030",
        "C_THSEL":     "#1a0800",
        "C_TROUGH":    "#0a2015",
        "C_TROUGHACT": "#0e2a1e",
        "C_GRID_BKR":  "#0c3040",
        "C_THERMO_BG": "#21262d",
        "C_THERMO_OL": "#7ab2cc",
        "C_TEMP_COOL": "#58a6ff",
        "C_CURVE": ["#58a6ff","#f78166","#3fb950","#d2a8ff","#e3b341","#8abeb7"],
        "C_KM":    "#d2a8ff",
        "FONT":    "Courier New",
    },
    "paper": {
        "C_BG":        "#f5f0e6",
        "C_PANEL":     "#ece5d0",
        "C_BORDER":    "#9a8050",
        "C_ACCENT":    "#1a6b1a",
        "C_BLUE":      "#1a3f8b",
        "C_TEXT":      "#1a1208",
        "C_MUTED":     "#7a6040",
        "C_WATER":     "#daeef8",
        "C_ENZ_A":     "#2060cc",
        "C_ENZ_B":     "#b06010",
        "C_ENZ_D":     "#9a7a5a",
        "C_ENZ_OL":    "#0a1050",
        "C_ENZ_DOL":   "#504030",
        "C_SUB":       "#d4900a",
        "C_PROD":      "#cc3300",
        "C_GBG":       "#faf6ec",
        "C_GGRID":     "#c8bfa0",
        "C_VMAX":      "#bb2020",
        "C_BTN_BG":    "#e2d8c0",
        "C_BTN_SEL":   "#d0c8a8",
        "C_ENTRY_BG":  "#f8f4ec",
        "C_START_BG":  "#d0edd0",
        "C_RESET_BG":  "#ccd4ed",
        "C_CLEAR_BG":  "#eddcd4",
        "C_CLEAR_FG":  "#bb2040",
        "C_PAUSE_BG":  "#ede8c4",
        "C_PAUSE_FG":  "#8b6a00",
        "C_DONE_BG":   "#ccd8ed",
        "C_THSEL":     "#e8e0c8",
        "C_TROUGH":    "#c8bfa0",
        "C_TROUGHACT": "#b0a888",
        "C_GRID_BKR":  "#b4cede",
        "C_THERMO_BG": "#e8dfc8",
        "C_THERMO_OL": "#8b7050",
        "C_TEMP_COOL": "#2060cc",
        "C_CURVE": ["#1a3f8b","#cc3300","#1a6b1a","#7a1a8b","#8b6b00","#006b5a"],
        "C_KM":    "#7a1a8b",
        "FONT":    "Georgia",
    },
}

_THEME_NAME = "dark"
_THEME      = THEMES["dark"]

C_BG = C_PANEL = C_BORDER = C_ACCENT = C_BLUE = C_TEXT = ""
C_MUTED = C_WATER = C_ENZ_A = C_ENZ_B = C_ENZ_D = ""
C_ENZ_OL = C_ENZ_DOL = C_SUB = C_PROD = C_GBG = C_GGRID = C_VMAX = ""


def apply_theme(name: str):
    global _THEME_NAME, _THEME
    global C_BG, C_PANEL, C_BORDER, C_ACCENT, C_BLUE, C_TEXT
    global C_MUTED, C_WATER, C_ENZ_A, C_ENZ_B, C_ENZ_D
    global C_ENZ_OL, C_ENZ_DOL, C_SUB, C_PROD, C_GBG, C_GGRID, C_VMAX
    _THEME_NAME = name
    _THEME = THEMES[name]
    C_BG      = _THEME["C_BG"]
    C_PANEL   = _THEME["C_PANEL"]
    C_BORDER  = _THEME["C_BORDER"]
    C_ACCENT  = _THEME["C_ACCENT"]
    C_BLUE    = _THEME["C_BLUE"]
    C_TEXT    = _THEME["C_TEXT"]
    C_MUTED   = _THEME["C_MUTED"]
    C_WATER   = _THEME["C_WATER"]
    C_ENZ_A   = _THEME["C_ENZ_A"]
    C_ENZ_B   = _THEME["C_ENZ_B"]
    C_ENZ_D   = _THEME["C_ENZ_D"]
    C_ENZ_OL  = _THEME["C_ENZ_OL"]
    C_ENZ_DOL = _THEME["C_ENZ_DOL"]
    C_SUB     = _THEME["C_SUB"]
    C_PROD    = _THEME["C_PROD"]
    C_GBG     = _THEME["C_GBG"]
    C_GGRID   = _THEME["C_GGRID"]
    C_VMAX    = _THEME["C_VMAX"]

apply_theme("dark")


def _apply_ttk_style(root_widget):
    st = ttk.Style(root_widget)
    st.theme_use("clam")
    st.configure("Horizontal.TScale",
                 background=_THEME["C_PANEL"],
                 troughcolor=_THEME["C_TROUGH"],
                 sliderthickness=18, sliderrelief="flat",
                 slidecolor=C_ACCENT)
    st.map("Horizontal.TScale",
           background=[("active", _THEME["C_PANEL"])],
           troughcolor=[("active", _THEME["C_TROUGHACT"])])


# ═══════════════════════════════  PHYSIK  ════════════════════════════════════
def rgt_factor(temp: float) -> float:
    return 2.0 ** ((temp - BASE_TEMP) / 10.0)

def get_denat_frac(temp: float, thermostable: bool) -> float:
    if thermostable:
        if temp >= 90: return 1.0
        elif temp >= 70: return (temp - 70) / 20.0
        return 0.0
    else:
        if temp >= 60: return 1.0
        elif temp >= 40: return 0.25 + 0.75 * ((temp - 40) / 20.0)
        return 0.0

def mm_rate(s: float, n_enz: int, temp: float, thermostable: bool) -> float:
    fac        = rgt_factor(temp)
    denat_frac = get_denat_frac(temp, thermostable)
    active_enz = n_enz * (1.0 - denat_frac)
    vmax       = active_enz * 14.0 * fac
    km         = 20.0
    if s <= 0: return 0.0
    effective_s = min(s, 150.0)
    v = vmax * effective_s / (km + effective_s)
    if s > 190.0:
        drop = 0.25 * (1.0 - math.exp(-(s - 190.0) / 60.0))
        v *= (1.0 - drop)
    return v


# ═══════════════════════════════  ZEICHNEN  ══════════════════════════════════
def _enzyme_pts(cx, cy, r):
    pts = []
    for i in range(6):
        a = math.pi - (math.pi * 0.35) * (i / 5)
        pts.extend([cx + r*math.cos(a), cy - r*0.8*math.sin(a)])
    x0,y0 = cx-r*0.4,  cy-r*0.7
    x1,y1 = cx-r*0.25, cy-r*0.2
    x2,y2 = cx-r*0.1,  cy-r*0.2
    x3,y3 = cx-r*0.05, cy-r*0.5
    x4,y4 = cx+r*0.05, cy-r*0.5
    x5,y5 = cx+r*0.1,  cy-r*0.2
    x6,y6 = cx+r*0.25, cy-r*0.2
    x7,y7 = cx+r*0.4,  cy-r*0.7
    pts.extend([x0,y0,x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,x6,y6,x7,y7])
    for i in range(6):
        a = math.pi*0.35 - (math.pi*0.35)*(i/5)
        pts.extend([cx+r*math.cos(a), cy-r*0.8*math.sin(a)])
    for i in range(1, 20):
        a = -math.pi*i/20
        pts.extend([cx+r*math.cos(a), cy-r*0.8*math.sin(a)])
    return pts

def _hexagon_pts(cx, cy, r):
    pts = []
    for i in range(6):
        pts.extend([cx+r*math.cos(math.pi/3*i), cy+r*math.sin(math.pi/3*i)])
    return pts

def _blob_pts(cx, cy, r, seed):
    rng = random.Random(seed)
    n   = 14; pts = []
    for i in range(n):
        t  = 2*math.pi*i/n
        br = r*rng.uniform(0.48, 1.12) + 0.18*r*math.sin(t*3+rng.random()*6)
        bry= r*0.56*rng.uniform(0.65, 1.0)
        pts += [cx+br*math.cos(t), cy+bry*math.sin(t)]
    return pts

def draw_enzyme(canvas, cx, cy, r, state: str, seed: int, tags):
    if state == "denatured":
        pts = _blob_pts(cx, cy, r, seed)
        canvas.create_polygon(pts, fill=C_ENZ_D, outline=C_ENZ_DOL,
                              width=1.5, smooth=False, tags=tags)
        s = r*0.38
        canvas.create_line(cx-s,cy-s, cx+s,cy+s, fill="#cc4444", width=2.5,
                           capstyle=tk.ROUND, tags=tags)
        canvas.create_line(cx+s,cy-s, cx-s,cy+s, fill="#cc4444", width=2.5,
                           capstyle=tk.ROUND, tags=tags)
    else:
        fill = C_ENZ_B if state == "binding" else C_ENZ_A
        pts  = _enzyme_pts(cx, cy, r)
        canvas.create_polygon(pts, fill=fill, outline=C_ENZ_OL,
                              width=1.5, smooth=False, tags=tags)
        if state == "binding":
            draw_substrate(canvas, cx, cy-r*0.3, SUBSTRATE_R*0.8, C_SUB, tags)

def draw_substrate(canvas, cx, cy, r, color, tags):
    hr  = r*0.85
    hx1 = cx-hr*0.95; hx2 = cx+hr*0.95
    outline_col = "#111" if _THEME_NAME == "dark" else "#333"
    canvas.create_line(hx1,cy, hx2,cy, fill=outline_col, width=1.5, tags=tags)
    canvas.create_polygon(_hexagon_pts(hx1,cy,hr), fill=color,
                          outline=outline_col, width=1, tags=tags)
    canvas.create_polygon(_hexagon_pts(hx2,cy,hr), fill=color,
                          outline=outline_col, width=1, tags=tags)

def draw_product(canvas, cx, cy, r, color, tags):
    outline_col = "#111" if _THEME_NAME == "dark" else "#333"
    canvas.create_polygon(_hexagon_pts(cx, cy, r*0.85), fill=color,
                          outline=outline_col, width=1, tags=tags)


# ═══════════════════════════════  PARTIKEL  ══════════════════════════════════
class Enzyme:
    def __init__(self, x, y):
        ang = random.uniform(0, 2*math.pi)
        spd = BASE_SPEED*0.44
        self.x, self.y   = float(x), float(y)
        self.vx, self.vy = math.cos(ang)*spd, math.sin(ang)*spd
        self.binding_timer = 0
        self.denatured     = False
        self.seed          = random.randint(10000, 99999)

    def check_denaturation(self, remaining):
        if self.denatured: return
        if hasattr(self,'denature_threshold') and remaining <= self.denature_threshold:
            self.denatured = True

    @property
    def state(self):
        if self.denatured:        return "denatured"
        if self.binding_timer > 0: return "binding"
        return "active"

    def move(self, factor, xmn, xmx, ymn, ymx):
        f = factor*(0.08 if self.denatured else 1.0)
        self.x += self.vx*f; self.y += self.vy*f
        if self.x < xmn or self.x > xmx: self.vx *= -1; self.x = max(xmn,min(xmx,self.x))
        if self.y < ymn or self.y > ymx: self.vy *= -1; self.y = max(ymn,min(ymx,self.y))

class Substrate:
    def __init__(self, x, y):
        ang = random.uniform(0, 2*math.pi)
        self.base_spd = BASE_SPEED*random.uniform(2.0, 2.8)
        self.x, self.y   = float(x), float(y)
        self.vx, self.vy = math.cos(ang)*self.base_spd, math.sin(ang)*self.base_spd
        self.reacted      = False

    def move(self, factor, xmn, xmx, ymn, ymx, enzymes=None, remaining=100):
        if enzymes:
            min_dist = float('inf'); target = None
            for e in enzymes:
                if not e.denatured and e.binding_timer == 0:
                    dist = math.hypot(e.x-self.x, e.y-self.y)
                    if dist < min_dist: min_dist = dist; target = e
            if target:
                dx = target.x-self.x; dy = target.y-self.y
                dist = max(min_dist, 1.0)
                pull = 0.3 if remaining < 10 else 0.1
                self.vx += (dx/dist)*pull; self.vy += (dy/dist)*pull
                cur_spd = math.hypot(self.vx, self.vy)
                if cur_spd > 0:
                    self.vx = (self.vx/cur_spd)*self.base_spd
                    self.vy = (self.vy/cur_spd)*self.base_spd
        self.x += self.vx*factor; self.y += self.vy*factor
        if self.x < xmn or self.x > xmx: self.vx *= -1; self.x = max(xmn,min(xmx,self.x))
        if self.y < ymn or self.y > ymx: self.vy *= -1; self.y = max(ymn,min(ymx,self.y))

class Product:
    def __init__(self, x, y):
        ang = random.uniform(0, 2*math.pi)
        spd = BASE_SPEED*0.36
        self.x, self.y   = float(x), float(y)
        self.vx, self.vy = math.cos(ang)*spd, math.sin(ang)*spd

    def move(self, factor, xmn, xmx, ymn, ymx):
        self.x += self.vx*factor*0.45; self.y += self.vy*factor*0.45
        if self.x < xmn or self.x > xmx: self.vx *= -1; self.x = max(xmn,min(xmx,self.x))
        if self.y < ymn or self.y > ymx: self.vy *= -1; self.y = max(ymn,min(ymx,self.y))


# ═══════════════════════════════  HAUPTKLASSE  ═══════════════════════════════
class EnzymeSim:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("⚗ ENZYM-SIMULATOR v3 | Michaelis-Menten-Kinetik")
        root.configure(bg=C_BG)
        root.resizable(False, False)

        self.running      = False
        self.thermostable = tk.BooleanVar(value=False)
        self.enzymes:    list = []
        self.substrates: list = []
        self.products:   list = []
        self.reactions_done = 0
        self.run_count      = 0
        self.data_points: list = []
        self._win_count = 0
        self._win_time  = 0.0
        self._accumulated_time = 0.0
        self._last_tick_time   = 0.0
        self._run_start_substrates = 0
        self.scale     = 1.0
        self.is_zoomed = False

        self._build_ui()
        self._reset()

    # ─────────────────────────────  UI-AUFBAU  ───────────────────────────────
    def _build_ui(self):
        sc = getattr(self, 'scale', 1.0)
        TH = _THEME
        FN = TH["FONT"]
        F  = (FN, int(10*sc))
        FB = (FN, int(10*sc), "bold")
        FT = (FN, int(13*sc), "bold")
        FS = (FN, int(8*sc))
        FM = (FN, int(9*sc))

        self.outer = tk.Frame(self.root, bg=C_BG)
        self.outer.pack(padx=int(14*sc), pady=int(14*sc))

        # ── Linke Spalte ──────────────────────────────────────────────────────
        left = tk.Frame(self.outer, bg=C_BG)
        left.grid(row=0, column=0, sticky="n", padx=(0, int(14*sc)))

        self.lbl_title = tk.Label(left, text="⚗  ENZYM-SIMULATOR",
                 bg=C_BG, fg=C_ACCENT,
                 font=(FN, int(22*sc), "bold"), cursor="hand2")
        self.lbl_title.pack(anchor="w", pady=(0,0))
        
        license_text = "m.poehl & Antigravity (2026)\nLizenz: MIT License"
        self.lbl_title.bind("<Enter>", lambda e: self._show_title_tooltip(e, license_text))
        self.lbl_title.bind("<Leave>", self._hide_title_tooltip)
        tk.Label(left, text="   Substratkonzentration  ·  Michaelis-Menten-Kinetik",
                 bg=C_BG, fg=C_MUTED,
                 font=(FN, int(9*sc))).pack(anchor="w", pady=(0,2))
        tk.Label(left, text="─"*56,
                 bg=C_BG, fg=C_BORDER,
                 font=(FN, int(8*sc))).pack(anchor="w", pady=(0, int(6*sc)))

        cw = BEAKER_X*2 + BEAKER_W
        ch = BEAKER_Y*2 + BEAKER_H
        self.can_b = tk.Canvas(left, width=cw, height=ch,
                               bg=C_BG, highlightthickness=0)
        self.can_b.pack()

        # Statistik
        sf = tk.Frame(left, bg=C_PANEL)
        sf.pack(fill="x", pady=(8,0))
        self.lbl_react = self._stat(sf, "Reaktionen:",        "white",   0)
        self.lbl_rate  = self._stat(sf, "Reaktionsgeschw.:",  C_BLUE,    1)
        self.lbl_sub   = self._stat(sf, "Substrat ♻:",        C_SUB,     2)

        # Sim-Speed + Zoom
        speed_f = tk.Frame(left, bg=C_PANEL)
        speed_f.pack(fill="x", pady=(8,0))
        tk.Label(speed_f, text="⏱  SIM-SPEED:",
                 bg=C_PANEL, fg=C_TEXT,
                 font=(FN, int(9*sc))).pack(side="left", padx=(10,4), pady=6)

        self.sim_speed_var = tk.DoubleVar(value=1.0)
        ttk.Scale(speed_f, from_=0.1, to=2.6, orient="horizontal",
                  variable=self.sim_speed_var,
                  length=int(200*sc)).pack(side="left", padx=4, pady=6)

        self.zoom_var = tk.BooleanVar(value=self.is_zoomed)
        tk.Checkbutton(speed_f, text="[ ZOOM +30% ]",
                       variable=self.zoom_var, command=self._toggle_zoom,
                       bg=C_PANEL, fg=C_BLUE,
                       font=(FN, int(9*sc)), selectcolor=TH["C_BTN_SEL"],
                       activebackground=C_PANEL,
                       activeforeground=C_BLUE).pack(side="right", padx=10)

        # ── Theme-Toggle (neu, unter Sim-Speed) ───────────────────────────────
        theme_f = tk.Frame(left, bg=C_PANEL)
        theme_f.pack(fill="x", pady=(0, 0))

        tk.Label(theme_f, text="🎨  DESIGN:",
                 bg=C_PANEL, fg=C_MUTED,
                 font=(FN, int(9*sc))).pack(side="left", padx=(10,6), pady=5)

        # Segmented-Control Container
        seg = tk.Frame(theme_f, bg=C_BORDER, padx=1, pady=1)
        seg.pack(side="left")

        is_dark   = (_THEME_NAME == "dark")
        dark_bg   = C_ACCENT if is_dark else TH["C_BTN_BG"]
        dark_fg   = C_BG     if is_dark else C_MUTED
        paper_bg  = TH["C_BTN_BG"] if is_dark else C_ACCENT
        paper_fg  = C_MUTED        if is_dark else C_BG

        self._btn_dark = tk.Button(
            seg, text="dunkel",
            font=(FN, int(9*sc), "bold"),
            bg=dark_bg, fg=dark_fg, relief="flat", bd=0,
            padx=10, pady=3, cursor="hand2",
            command=lambda: self._toggle_theme("dark"))
        self._btn_dark.pack(side="left")

        self._btn_paper = tk.Button(
            seg, text="hell",
            font=(FN, int(9*sc), "bold"),
            bg=paper_bg, fg=paper_fg, relief="flat", bd=0,
            padx=10, pady=3, cursor="hand2",
            command=lambda: self._toggle_theme("paper"))
        self._btn_paper.pack(side="left")

        # ── Rechte Spalte ─────────────────────────────────────────────────────
        right = tk.Frame(self.outer, bg=C_BG)
        right.grid(row=0, column=1, sticky="n")

        # ── Steuerbox ──
        ctrl = self._box(right, "  ⚙  Steuerung")
        ctrl.pack(fill="x", pady=(0,10), ipadx=8, ipady=8)

        self.temp_var = tk.DoubleVar(value=25.0)
        self._srow(ctrl, 0, "🌡  Temperatur:", self.temp_var, 0, TEMP_MAX, " °C",
                   cb=self._on_temp, entry=True)

        self.lbl_rgt = tk.Label(ctrl, text="RGT-Faktor: 1.00×  (Basis 25 °C)",
                                bg=C_PANEL, fg=C_MUTED, font=FS)
        self.lbl_rgt.grid(row=1, column=0, columnspan=4, sticky="w", padx=10)

        self.lbl_denat = tk.Label(ctrl, text="", bg=C_PANEL, fg="#f78166", font=FS)
        self.lbl_denat.grid(row=2, column=0, columnspan=4, sticky="w", padx=10)

        tk.Frame(ctrl, height=1, bg=C_BORDER).grid(
            row=3, column=0, columnspan=4, sticky="ew", pady=5)

        self.enz_var = tk.IntVar(value=4)
        self._srow(ctrl, 4, "🧬  Enzyme:", self.enz_var, 1, 20, "",
                   entry=True, cb=lambda v: self._draw_graph())

        tk.Frame(ctrl, height=1, bg=C_BORDER).grid(
            row=5, column=0, columnspan=4, sticky="ew", pady=5)

        self.sub_var = tk.IntVar(value=100)
        self._srow(ctrl, 6, "🟡  Substrate:", self.sub_var, 1, 200, "", entry=True)

        tk.Frame(ctrl, height=1, bg=C_BORDER).grid(
            row=7, column=0, columnspan=4, sticky="ew", pady=5)

        tf = tk.Frame(ctrl, bg=C_PANEL)
        tf.grid(row=8, column=0, columnspan=4, sticky="w", padx=10, pady=4)
        tk.Checkbutton(tf, text="🔥  Thermostabile Enzyme  [ Denat. ab 80 °C ]",
                       variable=self.thermostable, command=self._on_thermo,
                       bg=C_PANEL, fg=C_TEXT, font=FM,
                       selectcolor=_THEME["C_THSEL"],
                       activebackground=C_PANEL,
                       activeforeground="#ff8040").pack(anchor="w")

        bf = tk.Frame(ctrl, bg=C_PANEL)
        bf.grid(row=9, column=0, columnspan=4, pady=(10,4))
        self.btn_s = tk.Button(bf, text="▶  START", font=FB,
                               bg=_THEME["C_START_BG"], fg=C_ACCENT,
                               activebackground=_THEME["C_BTN_BG"],
                               activeforeground=C_ACCENT,
                               relief="flat", bd=0,
                               highlightbackground=C_ACCENT, highlightthickness=1,
                               padx=14, pady=6, cursor="hand2",
                               command=self._toggle)
        self.btn_s.pack(side="left", padx=4)

        tk.Button(bf, text="⟳  RESET", font=FB,
                  bg=_THEME["C_RESET_BG"], fg=C_BLUE,
                  activebackground=_THEME["C_BTN_BG"], activeforeground=C_BLUE,
                  relief="flat", bd=0,
                  highlightbackground=C_BLUE, highlightthickness=1,
                  padx=14, pady=6, cursor="hand2",
                  command=self._reset).pack(side="left", padx=4)

        tk.Button(bf, text="🗑  GRAPH ×", font=FB,
                  bg=_THEME["C_CLEAR_BG"], fg=_THEME["C_CLEAR_FG"],
                  activebackground=_THEME["C_BTN_BG"],
                  activeforeground=_THEME["C_CLEAR_FG"],
                  relief="flat", bd=0,
                  highlightbackground=_THEME["C_CLEAR_FG"], highlightthickness=1,
                  padx=14, pady=6, cursor="hand2",
                  command=self._clear_graph).pack(side="left", padx=4)

        self._legend(ctrl, row=10)

        # ── Graph-Box ──
        self.gbox = self._box(right, "  📈  Michaelis-Menten-Diagramm")
        self.gbox.pack(fill="x", pady=(0,10), ipadx=8, ipady=6)
        
        self.gbox.bind("<Enter>", lambda e: self._show_title_tooltip(e, license_text))
        self.gbox.bind("<Leave>", self._hide_title_tooltip)

        gw = int(420*sc); gh = int(310*sc)
        self.can_g = tk.Canvas(self.gbox, width=gw, height=gh,
                               bg=C_GBG, highlightthickness=0)
        self.can_g.pack(padx=8, pady=(0,4))

        self.lbl_avg = tk.Label(self.gbox, text="",
                                bg=C_PANEL, fg=C_BLUE,
                                font=(FN, int(9*sc)))
        self.lbl_avg.pack(anchor="w", padx=10)

        self.show_curve_var = tk.BooleanVar(value=False)
        self.show_km_var    = tk.BooleanVar(value=False)

        chk_f = tk.Frame(self.gbox, bg=C_PANEL)
        chk_f.pack(anchor="e", padx=10, pady=(0,4))

        self.cb_km = tk.Checkbutton(chk_f, text="[ Km einblenden ]",
                                    variable=self.show_km_var,
                                    command=self._draw_graph,
                                    state="disabled",
                                    bg=C_PANEL, fg=_THEME["C_KM"],
                                    font=(FN, int(9*sc)),
                                    selectcolor=_THEME["C_BTN_SEL"],
                                    activebackground=C_PANEL,
                                    activeforeground=_THEME["C_KM"])
        self.cb_km.pack(side="left", padx=(0,10))

        def _on_vmax_toggle():
            if self.show_curve_var.get():
                self.cb_km.config(state="normal")
            else:
                self.show_km_var.set(False)
                self.cb_km.config(state="disabled")
            self._draw_graph()

        tk.Checkbutton(chk_f, text="[ Vmax + Kurve einblenden ]",
                       variable=self.show_curve_var,
                       command=_on_vmax_toggle,
                       bg=C_PANEL, fg=C_BLUE,
                       font=(FN, int(9*sc)),
                       selectcolor=_THEME["C_BTN_SEL"],
                       activebackground=C_PANEL,
                       activeforeground=C_BLUE).pack(side="left")

    # ─────────────────────────────  UI-HELFER  ───────────────────────────────
    def _box(self, parent, title):
        FN = _THEME["FONT"]
        return tk.LabelFrame(parent, text=title,
                             bg=C_PANEL, fg=C_ACCENT,
                             font=(FN, int(9*self.scale), "bold"),
                             relief="flat", bd=2,
                             highlightbackground=C_BORDER,
                             highlightthickness=1)

    def _show_tooltip(self, event, text):
        self._hide_tooltip()
        c = self.can_g
        tid = c.create_text(event.x, event.y-18, text=text,
                            fill=C_TEXT,
                            font=("Segoe UI", 9, "bold"), tags="tooltip")
        bbox = c.bbox(tid)
        if bbox:
            c.create_rectangle(bbox[0]-5, bbox[1]-3, bbox[2]+5, bbox[3]+3,
                                fill=C_PANEL, outline=C_BORDER, tags="tooltip_bg")
            c.tag_raise(tid)

    def _hide_tooltip(self, event=None):
        self.can_g.delete("tooltip"); self.can_g.delete("tooltip_bg")

    def _show_title_tooltip(self, event, text):
        if hasattr(self, "_t_tip") and self._t_tip: return
        self._t_tip = tk.Toplevel(self.root)
        self._t_tip.wm_overrideredirect(True)
        self._t_tip.wm_geometry(f"+{event.x_root+15}+{event.y_root+15}")
        
        bg = _THEME["C_PANEL"]
        fg = _THEME["C_TEXT"]
        ol = _THEME["C_BORDER"]
        
        frame = tk.Frame(self._t_tip, bg=ol, padx=1, pady=1)
        frame.pack()
        inner = tk.Frame(frame, bg=bg, padx=8, pady=4)
        inner.pack()
        
        tk.Label(inner, text=text, bg=bg, fg=fg,
                 font=(_THEME["FONT"], int(9*self.scale), "bold"),
                 justify="left").pack()

    def _hide_title_tooltip(self, event=None):
        if hasattr(self, "_t_tip") and self._t_tip:
            self._t_tip.destroy()
            self._t_tip = None

    def _stat(self, parent, label, color, col):
        FN = _THEME["FONT"]
        tk.Label(parent, text=label, bg=C_PANEL, fg=C_MUTED,
                 font=(FN, 8)).grid(row=0, column=col*2, padx=(10,2), pady=4)
        lbl = tk.Label(parent, text="–", bg=C_PANEL, fg=color,
                       font=(FN, 10, "bold"), width=6)
        lbl.grid(row=0, column=col*2+1, padx=(0,6))
        return lbl

    def _srow(self, parent, row, label, var, from_, to, unit, cb=None, entry=True):
        FN  = _THEME["FONT"]
        FB  = (FN, 10, "bold")
        FS  = (FN,  8)
        TH  = _THEME
        tk.Label(parent, text=label, bg=C_PANEL, fg=C_TEXT,
                 font=(FN, 10)).grid(row=row, column=0, sticky="w", padx=10, pady=(4,2))

        ev = tk.StringVar(value=str(int(var.get())))

        def _cmd(val):
            v = float(val)
            ev.set(str(int(v)))
            if cb: cb(v)

        def _adj(delta):
            v = max(float(from_), min(float(to), float(var.get())+delta))
            var.set(v); _cmd(v)

        sf = tk.Frame(parent, bg=C_PANEL)
        sf.grid(row=row, column=1, padx=4, pady=2)

        tk.Button(sf, text="-", font=FB,
                  bg=TH["C_BTN_BG"], fg=C_ACCENT, relief="flat",
                  highlightthickness=1, highlightbackground=C_BORDER,
                  command=lambda: _adj(-1), padx=4, pady=0).pack(side="left")

        ttk.Scale(sf, from_=from_, to=to, orient="horizontal",
                  variable=var, command=_cmd, length=140).pack(side="left", padx=4)

        tk.Button(sf, text="+", font=FB,
                  bg=TH["C_BTN_BG"], fg=C_ACCENT, relief="flat",
                  highlightthickness=1, highlightbackground=C_BORDER,
                  command=lambda: _adj(1), padx=4, pady=0).pack(side="left")

        ef = tk.Frame(parent, bg=C_PANEL)
        ef.grid(row=row, column=2, sticky="w", padx=4)
        
        ent = tk.Entry(ef, textvariable=ev, width=4,
                       bg=TH["C_ENTRY_BG"], fg=C_ACCENT,
                       insertbackground=C_ACCENT,
                       font=FB, relief="flat", bd=3,
                       highlightbackground=C_BORDER, highlightthickness=1, justify="center")
        ent.pack(side="left")
        
        def _on_enter(e):
            try:
                v = max(float(from_), min(float(to), float(ev.get())))
                var.set(v); _cmd(v)
            except ValueError:
                ev.set(str(int(var.get())))
        ent.bind("<Return>", _on_enter)
        ent.bind("<FocusOut>", _on_enter)

        if unit:
            tk.Label(ef, text=unit, bg=C_PANEL, fg=C_TEXT, font=(FN, 10)).pack(side="left", padx=(2,0))
    def _legend(self, parent, row):
        FN = _THEME["FONT"]
        FS = (FN, 8)
        fr = tk.Frame(parent, bg=C_PANEL)
        fr.grid(row=row, column=0, columnspan=4, sticky="w", padx=10, pady=(4,2))
        tk.Label(fr, text="Legende:", bg=C_PANEL, fg=C_MUTED,
                 font=FS).pack(side="left", padx=(0,6))
        for col, txt in [(C_ENZ_A,"aktives Enzym"),
                         (C_ENZ_D,"denaturiert"),
                         (C_SUB,"Substrat"),
                         (C_PROD,"Produkt")]:
            tk.Canvas(fr, width=13, height=13, bg=col,
                      highlightthickness=1,
                      highlightbackground=C_BORDER).pack(side="left", padx=(0,2))
            tk.Label(fr, text=txt, bg=C_PANEL, fg=C_MUTED,
                     font=FS).pack(side="left", padx=(0,8))


    # ─────────────────────────────  THEME TOGGLE  ────────────────────────────
    def _toggle_theme(self, name: str):
        if _THEME_NAME == name:
            return
        was_running = self.running
        self.running = False

        # Zustand sichern
        t_val  = self.temp_var.get()
        e_val  = self.enz_var.get()
        s_val  = self.sub_var.get()
        th_val = self.thermostable.get()
        cv_val = self.show_curve_var.get()
        km_val = self.show_km_var.get()
        sp_val = self.sim_speed_var.get()
        data   = list(self.data_points)
        rc     = self.run_count
        rd     = self.reactions_done

        apply_theme(name)
        self.root.configure(bg=C_BG)
        _apply_ttk_style(self.root)

        self.outer.destroy()
        self._build_ui()

        # Zustand wiederherstellen
        self.temp_var.set(t_val)
        self.enz_var.set(e_val)
        self.sub_var.set(s_val)
        self.thermostable.set(th_val)
        self.show_curve_var.set(cv_val)
        self.show_km_var.set(km_val)
        self.sim_speed_var.set(sp_val)
        self.data_points   = data
        self.run_count     = rc
        self.reactions_done= rd

        self._on_temp(t_val)
        self._draw_beaker()
        self._draw_particles()
        self._draw_graph()

        if was_running:
            self._last_tick_time = __import__("time").time()
            self.running = True
            self.btn_s.config(text="⏸  PAUSE",
                              bg=_THEME["C_PAUSE_BG"],
                              fg=_THEME["C_PAUSE_FG"])
            self._animate()

    # ─────────────────────────────  ZOOM  ────────────────────────────────────
    def _toggle_zoom(self):
        was_running = self.running
        self.running = False
        self.is_zoomed = self.zoom_var.get()
        new_scale  = 1.3 if self.is_zoomed else 1.0
        scale_ratio = new_scale / self.scale
        self.scale  = new_scale

        t_val  = self.temp_var.get()
        e_val  = self.enz_var.get()
        s_val  = self.sub_var.get()
        th_val = self.thermostable.get()
        cv_val = self.show_curve_var.get()
        sp_val = self.sim_speed_var.get()

        global SUBSTRATE_R, ENZYME_R, BEAKER_W, BEAKER_H, BEAKER_X, BEAKER_Y, BEAKER_FLOOR, COLL_DIST
        SUBSTRATE_R *= scale_ratio; ENZYME_R *= scale_ratio
        BEAKER_W = int(BEAKER_W*scale_ratio); BEAKER_H = int(BEAKER_H*scale_ratio)
        BEAKER_X = int(BEAKER_X*scale_ratio); BEAKER_Y = int(BEAKER_Y*scale_ratio)
        BEAKER_FLOOR = BEAKER_Y + BEAKER_H
        COLL_DIST = SUBSTRATE_R + ENZYME_R + 8*self.scale

        for e in self.enzymes:
            e.x *= scale_ratio; e.y *= scale_ratio
        for s in self.substrates:
            s.x *= scale_ratio; s.y *= scale_ratio
            s.base_spd *= scale_ratio; s.vx *= scale_ratio; s.vy *= scale_ratio
        for p in self.products:
            p.x *= scale_ratio; p.y *= scale_ratio
            p.vx *= scale_ratio; p.vy *= scale_ratio

        self.outer.destroy(); self._build_ui()
        self.temp_var.set(t_val); self.enz_var.set(e_val)
        self.sub_var.set(s_val); self.thermostable.set(th_val)
        self.show_curve_var.set(cv_val); self.sim_speed_var.set(sp_val)
        self._on_temp(t_val)
        if was_running:
            self.running = True; self._animate()

    # ─────────────────────────────  ZEICHNEN  ────────────────────────────────
    def _update_denat_thresholds(self):
        temp   = self.temp_var.get()
        thermo = self.thermostable.get()
        denat_frac = get_denat_frac(temp, thermo)
        n_enz  = len(self.enzymes)
        if n_enz == 0: return
        num_to_denature = round(n_enz*denat_frac)
        for e in self.enzymes:
            if hasattr(e,'denature_threshold'): delattr(e,'denature_threshold')
            e.denatured = False
        to_denature = random.sample(self.enzymes, num_to_denature)
        remaining = sum(1 for s in self.substrates if not s.reacted)
        if remaining == 0: remaining = int(self.sub_var.get())
        for e in to_denature:
            if temp >= (90 if thermo else 60):
                e.denature_threshold = float('inf')
            else:
                e.denature_threshold = random.randint(5, max(5, remaining-1))

    def _on_temp(self, val):
        temp   = float(val)
        f      = rgt_factor(temp)
        thermo = self.thermostable.get()
        t_mid  = DENATURE_THERMO if thermo else DENATURE_NORMAL
        self.lbl_rgt.config(text=f"RGT-Faktor: {f:.2f}×  (Basis 25 °C)")
        if temp >= t_mid+10:
            self.lbl_denat.config(text=f"⚠  T ≥ {t_mid+10} °C – Alle Enzyme denaturiert!")
        elif temp >= t_mid-10:
            self.lbl_denat.config(text=f"⚠  T ≥ {t_mid-10} °C – Enzyme denaturieren zunehmend!")
        else:
            self.lbl_denat.config(text="")
        self._update_denat_thresholds()
        remaining = sum(1 for s in self.substrates if not s.reacted)
        for e in self.enzymes: e.check_denaturation(remaining)
        self._draw_beaker(); self._draw_particles(); self._draw_graph()

    def _on_thermo(self):
        temp   = self.temp_var.get()
        thermo = self.thermostable.get()
        t_mid  = DENATURE_THERMO if thermo else DENATURE_NORMAL
        if temp >= t_mid+10:
            self.lbl_denat.config(text=f"⚠  T ≥ {t_mid+10} °C – Alle Enzyme denaturiert!")
        elif temp >= t_mid-10:
            self.lbl_denat.config(text=f"⚠  T ≥ {t_mid-10} °C – Enzyme denaturieren zunehmend!")
        else:
            self.lbl_denat.config(text="")
        self._update_denat_thresholds()
        remaining = sum(1 for s in self.substrates if not s.reacted)
        for e in self.enzymes: e.check_denaturation(remaining)
        self._draw_particles()

    def _draw_beaker(self):
        c = self.can_b
        c.delete("beaker")
        bx, by, bw = BEAKER_X, BEAKER_Y, BEAKER_W
        fl = BEAKER_FLOOR
        TH = _THEME

        # Wasserfläche
        c.create_rectangle(bx, by, bx+bw, fl,
                           fill=C_WATER, outline="", tags="beaker")

        # Raster
        grid_col = TH["C_GRID_BKR"]
        grid_sp  = int(20*getattr(self,'scale',1.0))
        for gx in range(bx, bx+bw+1, grid_sp):
            c.create_line(gx, by, gx, fl, fill=grid_col, width=1, tags="beaker")
        for gy in range(by, fl+1, grid_sp):
            c.create_line(bx, gy, bx+bw, gy, fill=grid_col, width=1, tags="beaker")

        # Becherwand (etwas angedeutet)
        wall_col = TH["C_THERMO_OL"]
        c.create_rectangle(bx, by, bx+bw, fl,
                           fill="", outline=wall_col, width=2, tags="beaker")

        # Temperatur-Text
        temp   = self.temp_var.get()
        thermo = self.thermostable.get()
        t_mid  = DENATURE_THERMO if thermo else DENATURE_NORMAL
        tc = "#f78166" if temp > t_mid-10 else C_TEXT
        c.create_text(bx+10, by+10, text=f"T = {temp:.0f} °C",
                      fill=tc, font=("Courier New", 9, "bold"),
                      anchor="w", tags="beaker")

        # Thermometer
        thermo_bg = TH["C_THERMO_BG"]
        thermo_ol = TH["C_THERMO_OL"]
        th_x, th_y = bx+bw-22, by+18
        c.create_rectangle(th_x-3, th_y, th_x+3, th_y+40,
                           fill=thermo_bg, outline=thermo_ol,
                           width=1, tags="beaker")
        fill_h   = min(40, max(2, int(40*temp/TEMP_MAX)))
        fill_col = "#f78166" if temp > t_mid-10 else TH["C_TEMP_COOL"]
        c.create_rectangle(th_x-2, th_y+40-fill_h, th_x+2, th_y+40,
                           fill=fill_col, outline="", tags="beaker")
        c.create_oval(th_x-6, th_y+36, th_x+6, th_y+52,
                      fill=fill_col, outline=thermo_ol,
                      width=1, tags="beaker")

    def _draw_particles(self):
        c = self.can_b
        c.delete("particle")
        for p in self.products:
            draw_product(c, p.x, p.y, SUBSTRATE_R, C_PROD, "particle")
        for s in self.substrates:
            if not s.reacted:
                draw_substrate(c, s.x, s.y, SUBSTRATE_R, C_SUB, "particle")
        for e in self.enzymes:
            draw_enzyme(c, e.x, e.y, ENZYME_R, e.state, e.seed, "particle")

    def _draw_graph(self):
        c = self.can_g
        c.delete("all")
        W, H   = int(420*self.scale), int(310*self.scale)
        PL, PR  = int(52*self.scale), int(14*self.scale)
        PT, PB  = int(18*self.scale), int(38*self.scale)
        gw, gh  = W-PL-PR, H-PT-PB
        TH      = _THEME
        FN      = TH["FONT"]

        n_enz  = int(self.enz_var.get())
        temp   = self.temp_var.get()
        thermo = self.thermostable.get()

        configs = set((p[2],p[3]) for p in self.data_points)
        configs.add((n_enz, temp))
        sorted_configs = sorted(list(configs))

        max_s = max(200, int(self.sub_var.get()))
        if self.data_points:
            max_s = max(max_s, max(p[0] for p in self.data_points))

        vmax_dict = {cfg: mm_rate(150.0, cfg[0], cfg[1], thermo) for cfg in sorted_configs}
        global_max_vmax = max(vmax_dict.values()) if vmax_dict else 0.0
        max_r = max(global_max_vmax*1.15, 0.5)

        # Hintergrund + Raster
        c.create_rectangle(PL, PT, PL+gw, PT+gh,
                           fill=C_GBG, outline=C_GGRID)
        for i in range(1,4):
            y = PT+gh*i//4
            c.create_line(PL, y, PL+gw, y, fill=C_GGRID, width=1)
            x = PL+gw*i//4
            c.create_line(x, PT, x, PT+gh, fill=C_GGRID, width=1)

        # Achsen
        c.create_line(PL, PT, PL, PT+gh+2, fill=C_MUTED, width=2)
        c.create_line(PL-2, PT+gh, PL+gw, PT+gh, fill=C_MUTED, width=2)

        # Beschriftung
        c.create_text(PL-36, PT+gh//2,
                      text="Reaktions-\ngeschwindigkeit",
                      fill=C_MUTED, font=(FN, 8), angle=90, justify="center")
        c.create_text(PL+gw//2, H-6,
                      text="Substratkonzentration [S]",
                      fill=C_MUTED, font=(FN, 8))

        curve_colors = TH["C_CURVE"]

        # MM-Kurven
        if self.show_curve_var.get():
            steps = 200
            for idx, cfg in enumerate(sorted_configs):
                ne, t = cfg
                col = curve_colors[idx % len(curve_colors)]
                pts_for_cfg = [p for p in self.data_points if p[2]==ne and p[3]==t]
                max_sim  = max((p[0] for p in pts_for_cfg), default=0)
                max_rate = max((p[1] for p in pts_for_cfg), default=0)
                vmax_val = vmax_dict[cfg]
                if max_sim > 0:
                    curve_pts = []
                    for i in range(steps+1):
                        s = max_sim*i/steps
                        v = mm_rate(s, ne, t, thermo)
                        x = PL+(s/max_s)*gw
                        y = PT+gh-min(v/max_r,1.0)*gh
                        curve_pts += [x, y]
                    if len(curve_pts) >= 4:
                        c.create_line(curve_pts, fill=col, width=2.5, smooth=True)

                if max_rate >= vmax_val*0.97:
                    vy = PT+gh-min(vmax_val/max_r,1.0)*gh
                    lid = c.create_line(PL, vy, PL+gw, vy,
                                        fill=col, width=2, dash=(6,4))
                    txt = f"V_max ({ne}E, {t:.0f}°C)"
                    tid = c.create_text(PL+gw-4, vy-7, text=txt,
                                        fill=col, font=("Segoe UI",7), anchor="e")
                    htxt = f"V_max = {vmax_val:.2f} /s"
                    c.tag_bind(lid, "<Enter>",  lambda e, tx=htxt: self._show_tooltip(e,tx))
                    c.tag_bind(lid, "<Leave>",  self._hide_tooltip)
                    c.tag_bind(tid, "<Enter>",  lambda e, tx=htxt: self._show_tooltip(e,tx))
                    c.tag_bind(tid, "<Leave>",  self._hide_tooltip)

                    if getattr(self,'show_km_var',None) and self.show_km_var.get():
                        km_val  = 20.0
                        km_x    = PL+(km_val/max_s)*gw
                        vy_half = PT+gh-min((vmax_val/2)/max_r,1.0)*gh
                        km_col  = TH["C_KM"]
                        c.create_line(PL, vy_half, km_x, vy_half,
                                      fill=km_col, width=1.5, dash=(2,2))
                        c.create_line(km_x, vy_half, km_x, PT+gh,
                                      fill=km_col, width=1.5, dash=(2,2))
                        c.create_text(km_x, PT+gh+8,  text="K_m",
                                      fill=km_col, font=("Segoe UI",7,"bold"), anchor="n")
                        c.create_text(PL-4, vy_half, text="V_max/2",
                                      fill=km_col, font=("Segoe UI",7,"bold"), anchor="e")

        # Messpunkte
        if not self.data_points:
            c.create_text(PL+gw//2, PT+gh//2,
                          text="[ SIMULATION STARTEN ]\n> warte auf Messdaten...",
                          fill=C_MUTED, font=(FN,9), justify="center")
        else:
            for (s_cnt, rate, ne, t) in self.data_points:
                x   = PL+(s_cnt/max_s)*gw
                y   = PT+gh-min(rate/max_r,1.0)*gh
                idx = sorted_configs.index((ne,t))
                col = curve_colors[idx % len(curve_colors)]
                oid = c.create_oval(x-5,y-5, x+5,y+5,
                                    fill=col, outline=C_BG, width=1.5)
                c.tag_bind(oid,"<Enter>",lambda e,s=s_cnt: self._show_tooltip(e,f"[S] = {s}"))
                c.tag_bind(oid,"<Leave>",self._hide_tooltip)

        # Achsenwerte
        c.create_text(PL, PT+gh+4, text="0",
                      fill=C_MUTED, font=("Segoe UI",7), anchor="n")
        c.create_text(PL+gw, PT+gh+4, text=str(int(max_s)),
                      fill=C_MUTED, font=("Segoe UI",7), anchor="n")
        c.create_text(PL-4, PT, text=f"{max_r:.1f}",
                      fill=C_MUTED, font=("Segoe UI",7), anchor="e")

    def _clear_graph(self):
        self.data_points.clear()
        self.lbl_avg.config(text="")
        self._draw_graph()

    # ─────────────────────────────  PARTIKEL  ────────────────────────────────
    def _init_particles(self):
        self.enzymes.clear(); self.substrates.clear(); self.products.clear()
        ex1,ex2 = BEAKER_X+ENZYME_R+6,    BEAKER_X+BEAKER_W-ENZYME_R-6
        ey1,ey2 = BEAKER_Y+ENZYME_R+20,   BEAKER_FLOOR-ENZYME_R-6
        sx1,sx2 = BEAKER_X+SUBSTRATE_R+6, BEAKER_X+BEAKER_W-SUBSTRATE_R-6
        sy1,sy2 = BEAKER_Y+SUBSTRATE_R+20, BEAKER_FLOOR-SUBSTRATE_R-6
        for _ in range(int(self.enz_var.get())):
            self.enzymes.append(Enzyme(random.uniform(ex1,ex2), random.uniform(ey1,ey2)))
        for _ in range(int(self.sub_var.get())):
            self.substrates.append(Substrate(random.uniform(sx1,sx2), random.uniform(sy1,sy2)))
        self._update_denat_thresholds()
        remaining = sum(1 for s in self.substrates if not s.reacted)
        for e in self.enzymes: e.check_denaturation(remaining)

    def _reset(self):
        self.running = False
        self.reactions_done = 0
        self._win_count = 0; self._win_time = 0.0
        self._accumulated_time = 0.0; self._last_tick_time = 0.0
        for attr in ('_finish_delay','_initial_rate'):
            if hasattr(self, attr): delattr(self, attr)
        self._init_particles()
        self.btn_s.config(text="▶  START",
                          bg=_THEME["C_START_BG"], fg=C_ACCENT)
        self.lbl_avg.config(text="")
        self._draw_beaker(); self._draw_particles()
        self._draw_graph();  self._refresh_stats()

    def _toggle(self):
        self.running = not self.running
        if self.running:
            if self.reactions_done == 0 and self._accumulated_time == 0.0:
                self.run_count += 1
                self._run_start_substrates = sum(1 for s in self.substrates if not s.reacted)
            self._last_tick_time = time.time()
            self.btn_s.config(text="⏸  PAUSE",
                              bg=_THEME["C_PAUSE_BG"],
                              fg=_THEME["C_PAUSE_FG"])
            self._animate()
        else:
            self.btn_s.config(text="▶  WEITER",
                              bg=_THEME["C_START_BG"], fg=C_ACCENT)

    # ─────────────────────────────  ANIMATION  ───────────────────────────────
    def _animate(self):
        if not self.running: return
        sim_speed = self.sim_speed_var.get()
        temp   = self.temp_var.get()
        thermo = self.thermostable.get()
        fac    = rgt_factor(temp)*sim_speed

        bx, by, bw = BEAKER_X, BEAKER_Y, BEAKER_W
        fl = BEAKER_FLOOR
        ex1,ex2 = bx+ENZYME_R+4,    bx+bw-ENZYME_R-4
        ey1,ey2 = by+ENZYME_R+18,   fl-ENZYME_R-4
        sx1,sx2 = bx+SUBSTRATE_R+4, bx+bw-SUBSTRATE_R-4
        sy1,sy2 = by+SUBSTRATE_R+18, fl-SUBSTRATE_R-4

        remaining = sum(1 for s in self.substrates if not s.reacted)
        for e in self.enzymes:
            e.check_denaturation(remaining)
            if e.binding_timer > 0: e.binding_timer -= 1
            else: e.move(fac, ex1, ex2, ey1, ey2)

        new_rx = 0
        for s in self.substrates:
            if s.reacted: continue
            s.move(fac, sx1, sx2, sy1, sy2, self.enzymes, remaining)
            for e in self.enzymes:
                if not e.denatured and e.binding_timer == 0:
                    if math.hypot(s.x-e.x, s.y-e.y) < COLL_DIST:
                        s.reacted = True
                        e.binding_timer = max(2, int(6/fac))
                        new_rx += 1
                        for _ in range(2):
                            self.products.append(
                                Product(s.x+random.uniform(-5,5),
                                        s.y+random.uniform(-5,5)))
                        break

        self.reactions_done += new_rx
        self._win_count     += new_rx

        for p in self.products:
            p.move(fac, sx1, sx2, sy1, sy2)

        now = time.time()
        real_dt = now - self._last_tick_time
        self._last_tick_time = now
        dt = real_dt*sim_speed

        if remaining > 0:
            self._accumulated_time += dt
            self._win_time         += dt

        if (not hasattr(self,'_initial_rate') and
           (self.reactions_done >= self._run_start_substrates*0.5 or remaining==0)):
            if self._accumulated_time > 0:
                self._initial_rate = self.reactions_done/self._accumulated_time

        if self._win_time >= 0.5 and remaining > 0:
            rate = self._win_count/self._win_time
            self.lbl_rate.config(text=f"{rate:.1f}")
            self._win_count = 0; self._win_time = 0.0

        self._draw_beaker(); self._draw_particles(); self._refresh_stats()

        if remaining == 0 and self.substrates:
            if not hasattr(self,'_finish_delay'): self._finish_delay = 30
            self._finish_delay -= 1
            if self._finish_delay <= 0:
                del self._finish_delay
                self._finish(); return

        self.root.after(TICK_MS, self._animate)

    def _finish(self):
        self.running = False
        self.btn_s.config(text="✓  FERTIG",
                          bg=_THEME["C_DONE_BG"], fg=C_BLUE)
        if self._accumulated_time > 0 and self._run_start_substrates > 0:
            n_e    = int(self.enz_var.get())
            temp   = self.temp_var.get()
            thermo = self.thermostable.get()
            rate_to_plot = mm_rate(self._run_start_substrates, n_e, temp, thermo)
            self.data_points.append((self._run_start_substrates, rate_to_plot, n_e, temp))
            self.lbl_avg.config(
                text=f"Lauf #{self.run_count}  ·  v₀: {rate_to_plot:.2f} /s  "
                     f"·  Start-[S]: {self._run_start_substrates}  "
                     f"·  {n_e} Enzyme  ·  T = {temp:.0f} °C")
        self._draw_graph()

    def _refresh_stats(self):
        remaining = sum(1 for s in self.substrates if not s.reacted)
        self.lbl_react.config(text=str(self.reactions_done))
        self.lbl_sub.config(text=str(remaining))


# ═══════════════════════════════  START  ═════════════════════════════════════
def main():
    root = tk.Tk()
    _apply_ttk_style(root)
    EnzymeSim(root)
    root.mainloop()

if __name__ == "__main__":
    main()
