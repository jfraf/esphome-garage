// Gehäuse für die Garagentor-Sensorplatine mit TF-Luna
//
// Aufbau, von oben gesehen (y zeigt nach hinten, der Sensor blickt nach vorn):
//
//   hinten   +-------------------------------+
//            |  Kabelkerbe     USB-Schlitz   |
//            |  +-------------------------+  |
//            |  | Streifen 15             |  |
//            |  |   Platine    Spalte 1 > |  |
//            |  | Streifen 1 (Antenne)    |  |
//            |  +-------------------------+  |
//            |   Freiraum für die Antenne    |
//            |    o+-----------------+o      |
//            |     |  TF-Luna (hochkant,     |
//            |     |  Stecker nach oben)     |
//   vorn     +-----+===( O )( O )====+-------+
//
// Der TF-Luna steht mit den Linsen zur Stirnwand. Maße nach der Zeichnung im
// Datenblatt SJ-GU-TF-Luna A05: Front 35 x 21,25 mm, Tiefe 13,5 mm, der Stecker
// tritt an einer der langen Schmalseiten aus und zeigt hier nach oben.
//
// Alle Maße in mm. Die mit "MESSEN" markierten Werte sind Schätzungen und
// müssen vor dem Druck am echten Teil nachgemessen werden.

/* [Was wird gezeigt] */
// "beide" = Druckansicht, "unterteil", "deckel", "zusammenbau" = Kontrolle
teil = "beide"; // [beide, unterteil, deckel, zusammenbau]
// Platine und Sensor als durchsichtige Körper einblenden
zeige_bauteile = true;

/* [Platine] */
// Breite entlang der Streifen (19 Löcher), gemessen
platine_b = 51.0;
// Tiefe quer zu den Streifen (15 Streifen), gemessen
platine_t = 41.0;
platine_d = 1.6;
// Luft rund um die Platine
platine_spiel = 0.5;
// Platz unter der Platine für die Lötstellen
platine_abstand = 3.5;
// Höchstes Teil über der Platine: D1 mini auf Buchsenleisten, gemessen
hoehe_ueber_platine = 20.0;
raster = 2.54;
// Abstand der Lochspalte 1 von der nächsten Platinenkante. Aus einem Foto der
// Platine abgelesen: die Kanten laufen durch Lochreihen, je etwa 2 bis 2,7 mm
rand_links = 2.4;
// Abstand von Streifen 1 zur vorderen Platinenkante, ebenfalls aus dem Foto.
// Die Platine hat 15 Streifen.
rand_vorn = 2.5;

/* [TF-Luna] */
// Breite über die beiden Befestigungsohren
luna_b = 35.0;
// Breite des Körpers ohne Ohren
luna_koerper_b = 26.5;
// Höhe hochkant: glatte Schmalseite unten, Steckerseite oben
luna_h = 21.25;
// Höhe der Schultern links und rechts neben dem Steckersockel
luna_schulter = 19.0;
// Breite des Steckersockels
luna_sockel_b = 18.0;
// Tiefe des Körpers in Blickrichtung, ohne Linsenfassungen
luna_t = 12.0;
// Überstand der Linsenfassungen vor dem Körper
linse_ueberstand = 1.5;
// Mittenabstand der beiden Linsen
linse_abstand = 10.5;
// Linsenmitte über der glatten Schmalseite
linse_hoehe = 9.0;
// Durchmesser der Fensteröffnung je Linse; die Linse misst mit Fassung 10 bis 11
fenster_d = 11.5;
// Dicke der Ohren an der Rückseite
luna_ohr_d = 2.0;
luna_spiel = 0.3;
// Platz über dem Sensor für Stecker und Kabelbogen – MESSEN
stecker_raum = 7.0;
// Platz zwischen Sensor und Platine; hier ragt oben die Antenne des D1 mini hinein
kabelraum = 9.0;

/* [USB und Kabel] */
// Mitte des USB-Schlitzes von der Platinenkante bei Spalte 1. Das Foto ergibt
// 17,0 für die Buchse, die Anprobe 19,5; der Schlitz deckt beides ab
usb_mitte = 18.25;
// Breite des Schlitzes; ein Steckergriff ist etwa 11 breit
usb_breite = 15.0;
// Unterkante des Schlitzes über der Platinenoberseite, gemessen
usb_unterkante = 4.0;
// Höhe der Öffnung für den Stecker. Darüber schließt eine Zunge am Deckel
// den Schlitz – MESSEN am eigenen Kabel
usb_hoehe = 9.0;
// Platz zwischen Platine und Rückwand
raum_hinten = 7.0;
// Kerbe für das Kabel zum Antrieb
kerbe_breite = 6.0;
kerbe_tiefe = 5.0;

/* [Gehäuse] */
wand = 2.0;
boden = 2.0;
deckel_d = 2.0;
// Schraubdome: Kernloch für M3-Schrauben, die sich ins Plastik schneiden
dom_d = 6.0;
kernloch_d = 2.6;
durchgang_d = 3.4;
// Lüftungsschlitze im Deckel über dem D1 mini
schlitze = true;

/* [Befestigung] */
laschen = true;
lasche_b = 14.0;
lasche_t = 24.0;
lasche_d = 3.0;
langloch_d = 4.5;
langloch_l = 8.0;

/* [Hidden] */
$fn = 40;
eps = 0.01;

// ---------------------------------------------------------------- abgeleitet
innen_b = platine_b + 2 * platine_spiel;
luna_tasche_t = luna_t + luna_spiel;                // Körper liegt innen an der Stirnwand an
anschlag_d = 1.5;                                   // Rippen hinter dem Sensor
platine_y0 = luna_tasche_t + anschlag_d + kabelraum; // Vorderkante Platine (innen)
innen_t = platine_y0 + platine_t + platine_spiel + raum_hinten;
platine_z0 = platine_abstand;                      // Unterkante Platine (innen)
platine_oben = platine_z0 + platine_d;
innen_h = max(platine_oben + hoehe_ueber_platine, luna_h + luna_spiel + stecker_raum);
// freie Höhe zwischen Platinenoberseite und Deckel
frei_ueber_platine = innen_h - platine_oben;

aussen_b = innen_b + 2 * wand;
aussen_t = innen_t + 2 * wand;
aussen_h = innen_h + boden;

luna_x0 = (innen_b - luna_b) / 2;
luna_mitte = innen_b / 2;
usb_x = innen_b - platine_spiel - usb_mitte;         // Mitte des USB-Schlitzes (innen)
fenster_z = linse_hoehe + luna_spiel / 2;           // Höhe der Linsenmitte (innen)
schlitz_b = linse_abstand + fenster_d;              // Breite des Fensterschlitzes

// Lochposition auf der Platine in Innenkoordinaten (Spalte, Streifen)
// Die Platine liegt mit Streifen 1 zum Sensor. Von oben gesehen (Sensor unten
// im Bild) läuft Spalte 1 deshalb rechts, die Spalten zählen nach links.
function loch_x(s) = innen_b - platine_spiel - rand_links - (s - 1) * raster;
function loch_y(r) = platine_y0 + rand_vorn + (r - 1) * raster;

// Positionen der vier Schraubdome (Innenkoordinaten)
dome = [
    [dom_d / 2, dom_d / 2],
    [innen_b - dom_d / 2, dom_d / 2],
    [dom_d / 2, innen_t - dom_d / 2],
    [innen_b - dom_d / 2, innen_t - dom_d / 2]
];

// Niederhalter am Deckel auf freien Stellen der Platine: [x, y, Durchmesser]
// in Innenkoordinaten. Spalte 17 / Streifen 3, Spalte 19 / Streifen 15 und ein
// dünner Stift auf dem schmalen Rand außen neben Spalte 1 in Höhe von Streifen 2.
niederhalter = [
    [loch_x(17), loch_y(3), 3],
    [loch_x(19), loch_y(15), 3],
    [innen_b - platine_spiel - 1.3, loch_y(2), 2.4]
];

// ------------------------------------------------------------------ Unterteil
module unterteil() {
    difference() {
        union() {
            // Wanne
            difference() {
                cube([aussen_b, aussen_t, aussen_h]);
                translate([wand, wand, boden])
                    cube([innen_b, innen_t, innen_h + eps]);
            }
            translate([wand, wand, boden]) einbauten();
            if (laschen) befestigung();
        }
        translate([wand, wand, boden]) ausschnitte();
    }
}

module einbauten() {
    // Schraubdome
    for (p = dome)
        translate([p[0], p[1], 0]) cylinder(d = dom_d, h = innen_h);

    // Auflagen unter den vier Platinenecken, außen mit Anschlag in y
    a = 2.5;
    for (x = [0, innen_b - a]) {
        // vorn
        translate([x, platine_y0, 0]) cube([a, a, platine_z0]);
        translate([x, platine_y0 - 1.5, 0]) cube([a, 1.5, platine_oben + 1]);
        // hinten
        translate([x, platine_y0 + platine_t - a, 0]) cube([a, a, platine_z0]);
        translate([x, platine_y0 + platine_t + platine_spiel, 0])
            cube([a, 1.5, platine_oben + 1]);
    }

    // Tasche für den TF-Luna: zwei Wangen außen an den Ohren und je eine
    // Rippe hinter den Ohren. Der Sensor wird von oben eingeschoben.
    wange = 1.5;
    tasche_h = 12;
    for (x = [luna_x0 - luna_spiel / 2 - wange, luna_x0 + luna_b + luna_spiel / 2])
        translate([x, 0, 0]) cube([wange, luna_tasche_t + anschlag_d, tasche_h]);
    for (x = [luna_x0 - luna_spiel / 2, luna_x0 + luna_b + luna_spiel / 2 - 4])
        translate([x, luna_tasche_t, 0]) cube([4, anschlag_d, tasche_h]);
}

module ausschnitte() {
    // Kernlöcher in den Domen
    for (p = dome)
        translate([p[0], p[1], innen_h - 12]) cylinder(d = kernloch_d, h = 12 + eps);

    // Fenster: Langloch über beide Linsen. Die Linsenfassungen tauchen in die
    // Wand ein, der Körper liegt innen an. Nach außen aufgeweitet.
    hull() {
        for (sx = [-1, 1])
            translate([luna_mitte + sx * linse_abstand / 2, eps, fenster_z])
                rotate([90, 0, 0])
                    cylinder(d1 = fenster_d, d2 = fenster_d + 2 * wand, h = wand + 2 * eps);
    }
    // Das Fenster ist nach oben offen, damit die vorstehenden Linsenfassungen
    // beim Einschieben von oben durch die Wand gleiten. Eine Zunge am Deckel
    // schließt den Schlitz wieder.
    translate([luna_mitte - schlitz_b / 2, -wand - eps, fenster_z])
        cube([schlitz_b, wand + 2 * eps, innen_h]);

    // USB-Schlitz in der Rückwand, nach oben offen: Platine samt Kabel einlegen
    translate([usb_x - usb_breite / 2, innen_t - eps, platine_oben + usb_unterkante])
        cube([usb_breite, wand + 2 * eps, innen_h]);

    // Kerbe für das Kabel zum Antrieb
    translate([innen_b * 0.3 - kerbe_breite / 2, innen_t - eps, innen_h - kerbe_tiefe])
        cube([kerbe_breite, wand + 2 * eps, kerbe_tiefe + eps]);
}

module befestigung() {
    for (seite = [0, 1]) {
        x = seite == 0 ? -lasche_b : aussen_b;
        difference() {
            translate([x, (aussen_t - lasche_t) / 2, 0])
                cube([lasche_b, lasche_t, lasche_d]);
            // Langloch quer, erlaubt seitliches Verschieben und leichtes Drehen
            hull() {
                for (dx = [-1, 1])
                    translate([x + lasche_b / 2 + dx * (langloch_l - langloch_d) / 2, aussen_t / 2, -eps])
                        cylinder(d = langloch_d, h = lasche_d + 2 * eps);
            }
        }
    }
}

// --------------------------------------------------------------------- Deckel
// Gezeichnet mit der Außenseite nach unten, also so, wie er gedruckt wird.
// x ist gespiegelt, damit er umgedreht auf das Unterteil passt.
module deckel() {
    difference() {
        union() {
            cube([aussen_b, aussen_t, deckel_d]);
            // Niederhalter für die Platine
            for (n = niederhalter)
                translate([dx(wand + n[0]), wand + n[1], deckel_d])
                    cylinder(d = n[2], h = frei_ueber_platine - 0.3);
            // Zunge, die den Fensterschlitz oberhalb der Linsen schließt
            translate([aussen_b / 2 - (schlitz_b - 0.4) / 2, 0, deckel_d])
                cube([schlitz_b - 0.4, wand, innen_h - fenster_z - fenster_d / 2 - 0.3]);
            // Zunge, die den USB-Schlitz oberhalb des Steckers schließt
            translate([dx(wand + usb_x) - (usb_breite - 0.4) / 2, aussen_t - wand, deckel_d])
                cube([usb_breite - 0.4, wand, innen_h - platine_oben - usb_unterkante - usb_hoehe - 0.3]);
            // Niederhalter für den Sensor: zwei Stege auf den Schultern neben dem Stecker
            for (sx = [-1, 1])
                translate([aussen_b / 2 + sx * (luna_sockel_b / 2 + 2.2) - 1.5, wand + luna_tasche_t / 2 - 3, deckel_d])
                    cube([3, 6, innen_h - luna_schulter - 0.4]);
        }
        // Schraubenlöcher
        for (p = dome)
            translate([dx(wand + p[0]), wand + p[1], -eps])
                cylinder(d = durchgang_d, h = deckel_d + 2 * eps);
        // Lüftungsschlitze über dem D1 mini
        if (schlitze)
            for (i = [0 : 4])
                translate([dx(wand + loch_x(3.5 + i * 1.5)) - 0.75, wand + loch_y(2), -eps])
                    cube([1.5, 6 * raster, deckel_d + 2 * eps]);
    }
}

// spiegelt eine x-Koordinate für den umgedreht gedruckten Deckel
function dx(x) = aussen_b - x;

// ------------------------------------------------------------- Kontrollkörper
module bauteile() {
    translate([wand, wand, boden]) {
        // Platine
        color("green", 0.5)
            translate([platine_spiel, platine_y0, platine_z0])
                cube([platine_b, platine_t, platine_d]);
        // Raum für D1 mini, Relais und Elko
        color("gray", 0.25)
            translate([platine_spiel, platine_y0, platine_oben])
                cube([platine_b, platine_t, hoehe_ueber_platine]);
        // Antenne des D1 mini, ragt über Streifen 1 hinaus (geschätzt)
        color("gray", 0.25)
            translate([loch_x(11) - 1.4, platine_y0 - 9, platine_oben + 11])
                cube([25.6, 9, 5]);
        // TF-Luna, hochkant, Linsen nach vorn
        color("black", 0.6) translate([luna_mitte, 0, luna_spiel / 2]) {
            // Körper bis zur Schulter
            translate([-luna_koerper_b / 2, 0, 0]) cube([luna_koerper_b, luna_t, luna_schulter]);
            // Steckersockel
            translate([-luna_sockel_b / 2, 0, luna_schulter]) cube([luna_sockel_b, luna_t, luna_h - luna_schulter]);
            // Ohren an der Rückseite
            translate([-luna_b / 2, luna_t - luna_ohr_d, linse_hoehe - 2.25]) cube([luna_b, luna_ohr_d, 4.5]);
            // Linsenfassungen
            for (sx = [-1, 1])
                translate([sx * linse_abstand / 2, 0, linse_hoehe])
                    rotate([90, 0, 0]) cylinder(d = 11.3, h = linse_ueberstand);
        }
    }
}

// -------------------------------------------------------------------- Ausgabe
if (teil == "unterteil") {
    unterteil();
    if (zeige_bauteile) %bauteile();
} else if (teil == "deckel") {
    deckel();
} else if (teil == "zusammenbau") {
    unterteil();
    if (zeige_bauteile) %bauteile();
    // Deckel umgedreht aufgesetzt
    %translate([aussen_b, 0, aussen_h + deckel_d]) rotate([0, 180, 0]) deckel();
} else {
    unterteil();
    if (zeige_bauteile) %bauteile();
    translate([aussen_b + (laschen ? lasche_b : 0) + 10, 0, 0]) deckel();
}
