# esphome-garage

Garagentor-Status (offen, geschlossen, fährt, halb offen) für Home Assistant:
Wemos D1 mini mit TF-Luna-Abstandssensor am Antrieb Normstahl Magic 600,
optional mit Relais am Impulseingang. Firmware: ESPHome.

- `sensorplatine.html` – Schaltplan, Stückliste und Lötplan (Lochraster und Streifenraster)
- `assets/gen_board.py` – erzeugt `sensorplatine.html` und prüft dabei die Netze beider Layouts:
  `python3 assets/gen_board.py sensorplatine.html`
- `assets/gehaeuse.scad` – parametrisches Gehäuse für Platine und TF-Luna (OpenSCAD), Sensormaße nach Datenblatt A05, übrige Maße vor dem Druck nachmessen
- `relais-test.yaml` – Relaistest ohne WLAN und Sensor: Relais und LED schalten alle 3 s für 0,5 s
- `garagentor.yaml` – die eigentliche Firmware: Torposition, Torzustand und Impuls für Home Assistant
- `secrets.yaml.example` – Vorlage für die Zugangsdaten

## Relaistest flashen (Windows)

J2 dabei nicht mit dem Antrieb verbinden.

```
pip install esphome
esphome run relais-test.yaml
```

In der PowerShell ausführen, nicht in WSL: WSL sieht die USB-Schnittstelle des D1 mini
nur mit zusätzlichem `usbipd-win`. `esphome run` übersetzt, flasht über den COM-Port und
zeigt danach das Log.

## Firmware flashen

```
copy secrets.yaml.example secrets.yaml
```

`secrets.yaml` ausfüllen, dann:

```
py -m esphome run garagentor.yaml
```

Nach dem Einbau in Home Assistant kalibrieren: Tor ganz schließen und „Kalibrieren: Tor ist zu“
drücken, Tor ganz öffnen und „Kalibrieren: Tor ist offen“ drücken.
