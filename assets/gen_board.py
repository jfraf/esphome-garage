#!/usr/bin/env python3
"""Erzeugt sensorplatine.html: Schaltplan + Lochraster-Layout (mit Netz-Prüfung)."""
import sys
import xml.etree.ElementTree as ET

OUT = sys.argv[1]
COLS, ROWS = 24, 18

# ---------- Netze: Leiterzüge auf der Lötseite, als Polylinien (Spalte, Reihe) ----------
NETS = {
    "SDA": [[(7, 4), (7, 1), (1, 1), (1, 17)]],
    "SCL": [[(6, 4), (6, 2), (2, 2), (2, 17)]],
    "3V3": [[(3, 4), (3, 6), (6, 6), (6, 8)]],
    "5V": [[(3, 13), (3, 18), (24, 18), (24, 6), (22, 6)]],
    "GND": [[(4, 13), (4, 17), (21, 17)], [(18, 12), (18, 17)]],
    "SIG": [[(8, 13), (8, 14), (15, 14)]],
    "BASE": [[(19, 12), (19, 14)]],
    "COIL": [[(19, 6), (20, 6), (20, 12), (21, 12)]],
    "COM": [[(19, 10), (17, 10), (17, 2)]],
    "NO": [[(19, 2), (19, 4), (22, 4)]],
}
NET_LABEL = {
    "SDA": "SDA (D5 / GPIO14)", "SCL": "SCL (D6 / GPIO12)", "3V3": "3,3 V",
    "5V": "+5 V", "GND": "GND", "SIG": "Relais-Signal (D1 / GPIO5)",
    "BASE": "Basis Q1", "COIL": "Kollektor Q1 / Spule", "COM": "Kontakt COM → J2",
    "NO": "Kontakt NO → J2",
}

# ---------- Bauteil-Pins: (Spalte, Reihe) -> erwartetes Netz (None = frei) ----------
TOP_HDR = ["3V3", "D8", "D7", "D6", "D5", "D0", "A0", "RST"]
BOT_HDR = ["5V", "GND", "D4", "D3", "D2", "D1", "RX", "TX"]
PINS = {}
HDR_NET = {"3V3": "3V3", "D6": "SCL", "D5": "SDA", "5V": "5V", "GND": "GND", "D1": "SIG"}
for i, n in enumerate(TOP_HDR):
    PINS[(3 + i, 4)] = HDR_NET.get(n)
for i, n in enumerate(BOT_HDR):
    PINS[(3 + i, 13)] = HDR_NET.get(n)
J1 = [("SDA", "SDA"), ("SCL", "SCL"), ("5V", "5V"), ("GND", "GND"), ("CFG", "GND")]
for i, (_, net) in enumerate(J1):
    PINS[(1 + i, 17)] = net
PINS.update({
    (17, 2): "COM", (19, 2): "NO",                       # J2
    (19, 5): None, (22, 5): None,                        # K1 Kontakt A/B (NO/NC)
    (19, 6): "COIL", (22, 6): "5V",                      # K1 Spule
    (19, 10): "COM", (22, 10): None,                     # K1 COM (intern verbunden)
    (18, 12): "GND", (19, 12): "BASE", (20, 12): "COIL",  # Q1 E, B, C
    (15, 14): "SIG", (19, 14): "BASE",                   # R1
    (11, 14): "SIG", (11, 17): "GND",                    # R2
    (1, 8): "SDA", (6, 8): "3V3",                        # R3
    (2, 7): "SCL", (6, 7): "3V3",                        # R4
    (21, 12): "COIL", (24, 12): "5V",                    # Diode (Kathode an 5 V)
    (21, 17): "GND", (21, 18): "5V",                     # C1
})


def expand(poly):
    pts = []
    for (c0, r0), (c1, r1) in zip(poly, poly[1:]):
        assert c0 == c1 or r0 == r1, f"schräges Segment {poly}"
        dc = (c1 > c0) - (c1 < c0)
        dr = (r1 > r0) - (r1 < r0)
        c, r = c0, r0
        pts.append((c, r))
        while (c, r) != (c1, r1):
            c, r = c + dc, r + dr
            pts.append((c, r))
    return pts


pad_net = {}
for net, polys in NETS.items():
    for poly in polys:
        for p in expand(poly):
            assert 1 <= p[0] <= COLS and 1 <= p[1] <= ROWS, (net, p)
            assert pad_net.get(p, net) == net, f"Kurzschluss {p}: {pad_net[p]} / {net}"
            pad_net[p] = net
for p, net in PINS.items():
    assert pad_net.get(p) == net, f"Pin {p}: erwartet {net}, Leiterzug {pad_net.get(p)}"
print("Netzprüfung ok:", len(pad_net), "belegte Lötaugen,", len(PINS), "Bauteil-Pins")

# ---------- SVG-Helfer ----------
S, MX, MY = 27, 44, 34
BW, BH = MX + (COLS - 1) * S + 30, MY + (ROWS - 1) * S + 30


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def T(x, y, s, cls="t", anchor="middle"):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}">{esc(s)}</text>'


def board(mirror):
    def X(c):
        return MX + ((COLS - c) if mirror else (c - 1)) * S

    def Y(r):
        return MY + (r - 1) * S

    o = []
    o.append(f'<rect x="{MX - 20}" y="{MY - 20}" width="{(COLS - 1) * S + 40}" height="{(ROWS - 1) * S + 40}" rx="6" class="brd"/>')
    for c in range(1, COLS + 1):
        o.append(T(X(c), MY - 24, str(c), "ax"))
    for r in range(1, ROWS + 1):
        o.append(T(MX - 26, Y(r) + 3, str(r), "ax", "end"))
    # Leiterzüge
    for net, polys in NETS.items():
        for poly in polys:
            pts = " ".join(f"{X(c)},{Y(r)}" for c, r in poly)
            o.append(f'<polyline points="{pts}" class="tr n-{net}{"" if mirror else " faint"}"/>')
    # Lötbrücken-Varianten für NO
    for (c, lab) in ((19, "A"), (22, "B")):
        o.append(f'<line x1="{X(c)}" y1="{Y(4)}" x2="{X(c)}" y2="{Y(5)}" class="brg"/>')
        if mirror:
            dx = 11 if (c == 19) else -11
            o.append(T(X(c) + dx, Y(4.5) + 3, lab, "tb"))
    # Lötaugen
    for c in range(1, COLS + 1):
        for r in range(1, ROWS + 1):
            o.append(f'<circle cx="{X(c)}" cy="{Y(r)}" r="2.6" class="pad"/>')

    if mirror:
        for (c, r), net in PINS.items():
            cls = f"jt n-{net}" if net else "jt n-free"
            o.append(f'<circle cx="{X(c)}" cy="{Y(r)}" r="5.2" class="{cls}"/>')
        for i, n in enumerate(TOP_HDR):
            o.append(T(X(3 + i), Y(4) + 17, n, "ts"))
        for i, n in enumerate(BOT_HDR):
            o.append(T(X(3 + i), Y(13) - 10, n, "ts"))
        for i, (n, _) in enumerate(J1):
            o.append(T(X(1 + i), Y(17) - 10, n, "ts"))
        o.append(T(X(17), Y(2) - 10, "COM", "ts"))
        o.append(T(X(19), Y(2) - 10, "NO", "ts"))
        o.append(T(X(20.5), Y(8) + 3, "K1", "tm"))
        o.append(T(X(19), Y(12) + 17, "B", "ts"))
        o.append(T(X(18) + 9, Y(12) - 9, "E", "ts"))
        o.append(T(X(20) - 9, Y(12) - 9, "C", "ts"))
        o.append(T(X(9), Y(9), "D1 mini (von unten)", "tm"))
        return "\n".join(o)

    # ----- Bestückungsseite -----
    def res(p0, p1, label, lx, ly, anchor="start"):
        (c0, r0), (c1, r1) = p0, p1
        x0, y0, x1, y1 = X(c0), Y(r0), X(c1), Y(r1)
        o.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" class="lead"/>')
        if r0 == r1:
            mx = (x0 + x1) / 2
            o.append(f'<rect x="{mx - 24}" y="{y0 - 6}" width="48" height="12" rx="3" class="part"/>')
        else:
            my = (y0 + y1) / 2
            o.append(f'<rect x="{x0 - 6}" y="{my - 22}" width="12" height="44" rx="3" class="part"/>')
        o.append(T(X(lx), Y(ly) + 3, label, "tl", anchor))

    # D1 mini
    o.append(f'<rect x="{X(0.6)}" y="{Y(3.46)}" width="{13.5 * S}" height="{10.08 * S}" rx="5" class="mod"/>')
    o.append(T(X(10.5), Y(9.6), "D1 mini auf Buchsenleisten", "tm"))
    o.append(T(X(10.5), Y(10.3), "(Modul liegt über R3/R4)", "ts"))
    o.append(T(X(1.0), Y(11) + 3, "◂ USB", "ts", "start"))
    o.append(T(X(13.9), Y(8.5) + 3, "Antenne", "ts", "end"))
    for row in (4, 13):
        o.append(f'<rect x="{X(3) - 9}" y="{Y(row) - 9}" width="{7 * S + 18}" height="18" rx="3" class="part"/>')
    for i, n in enumerate(TOP_HDR):
        o.append(T(X(3 + i), Y(4) + 21, n, "ts"))
    for i, n in enumerate(BOT_HDR):
        o.append(T(X(3 + i), Y(13) - 14, n, "ts"))
    # J1
    o.append(f'<rect x="{X(1) - 9}" y="{Y(17) - 9}" width="{4 * S + 18}" height="18" rx="3" class="part"/>')
    for i, (n, _) in enumerate(J1):
        o.append(T(X(1 + i), Y(17) - 14, n, "ts"))
    o.append(T(X(6.0), Y(16.2), "J1 → TF-Luna", "tl", "start"))
    # J2
    o.append(f'<rect x="{X(16)}" y="{Y(1.15)}" width="{4 * S}" height="{1.6 * S}" rx="3" class="part"/>')
    o.append(T(X(17), Y(1.5) + 2, "COM", "ts"))
    o.append(T(X(19), Y(1.5) + 2, "NO", "ts"))
    o.append(T(X(20.3), Y(1.7) + 3, "J2 → Antrieb (Impuls)", "tl", "start"))
    # K1
    o.append(f'<rect x="{X(18.44)}" y="{Y(4.45)}" width="{4.12 * S}" height="{6.1 * S}" rx="4" class="part"/>')
    o.append(T(X(20.5), Y(8) + 3, "K1", "tm"))
    o.append(T(X(20.5), Y(8.7) + 3, "HK4100F", "ts"))
    for c, r, lab, a in ((19, 5, "A", "start"), (22, 5, "B", "end"), (19, 6, "Spule", "start"),
                         (22, 6, "Spule", "end"), (19, 10, "COM", "start"), (22, 10, "COM", "end")):
        dx = 8 if a == "start" else -8
        o.append(T(X(c) + dx, Y(r) + 3, lab, "ts", a))
    # Q1: flache Seite zeigt nach oben (zum Relais)
    cx, cy = X(19), Y(12)
    o.append(f'<path d="M {cx - 30} {cy - 9} L {cx + 30} {cy - 9} L {cx + 30} {cy - 2} A 30 16 0 0 1 {cx - 30} {cy - 2} Z" class="part"/>')
    o.append(T(X(18) - 2, Y(12) - 13, "E", "ts"))
    o.append(T(X(19), Y(12) - 13, "B", "ts"))
    o.append(T(X(20) + 2, Y(12) - 13, "C", "ts"))
    o.append(T(X(17.3), Y(12) + 3, "Q1", "tl", "end"))
    # Widerstände
    res((15, 14), (19, 14), "R1 1 kΩ", 17, 14.75, "middle")
    res((11, 14), (11, 17), "R2 10 kΩ", 11.45, 15.5)
    res((1, 8), (6, 8), "R3 4,7 kΩ", 6.45, 8)
    res((2, 7), (6, 7), "R4 4,7 kΩ", 6.45, 7)
    # Diode
    o.append(f'<line x1="{X(21)}" y1="{Y(12)}" x2="{X(24)}" y2="{Y(12)}" class="lead"/>')
    o.append(f'<rect x="{X(22.5) - 17}" y="{Y(12) - 6}" width="34" height="12" rx="3" class="part"/>')
    o.append(f'<rect x="{X(22.5) + 9}" y="{Y(12) - 6}" width="5" height="12" class="ring"/>')
    o.append(T(X(22.5), Y(12.75) + 3, "D 1N4148 (Ring → 5 V)", "tl"))
    # C1
    o.append(f'<circle cx="{X(21)}" cy="{Y(17.5)}" r="{0.95 * S}" class="part"/>')
    o.append(T(X(22.15), Y(17.2) + 3, "C1 100 µF", "tl", "start"))
    o.append(T(X(22.15), Y(17.85) + 3, "+ an Reihe 18", "ts", "start"))
    # Pins
    for (c, r), net in PINS.items():
        cls = f"pin n-{net}" if net else "pin n-free"
        o.append(f'<circle cx="{X(c)}" cy="{Y(r)}" r="4.2" class="{cls}"/>')
    return "\n".join(o)


def schematic():
    o = []

    def W(pts, net):
        o.append(f'<polyline points="{" ".join(f"{x},{y}" for x, y in pts)}" class="tr n-{net}"/>')

    def dot(x, y, net):
        o.append(f'<circle cx="{x}" cy="{y}" r="4" class="jd n-{net}"/>')

    def rv(x, y0, y1):
        o.append(f'<rect x="{x - 7}" y="{y0}" width="14" height="{y1 - y0}" class="sym"/>')

    # Blöcke
    o.append('<rect x="40" y="110" width="130" height="300" rx="4" class="blk"/>')
    o.append(T(40, 100, "TF-Luna (Kabel an J1)", "tm", "start"))
    for y, lab in ((170, "1  +5V"), (220, "2  SDA"), (260, "3  SCL"), (330, "4  GND"), (365, "5  CFG"), (395, "6  frei")):
        o.append(T(162, y + 4, lab, "t", "end"))
    o.append('<rect x="380" y="110" width="160" height="300" rx="4" class="blk"/>')
    o.append(T(380, 100, "D1 mini (ESP8266)", "tm", "start"))
    for y, lab in ((150, "3V3"), (220, "D5  GPIO14"), (260, "D6  GPIO12")):
        o.append(T(388, y + 4, lab, "t", "start"))
    for y, lab in ((150, "5V"), (290, "GPIO5  D1"), (370, "GND")):
        o.append(T(532, y + 4, lab, "t", "end"))
    # I2C + Pull-ups
    W([(170, 220), (380, 220)], "SDA")
    W([(170, 260), (380, 260)], "SCL")
    o.append(T(215, 213, "SDA", "tl", "start"))
    o.append(T(215, 253, "SCL", "tl", "start"))
    W([(380, 150), (290, 150)], "3V3")
    W([(330, 150), (330, 220)], "3V3")
    W([(290, 150), (290, 260)], "3V3")
    rv(330, 165, 199)
    rv(290, 165, 199)
    dot(330, 150, "3V3"); dot(330, 220, "SDA"); dot(290, 260, "SCL")
    o.append(T(342, 186, "R3 4,7 kΩ", "tl", "start"))
    o.append(T(279, 186, "R4 4,7 kΩ", "tl", "end"))
    # Versorgung
    W([(540, 150), (580, 150), (580, 60)], "5V")
    W([(170, 170), (205, 170), (205, 60), (955, 60)], "5V")
    dot(580, 60, "5V")
    o.append(T(592, 50, "+5 V (vom USB-Netzteil über den D1 mini)", "tl", "start"))
    W([(170, 330), (205, 330), (205, 460), (955, 460)], "GND")
    W([(170, 365), (205, 365)], "GND")
    dot(205, 365, "GND")
    W([(540, 370), (565, 370), (565, 460)], "GND")
    dot(565, 460, "GND")
    o.append(T(592, 480, "GND", "tl", "start"))
    o.append(T(215, 385, "Pin 5 an GND = I2C-Modus", "ts", "start"))
    # Treiberstufe
    W([(540, 290), (640, 290)], "SIG")
    W([(610, 290), (610, 460)], "SIG")
    rv(610, 350, 390)
    dot(610, 290, "SIG"); dot(610, 460, "GND")
    o.append(T(622, 374, "R2 10 kΩ", "tl", "start"))
    o.append('<rect x="640" y="283" width="50" height="14" class="sym"/>')
    o.append(T(665, 275, "R1 1 kΩ", "tl"))
    W([(690, 290), (742, 290)], "BASE")
    o.append('<circle cx="754" cy="290" r="31" class="symo"/>')
    o.append('<line x1="742" y1="268" x2="742" y2="312" class="symb"/>')
    W([(742, 280), (770, 262), (770, 180)], "COIL")
    W([(742, 300), (770, 318), (770, 460)], "GND")
    o.append('<polygon points="770,318 757,316 763,305" class="arr"/>')
    dot(770, 460, "GND")
    o.append(T(792, 294, "Q1 BC547", "tl", "start"))
    # Spule + Freilaufdiode
    W([(770, 60), (770, 120)], "5V")
    dot(770, 60, "5V")
    o.append('<rect x="755" y="120" width="30" height="60" class="sym"/>')
    o.append(T(770, 154, "K1", "ts"))
    W([(770, 100), (700, 100), (700, 138)], "5V")
    W([(700, 160), (700, 205), (770, 205)], "COIL")
    dot(770, 100, "5V"); dot(770, 205, "COIL")
    o.append('<polygon points="688,160 712,160 700,138" class="arr"/>')
    o.append('<line x1="687" y1="138" x2="713" y2="138" class="symb"/>')
    o.append(T(682, 153, "D 1N4148", "tl", "end"))
    # Kontakt
    o.append('<line x1="785" y1="150" x2="826" y2="150" class="dash"/>')
    W([(900, 135), (852, 135)], "NO")
    W([(900, 175), (822, 175)], "COM")
    W([(822, 175), (846, 143)], "COM")
    o.append('<circle cx="852" cy="135" r="3.5" class="jd n-NO"/>')
    o.append('<circle cx="822" cy="175" r="3.5" class="jd n-COM"/>')
    o.append('<rect x="900" y="112" width="40" height="86" rx="4" class="blk"/>')
    o.append(T(920, 139, "NO", "ts"))
    o.append(T(920, 179, "COM", "ts"))
    o.append(T(940, 102, "J2 → Impulseingang Antrieb", "tm", "end"))
    # C1
    W([(955, 60), (955, 250)], "5V")
    W([(955, 262), (955, 460)], "GND")
    o.append('<line x1="940" y1="250" x2="970" y2="250" class="symb"/>')
    o.append('<line x1="940" y1="262" x2="970" y2="262" class="symb"/>')
    o.append(T(945, 240, "+", "tl", "end"))
    o.append(T(935, 290, "C1 100 µF", "tl", "end"))
    return "\n".join(o)


svg_top = f'<svg viewBox="0 0 {BW} {BH}" role="img" aria-label="Lochrasterplatine von der Bestückungsseite: Lage aller Bauteile im Raster 24 mal 18">\n{board(False)}\n</svg>'
svg_bot = f'<svg viewBox="0 0 {BW} {BH}" role="img" aria-label="Lochrasterplatine von der Lötseite, gespiegelt: alle Leiterzüge und Lötstellen">\n{board(True)}\n</svg>'
svg_sch = f'<svg viewBox="0 0 990 500" role="img" aria-label="Schaltplan: D1 mini mit TF-Luna über I2C und Relais-Treiberstufe mit BC547">\n{schematic()}\n</svg>'
for s in (svg_top, svg_bot, svg_sch):
    ET.fromstring(s)


# =====================================================================
# Streifenraster-Variante: Streifen waagerecht (Reihe = Streifen)
# =====================================================================
NETCOL = {  # hell, dunkel
    "5V": ("#c62828", "#ff7b72"), "GND": ("#1f4fa3", "#79a8ff"), "3V3": ("#c96a00", "#ffb054"),
    "SDA": ("#1a7f37", "#56d364"), "SCL": ("#7b3fbf", "#c297ff"), "SIG": ("#8f6c00", "#e3c341"),
    "BASE": ("#8a5a44", "#d9a68c"), "COIL": ("#b0307a", "#ff8ac6"), "COM": ("#00727a", "#4fd1d9"),
    "NO": ("#566500", "#b5cc40"),
}
SC, SR = 19, 15
CUTS = [(5, 1), (5, 3), (5, 5), (5, 8), (14, 10), (14, 11)]
LINKS = [("L1", (9, 8), (9, 11)), ("L2", (8, 7), (8, 13)), ("L3", (18, 10), (18, 14))]
HL, HR = 2, 11
L_HDR = ["RST", "A0", "D0", "D5", "D6", "D7", "D8", "3V3"]
R_HDR = ["TX", "RX", "D1", "D2", "D3", "D4", "GND", "5V"]
S_HDR_NET = {"RST": "RST", "A0": "A0RX", "D0": "D0", "D5": "SDA", "D6": "SCL", "D7": "D7D4", "D8": "GND",
             "3V3": "3V3", "TX": "TX", "RX": "A0RX", "D1": "SIG", "D2": "SDA", "D3": "D3", "D4": "D7D4",
             "GND": "GND", "5V": "5V"}
SP = {}
for i, n in enumerate(L_HDR):
    SP[(HL, 1 + i)] = S_HDR_NET[n]
for i, n in enumerate(R_HDR):
    SP[(HR, 1 + i)] = S_HDR_NET[n]
SP.update({
    (1, 4): "SDA", (1, 5): "SCL", (1, 7): "GND", (1, 11): "5V", (1, 13): "GND",  # J1
    (3, 4): "SDA", (3, 8): "3V3", (4, 5): "SCL", (4, 8): "3V3",                  # R3, R4
    (6, 3): "SIG", (6, 7): "GND", (7, 3): "SIG", (7, 12): "BASE",                # R2, R1
    (15, 7): "GND", (15, 8): "5V",                                               # C1
    (13, 10): "NC", (16, 10): "NO", (13, 11): "5V", (16, 11): "COIL",            # K1
    (13, 15): "COM", (16, 15): "COM",
    (19, 11): "COIL", (19, 12): "BASE", (19, 13): "GND",                         # Q1 C, B, E
    (17, 8): "5V", (17, 11): "COIL",                                             # Diode K, A
    (1, 14): "NO", (1, 15): "COM",                                               # J2
    (9, 8): "5V", (9, 11): "5V", (8, 7): "GND", (8, 13): "GND",                  # Brücken
    (18, 10): "NO", (18, 14): "NO",
})
assert len(set(SP)) == len(SP)


def seg(c, r):
    assert (c, r) not in CUTS, f"Pin auf Trennstelle {(c, r)}"
    return (r, sum(1 for cc, rr in CUTS if rr == r and cc < c))


parent = {}


def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


for _, a, b in LINKS:
    parent[find(seg(*a))] = find(seg(*b))
grp_net, net_grp = {}, {}
for p, net in SP.items():
    assert 1 <= p[0] <= SC and 1 <= p[1] <= SR, p
    g = find(seg(*p))
    assert grp_net.setdefault(g, net) == net, f"Kurzschluss {p}: {grp_net[g]} / {net}"
    assert net_grp.setdefault(net, g) == g, f"Netz {net} nicht zusammenhängend bei {p}"
print("Streifenraster ok:", len(SP), "Pins,", len(CUTS), "Trennstellen,", len(LINKS), "Brücken")
seg_net = {seg(*p): n for p, n in SP.items()}

S2, MX2, MY2 = 30, 70, 34
SW, SH = MX2 + (SC - 1) * S2 + 46, MY2 + (SR - 1) * S2 + 36


def stripboard(mirror):
    def X(c):
        return MX2 + ((SC - c) if mirror else (c - 1)) * S2

    def Y(r):
        return MY2 + (r - 1) * S2

    o = []
    o.append(f'<rect x="{MX2 - 20}" y="{MY2 - 20}" width="{(SC - 1) * S2 + 40}" height="{(SR - 1) * S2 + 40}" rx="5" class="brd"/>')
    for c in range(1, SC + 1):
        o.append(T(X(c), MY2 - 24, str(c), "ax"))
    for r in range(1, SR + 1):
        o.append(T(MX2 + (SC - 1) * S2 + 26, Y(r) + 3, str(r), "ax", "start"))
    for r in range(1, SR + 1):
        cuts = sorted(c for c, rr in CUTS if rr == r)
        bounds = [0] + cuts + [SC + 1]
        for i, (a, b) in enumerate(zip(bounds, bounds[1:])):
            a, b = a + 1, b - 1
            net = seg_net.get((r, i))
            cls = f"sg n-{net}" if net in NETCOL else "sg n-none"
            xa, xb = sorted((X(a), X(b)))
            o.append(f'<rect x="{xa - S2 / 2 + 2}" y="{Y(r) - 9}" width="{xb - xa + S2 - 4}" height="18" rx="2" class="{cls}{" solid" if mirror else ""}"/>')
    for c in range(1, SC + 1):
        for r in range(1, SR + 1):
            o.append(f'<circle cx="{X(c)}" cy="{Y(r)}" r="2.6" class="pad"/>')
    for c, r in CUTS:
        x, y = X(c), Y(r)
        o.append(f'<circle cx="{x}" cy="{y}" r="9" class="cutc"/>')
        o.append(f'<path d="M {x - 5} {y - 5} L {x + 5} {y + 5} M {x - 5} {y + 5} L {x + 5} {y - 5}" class="cutx"/>')

    if mirror:
        for p in SP:
            o.append(f'<circle cx="{X(p[0])}" cy="{Y(p[1])}" r="5" class="jt n-free"/>')
        for i, n in enumerate(L_HDR):
            o.append(T(X(HL) - 11, Y(1 + i) + 3, n, "ts", "end"))
        for i, n in enumerate(R_HDR):
            o.append(T(X(HR) + 11, Y(1 + i) + 3, n, "ts", "start"))
        o.append(T(X(14.5), Y(12.5) + 3, "K1", "tm"))
        o.append(T(X(19) + 11, Y(12) - 9, "Q1", "ts", "start"))
        return "\n".join(o)

    def vres(c, r0, r1, label, ly):
        o.append(f'<line x1="{X(c)}" y1="{Y(r0)}" x2="{X(c)}" y2="{Y(r1)}" class="lead"/>')
        my = (Y(r0) + Y(r1)) / 2
        o.append(f'<rect x="{X(c) - 6.5}" y="{my - 24}" width="13" height="48" rx="3" class="part2"/>')
        o.append(T(X(c), Y(ly) + 3, label, "tl"))

    # D1 mini
    o.append(f'<rect x="{X(HL - 0.63)}" y="{MY2 - 20}" width="{10.26 * S2}" height="{Y(10.4) - MY2 + 20}" rx="5" class="mod"/>')
    o.append(T(X(8.3), Y(1.25) + 3, "D1 mini", "tm"))
    o.append(T(X(4.6), Y(9.9) + 3, "USB ▾", "ts"))
    for col in (HL, HR):
        o.append(f'<rect x="{X(col) - 9}" y="{Y(1) - 9}" width="18" height="{7 * S2 + 18}" rx="3" class="part"/>')
    for i, n in enumerate(L_HDR):
        o.append(T(X(HL) - 12, Y(1 + i) + 3, n, "ts", "end"))
    for i, n in enumerate(R_HDR):
        o.append(T(X(HR) - 13, Y(1 + i) + 3, n, "ts", "end"))
    # J1
    for r, lab in ((4, "SDA"), (5, "SCL"), (7, "GND"), (11, "5V"), (13, "CFG"), (14, "J2 NO"), (15, "J2 COM")):
        o.append(T(X(1) - 13, Y(r) + 3, lab, "tl", "end"))
    o.append(T(X(1) - 13, Y(2.6) + 3, "J1", "tm", "end"))
    vres(3, 4, 8, "R3", 3.3)
    vres(4, 5, 8, "R4", 4.3)
    vres(6, 3, 7, "R2", 2.3)
    vres(7, 3, 12, "R1", 2.3)
    for name, (c, r0), (_, r1) in LINKS:
        o.append(f'<line x1="{X(c)}" y1="{Y(r0)}" x2="{X(c)}" y2="{Y(r1)}" class="lnk"/>')
        o.append(T(X(c) + 6, Y(r1 + 0.8) + 3, name, "tl", "end" if name == "L2" else "start"))
    # C1
    o.append(f'<circle cx="{X(15)}" cy="{Y(7.5)}" r="{1.05 * S2}" class="part2"/>')
    o.append(T(X(16.25), Y(7.5) + 3, "C1", "tl", "start"))
    o.append(T(X(15) + 15, Y(8) + 14, "+", "tl"))
    # K1
    o.append(f'<rect x="{X(12.44)}" y="{Y(9.45)}" width="{4.12 * S2}" height="{6.1 * S2}" rx="4" class="part"/>')
    o.append(T(X(14.5), Y(12.7) + 3, "K1", "tm"))
    o.append(T(X(14.5), Y(13.35) + 3, "HK4100F", "ts"))
    o.append(T(X(13) + 10, Y(10) + 3, "NC", "ts", "start"))
    o.append(T(X(16) - 10, Y(10) + 3, "NO", "ts", "end"))
    o.append(T(X(14.5), Y(15) + 3, "COM", "ts"))
    # Q1: flache Seite zeigt nach links zum Relais
    cx, cy = X(19), Y(12)
    o.append(f'<path d="M {cx - 10} {cy - 37} L {cx - 10} {cy + 37} L {cx - 2} {cy + 37} A 17 37 0 0 0 {cx - 2} {cy - 37} Z" class="part2"/>')
    for r, lab in ((11, "C"), (12, "B"), (13, "E")):
        o.append(T(X(19) - 13, Y(r) + 3, lab, "ts", "end"))
    o.append(T(X(19), Y(14.05) + 3, "Q1", "tl"))
    # Diode
    o.append(f'<line x1="{X(17)}" y1="{Y(8)}" x2="{X(17)}" y2="{Y(11)}" class="lead"/>')
    o.append(f'<rect x="{X(17) - 6.5}" y="{Y(9.5) - 17}" width="13" height="34" rx="2" class="part2"/>')
    o.append(f'<rect x="{X(17) - 6.5}" y="{Y(9.5) - 17}" width="13" height="5" class="ring"/>')
    o.append(T(X(17), Y(7.15) + 3, "D", "tl"))
    for p, net in SP.items():
        cls = f"pin n-{net}" if net in NETCOL else "pin n-free"
        o.append(f'<circle cx="{X(p[0])}" cy="{Y(p[1])}" r="4.4" class="{cls}"/>')
    return "\n".join(o)


svg_stop = f'<svg viewBox="0 0 {SW} {SH}" role="img" aria-label="Streifenrasterplatine, 19 Löcher breit und 15 Streifen hoch, von der Bestückungsseite mit sechs Trennstellen und drei Drahtbrücken">\n{stripboard(False)}\n</svg>'
svg_sbot = f'<svg viewBox="0 0 {SW} {SH}" role="img" aria-label="Streifenrasterplatine von der Kupferseite, gespiegelt, mit den fünf Trennstellen">\n{stripboard(True)}\n</svg>'
for s in (svg_stop, svg_sbot):
    ET.fromstring(s)


def path_txt(poly):
    return " → ".join(f"S{c}/R{r}" for c, r in poly)


rows_html = ""
for net, polys in NETS.items():
    paths = "<br>".join(path_txt(p) for p in polys)
    rows_html += f'<tr><td><span class="sw n-{net}"></span>{esc(NET_LABEL[net])}</td><td class="mono">{paths}</td></tr>\n'

light = "".join(f"--n-{k}:{v[0]};" for k, v in NETCOL.items())
dark = "".join(f"--n-{k}:{v[1]};" for k, v in NETCOL.items())
netcss = "".join(
    f".tr.n-{k},.jd.n-{k}{{stroke:var(--n-{k})}}.jd.n-{k},.pin.n-{k},.jt.n-{k},.sw.n-{k}{{fill:var(--n-{k});background:var(--n-{k})}}"
    for k in NETCOL)
netcss += "".join(f"svg .sg.n-{k}{{fill:var(--n-{k})}}" for k in NETCOL)
netcss += ("svg .sg{opacity:.32}svg .sg.solid{opacity:.8}svg .sg.n-none{fill:var(--pad)}svg .sg.n-none.solid{opacity:.45}"
           "svg .cutc{fill:var(--surface);stroke:var(--fg);stroke-width:1.4}svg .cutx{stroke:var(--fg);stroke-width:1.8;fill:none}"
           "svg .lnk{stroke:var(--fg);stroke-width:3;stroke-linecap:round}svg .part2{fill:var(--surface);stroke:var(--fg);stroke-width:1.2}")
DARK =f"--bg:#141a16;--surface:#1c241e;--fg:#e6ece6;--muted:#9aa89c;--line:#34413a;--board:#22301f;--pad:#5d6f60;--part:#e6ece61f;--warn:#ffb054;{dark}color-scheme:dark"

html = f"""<title>Garagentor-Sensorplatine</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
/* Layout: eine Lesespalte, Zeichnungen in voller Breite der Spalte, jede in eigenem Scroll-Container */
:root {{--bg:#f2f4ef;--surface:#ffffff;--fg:#1b211c;--muted:#5a655c;--line:#cdd5cc;--board:#e4ead9;--pad:#93a394;--part:#1b211c14;--warn:#a65a00;{light}
  --sans:"IBM Plex Sans",system-ui,sans-serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{{DARK}}} }}
:root[data-theme="dark"] {{{DARK}}}
body {{background:var(--bg);color:var(--fg);font-family:var(--sans);font-size:16px;line-height:1.55}}
main {{max-width:1000px;margin:0 auto;padding-block:32px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:flex;flex-direction:column;gap:36px}}
section {{display:flex;flex-direction:column;gap:14px;min-width:0}}
h1 {{font-size:30px;line-height:1.15;margin:0;font-weight:600;text-wrap:balance}}
h2 {{font-size:20px;margin:0;font-weight:600;text-wrap:balance}}
p, ul, ol {{margin:0;max-width:68ch}}
ul, ol {{padding-left:1.3em;display:flex;flex-direction:column;gap:6px}}
.lead-p {{color:var(--muted);font-size:17px}}
figure {{margin:0;display:flex;flex-direction:column;gap:8px}}
.scroll {{overflow-x:auto;background:var(--surface);border:1px solid var(--line);border-radius:8px}}
.scroll svg {{display:block;width:100%;min-width:680px;height:auto}}
figcaption {{color:var(--muted);font-size:14px;max-width:75ch}}
table {{border-collapse:collapse;width:100%;font-size:14.5px}}
th, td {{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
th {{font-weight:600;font-size:12.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}}
.mono, code {{font-family:var(--mono);font-size:13.5px}}
.sw {{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:8px}}
.note {{border-left:3px solid var(--warn);padding:2px 0 2px 14px}}
.note strong {{color:var(--warn)}}
svg text {{font-family:var(--mono);fill:var(--fg)}}
svg .t {{font-size:12px}} svg .tl {{font-size:11.5px}} svg .ts {{font-size:9.5px;fill:var(--muted)}}
svg .tm {{font-size:12.5px;font-weight:500}} svg .ax {{font-size:8.5px;fill:var(--muted)}} svg .tb {{font-size:11px;font-weight:500}}
svg .brd {{fill:var(--board);stroke:var(--line)}} svg .pad {{fill:var(--surface);stroke:var(--pad);stroke-width:1}}
svg .tr {{fill:none;stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round}} svg .tr.faint {{opacity:.3}}
svg .brg {{stroke:var(--fg);stroke-width:3;stroke-dasharray:3 3;fill:none}}
svg .part {{fill:var(--part);stroke:var(--fg);stroke-width:1.2}} svg .ring {{fill:var(--fg)}}
svg .mod {{fill:none;stroke:var(--muted);stroke-width:1.2;stroke-dasharray:6 4}}
svg .lead {{stroke:var(--fg);stroke-width:1.4}} svg .pin {{stroke:var(--surface);stroke-width:1.2}}
svg .jt {{stroke:var(--fg);stroke-width:1.3}} svg .n-free {{fill:var(--surface);stroke:var(--fg)}}
svg .blk {{fill:var(--part);stroke:var(--fg);stroke-width:1.3}} svg .sym {{fill:var(--surface);stroke:var(--fg);stroke-width:1.5}}
svg .symo {{fill:none;stroke:var(--muted);stroke-width:1}} svg .symb {{stroke:var(--fg);stroke-width:3;fill:none}}
svg .arr {{fill:var(--fg)}} svg .dash {{stroke:var(--muted);stroke-width:1.2;stroke-dasharray:4 4}} svg .jd {{stroke-width:0}}
{netcss}
</style>
<main>
<header style="display:flex;flex-direction:column;gap:10px">
  <h1>Garagentor-Sensorplatine</h1>
  <p class="lead-p">D1 mini, TF-Luna über I2C und ein HK4100F-Relais für den Impulseingang des Normstahl Magic 600, aufgebaut auf einer Lochrasterplatine 5 × 7 cm (24 × 18 Lötaugen).</p>
</header>

<section>
  <h2>Pinwahl</h2>
  <ul>
    <li><strong>Relais an D1 (GPIO5).</strong> GPIO4 und GPIO5 sind beim ESP8266 die einzigen Pins, die nach einem Reset hochohmig bleiben. D5 bis D7 haben dann einen schwachen Pull-up und könnten das Relais beim Booten kurz anziehen lassen, das Tor würde also fahren.</li>
    <li><strong>I2C an D5 (SDA) und D6 (SCL).</strong> Der ESP8266 macht I2C in Software, die Pins sind frei wählbar. Der Pull-up nach dem Reset stört bei I2C nicht.</li>
    <li><strong>R2 zieht den Relais-Eingang zusätzlich auf GND</strong>, damit der Transistor auch bei offenem Pin sicher sperrt.</li>
  </ul>
</section>

<section>
  <h2>Schaltplan</h2>
  <figure>
    <div class="scroll">{svg_sch}</div>
    <figcaption>Der TF-Luna hängt mit 5 V Versorgung und 3,3-V-Datenleitungen am I2C-Bus. GPIO5 schaltet über Q1 die Relaisspule, der Schließerkontakt geht potentialfrei an den Impulseingang. Linien, die sich ohne Punkt kreuzen, sind nicht verbunden.</figcaption>
  </figure>
</section>

<section>
  <h2>Stückliste</h2>
  <div style="overflow-x:auto"><table>
    <tr><th>Teil</th><th>Wert</th><th>Hinweis</th></tr>
    <tr><td>Platine</td><td>Lochraster 5 × 7 cm, 2,54 mm</td><td>24 × 18 Lötaugen, einzelne Lötpunkte (kein Streifenraster)</td></tr>
    <tr><td>U1</td><td>Wemos D1 mini</td><td>auf 2 Buchsenleisten 1 × 8, weil R3 und R4 darunter liegen</td></tr>
    <tr><td>K1</td><td>HK4100F-DC5V-SHG</td><td>Spule 125 Ω, etwa 40 mA</td></tr>
    <tr><td>Q1</td><td>BC547</td><td>Pinfolge von der flachen Seite gesehen: C, B, E</td></tr>
    <tr><td>D</td><td>1N4148 oder 1N4007</td><td>Freilaufdiode, Ring zeigt zu +5 V</td></tr>
    <tr><td>R1</td><td>1 kΩ</td><td>Basiswiderstand</td></tr>
    <tr><td>R2</td><td>10 kΩ</td><td>Pull-down am Relais-Signal</td></tr>
    <tr><td>R3, R4</td><td>4,7 kΩ</td><td>I2C-Pull-ups nach 3,3 V</td></tr>
    <tr><td>C1</td><td>100 µF, mindestens 10 V</td><td>Elko, puffert die Stromspitzen von Sensor und Relais</td></tr>
    <tr><td>J1</td><td>Stiftleiste 1 × 5</td><td>oder das Sensorkabel direkt einlöten</td></tr>
    <tr><td>J2</td><td>Schraubklemme 2-polig, 5,08 mm</td><td>zum Impulseingang des Antriebs</td></tr>
  </table></div>
</section>

<section>
  <h2>Vor dem Löten prüfen</h2>
  <p class="note"><strong>Relais ausmessen.</strong> Laut Datenblatt liegen die beiden Spulenpins in der Mitte, die beiden COM-Pins am entfernten Ende und Öffner/Schließer am Ende neben der Spule. Nach einer vom Händler beschrifteten Fassung der Datenblattzeichnung ist Pin B (Spalte 22) der Schließer (NO) und Pin A der Öffner (NC). Miss das trotzdem einmal nach.</p>
  <ol>
    <li><strong>Spule:</strong> Zwischen den beiden Pins in Reihe 6 müssen etwa 125 Ω liegen.</li>
    <li><strong>COM:</strong> Die beiden Pins in Reihe 10 haben untereinander Durchgang.</li>
    <li><strong>NO finden:</strong> In Ruhe hat COM Durchgang zu genau einem der Pins A oder B, das ist der Öffner (NC). Der andere ist NO. Er bekommt die Lötbrücke zur Reihe 4: Variante A an Spalte 19, Variante B an Spalte 22. Zu erwarten ist Variante B. Nur eine der beiden Brücken setzen.</li>
    <li><strong>D1 mini:</strong> Die Beschriftung auf dem Modul gilt. Der Pin 5V muss auf Spalte 3 / Reihe 13 sitzen, 3V3 auf Spalte 3 / Reihe 4.</li>
    <li><strong>TF-Luna:</strong> Die Adern nach Pinnummer am Sensor zuordnen, nicht nach Farbe. Wo Pin 1 sitzt, steht im Handbuch des Sensors.</li>
  </ol>
</section>

<section>
  <h2>Bestückungsseite</h2>
  <figure>
    <div class="scroll">{svg_top}</div>
    <figcaption>Blick von oben auf die Bauteile, USB-Buchse des D1 mini zeigt nach links über den Platinenrand. Die Leiterzüge der Unterseite scheinen blass durch. Die gestrichelten Brücken A und B über den Relaiskontakten sind die beiden NO-Varianten. Die Umrisse von Modul und Antenne sind geschätzt, bitte vor dem Löten mit aufgelegtem Modul prüfen.</figcaption>
  </figure>
</section>

<section>
  <h2>Lötseite</h2>
  <figure>
    <div class="scroll">{svg_bot}</div>
    <figcaption>Blick von unten, also seitenverkehrt: Spalte 24 liegt links. Jede farbige Linie ist ein Leiterzug aus blankem Draht oder durchgezogenem Lötzinn. Benachbarte Linien verschiedener Farbe dürfen sich nicht berühren. Kreise mit Rand sind Bauteil-Pins.</figcaption>
  </figure>
</section>

<section>
  <h2>Leiterzüge</h2>
  <p>S = Spalte, R = Reihe, gezählt auf der Bestückungsseite von links oben. Jeder Zug verläuft gerade von Punkt zu Punkt.</p>
  <div style="overflow-x:auto"><table>
    <tr><th>Netz</th><th>Verlauf</th></tr>
    {rows_html}
    <tr><td>Lötbrücke NO</td><td class="mono">S19/R4 → S19/R5 (Variante A) oder S22/R4 → S22/R5 (Variante B)</td></tr>
  </table></div>
</section>

<section>
  <h2>Sensorkabel an J1</h2>
  <div style="overflow-x:auto"><table>
    <tr><th>TF-Luna</th><th>Funktion</th><th>J1</th></tr>
    <tr><td>Pin 1</td><td>+5 V</td><td class="mono">S3/R17 (5V)</td></tr>
    <tr><td>Pin 2</td><td>SDA</td><td class="mono">S1/R17 (SDA)</td></tr>
    <tr><td>Pin 3</td><td>SCL</td><td class="mono">S2/R17 (SCL)</td></tr>
    <tr><td>Pin 4</td><td>GND</td><td class="mono">S4/R17 (GND)</td></tr>
    <tr><td>Pin 5</td><td>Konfiguration, an GND für I2C</td><td class="mono">S5/R17 (CFG)</td></tr>
    <tr><td>Pin 6</td><td>nicht benutzt</td><td>Ader isolieren</td></tr>
  </table></div>
  <p>Pin 5 muss schon beim Einschalten auf GND liegen, sonst startet der Sensor im UART-Modus.</p>
</section>

<section>
  <h2>Reihenfolge</h2>
  <ol>
    <li>R3 und R4 einlöten, danach R1, R2 und die Diode.</li>
    <li>Buchsenleisten für den D1 mini, J1 und J2 setzen. Die Buchsenleisten beim Löten mit aufgestecktem Modul ausrichten.</li>
    <li>Q1 mit der flachen Seite zum Relais einsetzen, dann C1 (Plus an Reihe 18) und K1.</li>
    <li>Leiterzüge nach der Tabelle ziehen, zuerst die langen Züge für 5 V und GND.</li>
    <li>Die eine passende NO-Lötbrücke setzen.</li>
    <li>Ohne Modul und ohne Sensor mit dem Durchgangsprüfer messen: kein Durchgang zwischen 5 V und GND, zwischen 3,3 V und GND und zwischen den beiden J2-Klemmen.</li>
    <li>Modul aufstecken, per USB versorgen und an J1 die 5 V nachmessen. Erst dann den Sensor anschließen, und J2 erst nach einem Relaistest mit dem Antrieb verbinden.</li>
  </ol>
</section>

<section>
  <h2>Variante auf Streifenraster</h2>
  <p>Gleiche Schaltung, gleiche Pins, gleiche Bauteile, ausgelegt für deine Platinen mit 37 Streifen zu je 19 Löchern. Der Aufbau belegt die volle Streifenlänge von 19 Löchern und 15 der 37 Streifen (etwa 48 × 38 mm). Er kommt mit <strong>6 Trennstellen und 3 Drahtbrücken</strong> aus und ist so gebaut und mit dem Relaistest geprüft. Jede Trennstelle sitzt auf einem freien Loch und wird dort mit einem 3-mm-Bohrer von Hand aufgebohrt.</p>
  <ul>
    <li><strong>Alle hohen Teile stehen neben dem D1 mini.</strong> Relais, Elko und Transistor liegen rechts außerhalb der Modulfläche und weit weg vom USB-Stecker. Unter dem Modul und unter dem Stecker liegen nur die vier Widerstände und zwei der drei Drahtbrücken.</li>
    <li><strong>Der D1 mini steht quer zu den Streifen.</strong> Jeder Streifen verbindet dadurch einen linken mit einem rechten Modulpin. Vier dieser Paare müssen getrennt werden, die anderen vier dürfen verbunden bleiben: D5 mit D2 (D2 bleibt unbenutzt), D8 mit GND (GPIO15 muss beim Booten ohnehin auf GND liegen), A0 mit RX und D7 mit D4.</li>
    <li><strong>Die Relaiskontakte sind durch eine Trennstelle getrennt.</strong> Die beiden Kontaktpins sitzen auf Streifen 10. Die Trennstelle S14/R10 trennt sie; der Öffner-Pin an S13/R10 hängt damit an einem unbenutzten Streifenstück und muss nicht abgekniffen werden.</li>
    <li><strong>Alle Anschlüsse liegen in Spalte 1.</strong> Die Brücke L3 holt den Schließer von Streifen 10 auf Streifen 14. Damit liegen J2 (Streifen 14 und 15) und das Sensorkabel J1 in derselben Spalte, und eine einzige Stiftleiste genügt.</li>
    <li><strong>Die Widerstände überbrücken die Streifen selbst.</strong> R1 bis R4 stehen senkrecht zu den Streifen und ersetzen so vier Querverbindungen.</li>
    <li><strong>Platine:</strong> Streifen 1 liegt an der Platinenkante, damit die Antenne des D1 mini über den Rand ragt. Streifen 9 bleibt als Abstand frei. Hinter Streifen 16 kannst du die Platine absägen.</li>
  </ul>
  <figure>
    <div class="scroll">{svg_stop}</div>
    <figcaption>Bestückungsseite. Die Streifen der Unterseite sind blass in der Farbe ihres Netzes eingezeichnet, graue Streifen sind unbenutzt. Kreise mit Kreuz sind Trennstellen, L1 bis L3 die Drahtbrücken. Die gestrichelte Fläche ist der D1 mini; sein Umriss ist geschätzt.</figcaption>
  </figure>
  <figure>
    <div class="scroll">{svg_sbot}</div>
    <figcaption>Kupferseite, seitenverkehrt: Spalte 19 liegt links. Hier werden die sechs Trennstellen gebohrt. Kreise sind Lötstellen.</figcaption>
  </figure>
  <div style="overflow-x:auto"><table>
    <tr><th>Trennstelle</th><th>trennt</th></tr>
    <tr><td class="mono">S5/R1</td><td>RST von TX (sonst setzt jede serielle Ausgabe den ESP zurück)</td></tr>
    <tr><td class="mono">S5/R3</td><td>D0 vom Relais-Signal an D1</td></tr>
    <tr><td class="mono">S5/R5</td><td>SCL an D6 von D3 (GPIO0, Boot-Pin)</td></tr>
    <tr><td class="mono">S5/R8</td><td>3,3 V von 5 V</td></tr>
    <tr><td class="mono">S14/R10</td><td>die beiden Kontaktpins des Relais (links Öffner, rechts Schließer)</td></tr>
    <tr><td class="mono">S14/R11</td><td>die beiden Spulenpins des Relais (links 5 V, rechts Kollektor)</td></tr>
  </table></div>
  <div style="overflow-x:auto"><table>
    <tr><th>Teil</th><th>Löcher (S = Spalte, R = Streifen)</th><th>Hinweis</th></tr>
    <tr><td>Buchsenleisten U1</td><td class="mono">S2/R1–R8 und S11/R1–R8</td><td>links RST oben, 3V3 unten; rechts TX oben, 5V unten</td></tr>
    <tr><td>R3 4,7 kΩ</td><td class="mono">S3/R4 – S3/R8</td><td>unter dem Modul, SDA nach 3,3 V</td></tr>
    <tr><td>R4 4,7 kΩ</td><td class="mono">S4/R5 – S4/R8</td><td>unter dem Modul, SCL nach 3,3 V</td></tr>
    <tr><td>R2 10 kΩ</td><td class="mono">S6/R3 – S6/R7</td><td>unter dem Modul, Relais-Signal nach GND</td></tr>
    <tr><td>R1 1 kΩ</td><td class="mono">S7/R3 – S7/R12</td><td>unter Modul und USB-Stecker, Relais-Signal zur Basis</td></tr>
    <tr><td>Brücke L2 (GND)</td><td class="mono">S8/R7 – S8/R13</td><td>isolierter Draht, flach verlegen</td></tr>
    <tr><td>Brücke L1 (5 V)</td><td class="mono">S9/R8 – S9/R11</td><td>isolierter Draht, flach verlegen</td></tr>
    <tr><td>Brücke L3 (NO)</td><td class="mono">S18/R10 – S18/R14</td><td>isolierter Draht zwischen Diode und Transistor, führt den Schließer zu J2</td></tr>
    <tr><td>C1 100 µF</td><td class="mono">S15/R7 (−), S15/R8 (+)</td><td>steht rechts neben dem Modul</td></tr>
    <tr><td>K1</td><td class="mono">S13 und S16, jeweils R10, R11, R15</td><td>R10 Kontakte (NC an S13, NO an S16), R11 Spule, R15 COM</td></tr>
    <tr><td>Q1 BC547</td><td class="mono">S19/R11 (C), R12 (B), R13 (E)</td><td>am rechten Rand, flache Seite zeigt zum Relais</td></tr>
    <tr><td>Diode</td><td class="mono">S17/R8 (Ring) – S17/R11</td><td>liegend zwischen Relais und Brücke L3; überspannt das freie Loch S17/R10</td></tr>
    <tr><td>J2</td><td class="mono">S1/R14 (NO), S1/R15 (COM)</td><td>die beiden untersten Stifte der Stiftleiste, zum Impulseingang des Antriebs</td></tr>
    <tr><td>J1 Sensorkabel</td><td class="mono">S1/R11 (Pin 1, 5 V), S1/R4 (Pin 2, SDA), S1/R5 (Pin 3, SCL), S1/R7 (Pin 4, GND), S1/R13 (Pin 5, CFG)</td><td>gemeinsame Stiftleiste mit J2 in Spalte 1</td></tr>
  </table></div>
  <ul>
    <li><strong>Noch weniger Trennstellen:</strong> Wenn die Stiftleisten am D1 mini noch nicht eingelötet sind, lass die Pins RST, D0 und D3 unbestückt. Dann entfallen die Trennstellen in R1, R3 und R5, und es bleiben zwei.</li>
    <li><strong>Firmware:</strong> D8 liegt fest auf GND und D2 am SDA-Streifen. Beide Pins dürfen in ESPHome nicht als Ausgang konfiguriert werden.</li>
    <li><strong>Reihenfolge:</strong> Zuerst Trennstellen bohren, dann Widerstände und Brücken, dann die Buchsenleisten, zuletzt die hohen Teile.</li>
    <li><strong>Impulskreis:</strong> Die Streifen R14 und R15 führen über die ganze Breite das Signal des Antriebs, dazu das rechte Stück von R10. Achte beim Löten in R11 und R13 besonders auf Zinnbrücken zum Nachbarstreifen.</li>
    <li><strong>Unbenutzte Stifte:</strong> Wenn die Stiftleiste in Spalte 1 durchgehend von R4 bis R15 bestückt ist, liegen auch auf den übrigen Stiften Signale: R6 = D7/D4, R8 = 3,3 V, R10 = Öffner des Relais, R12 = Basis von Q1; R9 ist frei. Dort nichts anschließen.</li>
    <li><strong>Prüfen:</strong> Nach dem Bohren jede Trennstelle mit dem Durchgangsprüfer messen, dann wie oben 5 V gegen GND, 3,3 V gegen GND und die beiden J2-Punkte gegeneinander.</li>
  </ul>
</section>
</main>
"""
open(OUT, "w", encoding="utf-8").write(html)
print("geschrieben:", OUT, len(html), "Bytes")
