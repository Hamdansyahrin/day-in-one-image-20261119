#!/usr/bin/env python3
"""Deterministic renderer for the news-image-20261119 entry.

Draws one illustrated newspaper front page -- "The Day in One Page" --
that sums up the world news of Thursday 19 November 2026 in a single
1024x1024 full-colour PNG: 3 illustrated lead stories, 10 illustrated
story cards, a stat strip, a dotted world map with 13 numbered pins and
32 one-line briefs (45 stories in all).

Build-time only: uses Pillow. No network, no randomness, no clock --
two runs produce byte-identical output.
"""

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 28
CW = W - 2 * MARGIN  # content width = 968

# --- palette: warm paper, deep navy ink, one crimson accent, gold -------
PAPER = (250, 246, 238)
CARD_BG = (255, 253, 248)
INK = (22, 30, 50)
INK_SOFT = (74, 82, 102)
NAVY = (23, 37, 66)
CRIMSON = (178, 32, 44)
GOLD = (196, 132, 30)
TEAL = (14, 92, 84)
GREEN = (43, 106, 58)
INDIGO = (60, 62, 138)
ORANGE = (190, 98, 18)
PLUM = (122, 52, 92)
RULE = (196, 188, 168)
MAP_DOT = (168, 178, 198)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/liberation/"
SERIF_B = FONT_DIR + "LiberationSerif-Bold.ttf"
SERIF = FONT_DIR + "LiberationSerif-Regular.ttf"
SANS = FONT_DIR + "LiberationSans-Regular.ttf"
SANS_B = FONT_DIR + "LiberationSans-Bold.ttf"
SANS_I = FONT_DIR + "LiberationSans-Italic.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# --- the day's news, researched from wire/press reports of 19 Nov 2026 --
# (headline, kicker, standfirst, scene key, pin lon/lat or None)
LEADS = [
    (
        "Trump, Xi and Putin hold first three-way summit",
        "SHENZHEN · APEC SUMMIT",
        "The US, Chinese and Russian presidents meet face to face for "
        "the first time: Ukraine, Iran, nuclear arms, trade and AI "
        "are all on the table.",
        "summit",
        (114.1, 22.5),
    ),
    (
        "Iran hits Gulf states after US strike on Qeshm",
        "MIDDLE EAST · THE WAR WIDENS",
        "Tehran retaliates across the Gulf as a tanker is struck "
        "near Hormuz and a Houthi missile is aimed at Riyadh.",
        "gulf",
        (56.3, 27.0),
    ),
    (
        "Anthropic's $81bn listing is the biggest in history",
        "MARKETS · RECORD IPO",
        "Priced at $83 a share, the Claude maker's Nasdaq debut "
        "values it near $1.5 trillion -- and tests the whole AI trade.",
        "ipo",
        (-74.0, 40.7),
    ),
]

# (headline, sub, section, icon key, pin lon/lat)
CARDS = [
    ("Ukraine hits Crimean Bridge for third time",
     "Traffic halted, damage assessed", "CONFLICT", "bridge",
     (35.0, 45.0)),
    ("World court to rule on Myanmar genocide case",
     "ICJ judgment on Rohingya claims", "JUSTICE", "scales",
     (4.3, 52.1)),
    ("Jeffries poised to be first Black US Speaker",
     "A 56-seat Senate majority won", "US POLITICS", "dome",
     (-77.0, 38.9)),
    ("Record rain floods the California coast",
     "San Francisco under flood alerts", "DISASTER", "rain",
     (-122.4, 37.8)),
    ("Cyclone Aqwan bears down on India's east coast",
     "Odisha braces for landfall", "DISASTER",
     "cyclone", (86.0, 20.0)),
    ("COP31 deadlocked as Pacific drought bites",
     "Fiji, Tonga declare emergencies", "CLIMATE", "leaf",
     (30.7, 36.9)),
    ("Voyager 1 reaches one light-day from Earth",
     "NASA's farthest probe ever", "SPACE", "dish",
     (-118.1, 34.1)),
    ("GTA VI goes on sale after a 13-year wait",
     "1,600 Bengaluru developers on it", "TECH & GAMES",
     "pad", (-80.2, 25.8)),
    ("Alcaraz beats Medvedev at the ATP Finals",
     "6-2 6-4 in the Turin group stage", "SPORT", "tennis",
     (7.7, 45.1)),
    ("Chelsea edge PSG on Buurman's late winner",
     "87' winner tops the WCL group", "SPORT",
     "football", (-0.1, 51.5)),
]

# (big number, label) -- all from today's reporting
STATS = [
    ("$83", "ANTHROPIC IPO PRICE"),
    ("$1.5tn", "ITS VALUATION"),
    ("-2.78%", "HANG SENG TODAY"),
    ("103.9", "DOLLAR INDEX · 19-MO HIGH"),
    ("€45bn", "EU LOAN FOR UKRAINE"),
    ("1 in 4", "CHILDREN IN WAR ZONES"),
]

GLANCE = [
    ("3", "superpowers at one table in Shenzhen"),
    ("56", "Senate seats for the Democrats"),
    ("3rd", "Crimean Bridge strike this week"),
    ("13", "years of waiting for GTA VI"),
    ("1", "light-day: Voyager 1's distance"),
    ("10-8", "Wattimena's darts upset of Littler"),
]

# (column header, [one-line briefs]) -- 8 per column, 32 in all
BRIEFS = [
    ("POLITICS & WAR", [
        "IAEA: N. Korea expands uranium work",
        "Ethiopia, Eritrea mass troops on border",
        "Israel opens ground op inside Gaza",
        "Israel delays E1 settlement plan",
        "Trump: Iran may seek chem-bio weapons",
        "Houthi missile aimed at Riyadh",
        "Five EU states plan Rwanda asylum deal",
        "Sudan drones drive civilian toll",
    ]),
    ("ECONOMY & SOCIETY", [
        "EU approves trade deal with Indonesia",
        "Seoul, Beijing expand cultural ties",
        "Australia jobless rate rises to 4.9%",
        "IMF deal unlocks $2.3bn for Egypt",
        "Gold, copper and bitcoin slide together",
        "Korea exam held under AI cheating curbs",
        "Pew: Islam to pass Christianity by 2035",
        "Awa group makes rare contact in Brazil",
    ]),
    ("SCIENCE · HEALTH · CLIMATE", [
        "US loses measles elimination status",
        "Ebola vaccines to be trialled in Congo",
        "Alzheimer's, brain tumour advances",
        "Blue whales up tenfold since whaling ban",
        "Webb telescope spots rare star merger",
        "NASA readies CRS-25 cargo launch",
        "Solar flare noted by sky-watchers",
        "Kenya drought deepens milk shortage",
    ]),
    ("SPORT & CULTURE", [
        "Bancroft: team all knew of 2018 plot",
        "England win ODI series in Australia",
        "Wattimena beats Littler 10-8 in darts",
        "Litton Das sets wicketkeeping record",
        "Pochettino starts at Man United",
        "'Human' is Cambridge word of the year",
        "Two-year-old Comté is best cheese",
        "Barty to enter tennis Hall of Fame",
    ]),
]

SECTION_COLORS = {
    "CONFLICT": CRIMSON, "JUSTICE": NAVY, "US POLITICS": NAVY,
    "DISASTER": ORANGE, "CLIMATE": GREEN, "SPACE": INDIGO,
    "TECH & GAMES": PLUM, "SPORT": TEAL,
}

# Dotted world map: land spans (lon_start, lon_end) per 5-degree
# latitude band centre, authored from a standard world outline.
MAP_BANDS = {
    75: [(40, 180)],
    70: [(-168, -125), (-45, -25), (35, 180)],
    65: [(-168, -120), (-45, -30), (30, 180)],
    60: [(-165, -95), (-50, -40), (5, 180)],
    55: [(-160, -70), (-5, 0), (2, 180)],
    50: [(-150, -70), (-2, 140)],
    45: [(-125, -68), (-2, 30), (35, 140)],
    40: [(-124, -72), (-9, 3), (10, 12), (18, 28), (44, 140),
         (138, 141)],
    35: [(-120, -75), (-6, 0), (10, 15), (22, 28), (28, 48),
         (48, 140), (135, 140)],
    30: [(-115, -80), (-10, 32), (48, 122)],
    25: [(-110, -90), (-13, 35), (43, 97), (100, 122)],
    20: [(-105, -87), (-15, 38), (72, 80), (92, 108)],
    15: [(-92, -80), (-17, 40), (73, 84), (95, 108)],
    10: [(-77, -62), (-13, 42), (77, 80), (97, 110)],
    5: [(-78, -55), (-9, 42), (95, 115), (120, 135)],
    0: [(-79, -50), (-9, 41), (97, 118), (125, 140)],
    -5: [(-77, -42), (12, 40), (105, 118), (131, 141)],
    -10: [(-75, -40), (13, 40), (113, 142)],
    -15: [(-72, -42), (14, 38), (114, 146)],
    -20: [(-70, -45), (15, 36), (44, 49), (114, 149)],
    -25: [(-68, -48), (17, 33), (115, 147)],
    -30: [(-68, -52), (19, 31), (117, 145)],
    -35: [(-71, -55), (20, 28), (118, 140), (172, 176)],
    -40: [(-72, -62), (168, 176)],
    -45: [(-73, -67)],
    -50: [(-73, -68)],
}


# ---------------------------------------------------------------- helpers
def text_w(dr, s, f):
    return dr.textlength(s, font=f)


def wrap(dr, text, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if text_w(dr, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_line(dr, text, f, max_w):
    """One line, ellipsised if needed."""
    if text_w(dr, text, f) <= max_w:
        return text
    while text and text_w(dr, text + "…", f) > max_w:
        text = text[:-1]
    return text + "…"


def spaced(dr, xy, text, f, fill, tracking=2):
    """Draw text with manual letter tracking (for kickers/labels)."""
    x, y = xy
    for ch in text:
        dr.text((x, y), ch, font=f, fill=fill)
        x += text_w(dr, ch, f) + tracking
    return x


# ---------------------------------------------------------------- scenes
def scene_summit(dr, box):
    x0, y0, x1, y1 = box
    # dusk sky bands
    bands = [(38, 54, 92), (58, 76, 116), (86, 102, 140), (120, 128, 156)]
    bh = (y1 - y0) // len(bands)
    for i, c in enumerate(bands):
        dr.rectangle([x0, y0 + i * bh, x1, y0 + (i + 1) * bh + 1], fill=c)
    # skyline silhouette (Shenzhen towers)
    towers = [(0.03, 0.52), (0.10, 0.34), (0.17, 0.58), (0.24, 0.28),
              (0.33, 0.48), (0.42, 0.38), (0.52, 0.55), (0.60, 0.30),
              (0.68, 0.50), (0.76, 0.36), (0.84, 0.54), (0.91, 0.42)]
    wdt = x1 - x0
    for fx, fh in towers:
        tx = x0 + fx * wdt
        dr.rectangle([tx, y1 - fh * (y1 - y0) - 14, tx + 0.055 * wdt, y1 - 12],
                     fill=(16, 24, 44))
    dr.rectangle([x0, y1 - 14, x1, y1], fill=(12, 18, 34))
    # three flags on poles above the skyline
    fy = y0 + 14
    fh2, fw2 = 26, 40
    for i, fx in enumerate((0.16, 0.46, 0.76)):
        px = x0 + fx * wdt
        dr.line([px, fy - 6, px, fy + fh2 + 16], fill=WHITE, width=2)
        fx0, fy0 = px + 2, fy
        if i == 0:  # United States: stripes + blue canton
            for s in range(5):
                col = (178, 34, 52) if s % 2 == 0 else WHITE
                dr.rectangle([fx0, fy0 + s * fh2 // 5, fx0 + fw2,
                              fy0 + (s + 1) * fh2 // 5], fill=col)
            dr.rectangle([fx0, fy0, fx0 + 17, fy0 + 13], fill=(40, 52, 118))
            for r in range(3):
                for c in range(4):
                    dr.point((fx0 + 3 + c * 4, fy0 + 3 + r * 4), fill=WHITE)
        elif i == 1:  # China: red field, gold stars
            dr.rectangle([fx0, fy0, fx0 + fw2, fy0 + fh2], fill=(206, 32, 40))
            dr.polygon([(fx0 + 7, fy0 + 4), (fx0 + 9, fy0 + 9),
                        (fx0 + 4, fy0 + 9)], fill=(244, 200, 60))
            for dx, dy in ((14, 3), (16, 7), (16, 11), (14, 14)):
                dr.point((fx0 + dx, fy0 + dy), fill=(244, 200, 60))
        else:  # Russia: white / blue / red
            for s, col in enumerate((WHITE, (40, 84, 166), (206, 40, 48))):
                dr.rectangle([fx0, fy0 + s * fh2 // 3, fx0 + fw2,
                              fy0 + (s + 1) * fh2 // 3], fill=col)


def scene_gulf(dr, box):
    x0, y0, x1, y1 = box
    dr.rectangle(box, fill=(30, 52, 84))                    # night sky
    for i in range(14):                                     # sparse stars
        sx = x0 + (i * 53) % (x1 - x0 - 8) + 4
        sy = y0 + (i * 29) % 34 + 4
        dr.point((sx, sy), fill=(210, 220, 240))
    sea_y = y0 + int((y1 - y0) * 0.66)
    dr.rectangle([x0, sea_y, x1, y1], fill=(16, 66, 84))    # sea
    for i in range(9):                                      # wave ticks
        wy = sea_y + 8 + i * 9
        dr.line([x0 + (i * 37) % 60 + 6, wy, x0 + (i * 37) % 60 + 30, wy],
                fill=(40, 104, 116), width=2)
    # tanker silhouette, right
    tx = x0 + int((x1 - x0) * 0.52)
    dr.polygon([(tx, sea_y - 4), (tx + 128, sea_y - 4), (tx + 116, sea_y + 8),
                (tx + 10, sea_y + 8)], fill=(10, 16, 26))
    dr.rectangle([tx + 18, sea_y - 16, tx + 104, sea_y - 4], fill=(10, 16, 26))
    dr.rectangle([tx + 84, sea_y - 27, tx + 96, sea_y - 16], fill=(10, 16, 26))
    # missile arc from left toward the tanker, with burst
    import math
    pts = []
    for t in range(21):
        u = t / 20.0
        mx = x0 + 14 + u * (tx + 40 - x0 - 14)
        my = sea_y - 8 - math.sin(u * math.pi) * 52 + u * 6
        pts.append((mx, my))
    dr.line(pts, fill=(244, 170, 60), width=3)
    bx, by = pts[-1]
    for a in range(0, 360, 30):
        r = 13 if a % 60 == 0 else 8
        dr.line([bx, by, bx + r * math.cos(math.radians(a)),
                 by + r * math.sin(math.radians(a))],
                fill=(240, 120, 50), width=2)
    dr.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(255, 210, 90))
    # island (Qeshm) left
    dr.polygon([(x0 + 6, sea_y + 2), (x0 + 44, sea_y - 12),
                (x0 + 84, sea_y + 2)], fill=(12, 20, 32))


def scene_ipo(dr, box):
    x0, y0, x1, y1 = box
    dr.rectangle(box, fill=NAVY)
    base = y1 - 16
    bars = [0.22, 0.34, 0.30, 0.48, 0.62, 0.58, 0.86]
    bw = (x1 - x0 - 90) // len(bars)
    for i, bh in enumerate(bars):
        bx = x0 + 14 + i * bw
        top = base - int(bh * (y1 - y0 - 46))
        col = (120, 140, 190) if i < len(bars) - 1 else GOLD
        dr.rectangle([bx, top, bx + bw - 8, base], fill=col)
    dr.line([x0 + 10, base, x1 - 76, base], fill=(150, 165, 200), width=2)
    # rising arrow
    dr.line([x0 + 18, base - 18, x1 - 96, y0 + 22], fill=GOLD, width=3)
    dr.polygon([(x1 - 96, y0 + 22), (x1 - 110, y0 + 24), (x1 - 98, y0 + 36)],
               fill=GOLD)
    # price tag
    f_big = font(SANS_B, 40)
    dr.text((x1 - 118, y0 + 40), "$83", font=f_big, fill=WHITE)
    f_tag = font(SANS_B, 13)
    dr.rounded_rectangle([x1 - 116, y0 + 88, x1 - 62, y0 + 110], radius=4,
                         fill=CRIMSON)
    dr.text((x1 - 104, y0 + 92), "ANT", font=f_tag, fill=WHITE)


# ---------------------------------------------------------------- icons
def icon(dr, key, box, color):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    w = 3
    if key == "bridge":
        dr.arc([x0 + 3, y0 + 8, x1 - 3, y1 + 12], 180, 360, fill=color, width=w)
        dr.line([x0 + 3, y1 - 6, x1 - 3, y1 - 6], fill=color, width=w)
        for fx in (0.3, 0.5, 0.7):
            sx = x0 + fx * (x1 - x0)
            dr.line([sx, y0 + 12, sx, y1 - 6], fill=color, width=2)
    elif key == "scales":
        dr.line([cx, y0 + 4, cx, y1 - 8], fill=color, width=w)
        dr.line([x0 + 5, y0 + 9, x1 - 5, y0 + 9], fill=color, width=w)
        for sx in (x0 + 9, x1 - 9):
            dr.polygon([(sx - 6, y1 - 12), (sx + 6, y1 - 12), (sx, y0 + 9)],
                       outline=color, width=2)
        dr.line([cx - 7, y1 - 4, cx + 7, y1 - 4], fill=color, width=w)
    elif key == "dome":
        dr.arc([cx - 11, y0 + 6, cx + 11, y0 + 26], 180, 360, fill=color, width=w)
        dr.line([cx, y0 + 2, cx, y0 + 7], fill=color, width=w)
        dr.rectangle([x0 + 5, y1 - 14, x1 - 5, y1 - 11], fill=color)
        for fx in (0.24, 0.42, 0.58, 0.76):
            sx = x0 + fx * (x1 - x0)
            dr.line([sx, y0 + 17, sx, y1 - 14], fill=color, width=2)
    elif key == "rain":
        dr.arc([x0 + 6, y0 + 4, x0 + 24, y0 + 20], 90, 270, fill=color, width=w)
        dr.arc([x0 + 14, y0 + 2, x1 - 4, y0 + 22], 270, 90, fill=color, width=w)
        dr.line([x0 + 8, y0 + 17, x1 - 8, y0 + 17], fill=color, width=w)
        for fx in (0.3, 0.5, 0.7):
            sx = x0 + fx * (x1 - x0)
            dr.line([sx, y1 - 11, sx - 3, y1 - 3], fill=color, width=2)
    elif key == "cyclone":
        import math
        pts = []
        for t in range(60):
            u = t / 59.0
            ang = u * 5.2
            r = 3 + u * (min(x1 - x0, y1 - y0) // 2 - 4)
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        dr.line(pts, fill=color, width=w)
    elif key == "leaf":
        dr.polygon([(x0 + 7, y1 - 6), (x0 + 10, y0 + 8), (x1 - 7, y0 + 5),
                    (x1 - 9, y1 - 9)], outline=color, width=w)
        dr.line([x0 + 9, y1 - 8, x1 - 10, y0 + 8], fill=color, width=2)
    elif key == "dish":
        dr.arc([x0 + 4, y0 + 6, x0 + 26, y1 - 4], 300, 130, fill=color, width=w)
        dr.line([x0 + 15, y0 + 16, x1 - 8, y0 + 5], fill=color, width=2)
        dr.line([cx - 2, y1 - 8, cx + 8, y1 - 16], fill=color, width=2)
        for r in (6, 11):
            dr.arc([x1 - 14 - r, y0 + 1 - r // 2, x1 - 14 + r,
                    y0 + 1 + r + r // 2], 300, 60, fill=color, width=2)
    elif key == "pad":
        dr.rounded_rectangle([x0 + 3, y0 + 10, x1 - 3, y1 - 8], radius=8,
                             outline=color, width=w)
        dr.line([x0 + 10, cy, x0 + 18, cy], fill=color, width=2)
        dr.line([x0 + 14, cy - 4, x0 + 14, cy + 4], fill=color, width=2)
        dr.ellipse([x1 - 15, cy - 6, x1 - 10, cy - 1], fill=color)
        dr.ellipse([x1 - 11, cy + 2, x1 - 6, cy + 7], fill=color)
    elif key == "tennis":
        dr.ellipse([x0 + 5, y0 + 5, x1 - 5, y1 - 5], outline=color, width=w)
        dr.arc([x0 - 4, y0 + 5, x0 + 16, y1 - 5], 270, 90, fill=color, width=2)
        dr.arc([x1 - 16, y0 + 5, x1 + 4, y1 - 5], 90, 270, fill=color, width=2)
    elif key == "football":
        dr.ellipse([x0 + 5, y0 + 5, x1 - 5, y1 - 5], outline=color, width=w)
        dr.polygon([(cx - 4, cy - 4), (cx + 4, cy - 4), (cx + 6, cy + 2),
                    (cx, cy + 6), (cx - 6, cy + 2)], fill=color)
        for dx, dy in ((-10, -8), (10, -8), (-11, 7), (11, 7), (0, 12)):
            dr.line([cx, cy, cx + dx, cy + dy], fill=color, width=1)


# ---------------------------------------------------------------- map
MAP_X, MAP_Y = MARGIN, 478
MAP_W, MAP_H = 620, 206
LON0, LAT0 = -170.0, 76.0
PX_PER_LON = MAP_W / 360.0
PX_PER_LAT = MAP_H / 126.0


def lonlat_to_xy(lon, lat):
    return (MAP_X + (lon - LON0) * PX_PER_LON,
            MAP_Y + (LAT0 - lat) * PX_PER_LAT)


def draw_map(dr):
    for lat, spans in MAP_BANDS.items():
        for lon_s, lon_e in spans:
            lon = lon_s
            while lon <= lon_e:
                x, y = lonlat_to_xy(lon + 2.5, lat)
                dr.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6],
                           fill=MAP_DOT)
                lon += 5
    # numbered pins for the 13 pictured stories; small nudges keep
    # clustered pins (US coasts, western Europe) from overlapping
    pins = [(i + 1,) + lead[4] for i, lead in enumerate(LEADS)]
    pins += [(i + 4,) + card[4] for i, card in enumerate(CARDS)]
    nudges = {3: (10, -7), 5: (11, -4), 6: (-8, 7), 7: (-5, -5),
              10: (9, 9), 12: (5, 11), 13: (-6, -2)}
    f_pin = font(SANS_B, 10)
    for num, lon, lat in pins:
        x, y = lonlat_to_xy(lon, lat)
        dx, dy = nudges.get(num, (0, 0))
        x, y = x + dx, y + dy
        dr.ellipse([x - 8, y - 8, x + 8, y + 8], fill=CRIMSON,
                   outline=WHITE, width=1)
        s = str(num)
        dr.text((x - text_w(dr, s, f_pin) / 2, y - 6), s, font=f_pin,
                fill=WHITE)


# ---------------------------------------------------------------- layout
def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(img)

    # masthead
    f_date = font(SANS_B, 12)
    f_title = font(SERIF_B, 47)
    f_sub = font(SANS, 12)
    dr.line([MARGIN, 18, W - MARGIN, 18], fill=INK, width=1)
    dr.text((MARGIN, 24), "THURSDAY · 19 NOVEMBER 2026", font=f_date,
            fill=INK)
    right = "45 STORIES · SIX CONTINENTS · ONE PAGE"
    dr.text((W - MARGIN - text_w(dr, right, f_date), 24), right,
            font=f_date, fill=INK)
    title = "THE DAY IN ONE PAGE"
    dr.text(((W - text_w(dr, title, f_title)) / 2, 42), title,
            font=f_title, fill=INK)
    sub = "The world's news of Thursday 19 November 2026, in a single image"
    dr.text(((W - text_w(dr, sub, f_sub)) / 2, 96), sub, font=f_sub,
            fill=INK_SOFT)
    dr.line([MARGIN, 118, W - MARGIN, 118], fill=INK, width=3)
    dr.line([MARGIN, 122, W - MARGIN, 122], fill=INK, width=1)

    # leads
    f_kick = font(SANS_B, 11)
    f_lead_h = font(SERIF_B, 22)
    f_stand = font(SANS, 12)
    lead_w = (CW - 32) // 3
    scenes = {"summit": scene_summit, "gulf": scene_gulf, "ipo": scene_ipo}
    for i, (headline, kicker, stand, scene, _pin) in enumerate(LEADS):
        x0 = MARGIN + i * (lead_w + 16)
        x1 = x0 + lead_w
        scenes[scene](dr, (x0, 130, x1, 240))
        dr.rectangle([x0, 130, x1, 240], outline=INK, width=1)
        spaced(dr, (x0, 248), kicker, f_kick, CRIMSON, tracking=1)
        y = 266
        for line in wrap(dr, headline, f_lead_h, lead_w)[:3]:
            dr.text((x0, y), line, font=f_lead_h, fill=INK)
            y += 26
        y += 2
        for line in wrap(dr, stand, f_stand, lead_w)[:4]:
            dr.text((x0, y), line, font=f_stand, fill=INK_SOFT)
            y += 15
        if i < 2:
            dr.line([x1 + 8, 130, x1 + 8, 392], fill=RULE, width=1)
    dr.line([MARGIN, 398, W - MARGIN, 398], fill=RULE, width=1)

    # stat strip
    dr.rectangle([MARGIN, 406, W - MARGIN, 452], fill=NAVY)
    f_num = font(SANS_B, 19)
    f_lab = font(SANS_B, 9)
    cell_w = CW / len(STATS)
    for i, (num, lab) in enumerate(STATS):
        cx = MARGIN + i * cell_w
        dr.text((cx + (cell_w - text_w(dr, num, f_num)) / 2, 411), num,
                font=f_num, fill=(240, 196, 92))
        lab_t = fit_line(dr, lab, f_lab, cell_w - 8)
        dr.text((cx + (cell_w - text_w(dr, lab_t, f_lab)) / 2, 434),
                lab_t, font=f_lab, fill=(214, 220, 234))
        if i:
            dr.line([cx, 412, cx, 446], fill=(52, 68, 102), width=1)

    # map + at a glance
    f_sec = font(SANS_B, 12)
    spaced(dr, (MARGIN, 458), "THE DAY ON THE MAP — 13 PICTURED STORIES",
           f_sec, INK, tracking=1)
    draw_map(dr)
    gx = MAP_X + MAP_W + 18
    dr.rectangle([gx, MAP_Y - 4, W - MARGIN, MAP_Y + MAP_H + 2],
                 fill=CARD_BG, outline=RULE, width=1)
    spaced(dr, (gx + 14, MAP_Y + 6), "AT A GLANCE", f_sec, CRIMSON,
           tracking=1)
    f_gn = font(SERIF_B, 20)
    f_gt = font(SANS, 12)
    gy = MAP_Y + 34
    for num, txt in GLANCE:
        dr.text((gx + 14, gy), num, font=f_gn, fill=NAVY)
        tx = gx + 14 + text_w(dr, num, f_gn) + 8
        lines = wrap(dr, txt, f_gt, W - MARGIN - tx - 10)[:2]
        for j, line in enumerate(lines):
            dr.text((tx, gy + 3 + j * 15), line, font=f_gt, fill=INK)
        gy += max(28, 10 + len(lines) * 15)

    # cards: two rows of five
    f_tag = font(SANS_B, 9)
    f_card_h = font(SANS_B, 13)
    f_card_s = font(SANS, 11)
    card_w = (CW - 32) // 5
    card_h = 94
    for idx, (headline, sub, section, icon_key, _pin) in enumerate(CARDS):
        row, col = divmod(idx, 5)
        x0 = MARGIN + col * (card_w + 8)
        y0 = 694 + row * (card_h + 8)
        x1, y1 = x0 + card_w, y0 + card_h
        color = SECTION_COLORS[section]
        dr.rectangle([x0, y0, x1, y1], fill=CARD_BG, outline=RULE, width=1)
        dr.rectangle([x0, y0, x0 + 4, y1], fill=color)
        icon(dr, icon_key, (x0 + 9, y0 + 7, x0 + 39, y0 + 37), color)
        tag = f"{idx + 4} · {section}"
        dr.text((x0 + 45, y0 + 15), tag, font=f_tag, fill=color)
        lines = wrap(dr, headline, f_card_h, card_w - 16)[:2]
        y = y0 + 44
        for line in lines:
            dr.text((x0 + 8, y), line, font=f_card_h, fill=INK)
            y += 15
        dr.text((x0 + 8, y0 + 76),
                fit_line(dr, sub, f_card_s, card_w - 16),
                font=f_card_s, fill=INK_SOFT)

    # briefs: four columns
    f_bh = font(SANS_B, 11)
    f_b = font(SANS, 11)
    dr.line([MARGIN, 894, W - MARGIN, 894], fill=INK, width=2)
    col_w = (CW - 24) // 4
    for ci, (header, items) in enumerate(BRIEFS):
        x0 = MARGIN + ci * (col_w + 8)
        spaced(dr, (x0, 900), header, f_bh, NAVY, tracking=0)
        y = 917
        for item in items:
            dr.text((x0, y), "· " + fit_line(dr, item, f_b, col_w - 12),
                    font=f_b, fill=INK)
            y += 11

    # footer
    f_foot = font(SANS_I, 9)
    foot = ("Compiled from wire and press reports of 19 November 2026 · "
            "Drawn programmatically — no photographs · "
            "make.fun news-image-20261119")
    dr.text(((W - text_w(dr, foot, f_foot)) / 2, 1010), foot,
            font=f_foot, fill=INK_SOFT)
    return img


if __name__ == "__main__":
    draw_page().save("entry.png")
    print("wrote entry.png")
