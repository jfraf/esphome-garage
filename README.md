# esphome-garage

Garagentor-Status (offen, geschlossen, fährt, halb offen) für Home Assistant:
Wemos D1 mini mit TF-Luna-Abstandssensor am Antrieb Normstahl Magic 600,
optional mit Relais am Impulseingang. Firmware: ESPHome.

- `sensorplatine.html` – Schaltplan, Stückliste und Lötplan (Lochraster und Streifenraster)
- `assets/gen_board.py` – erzeugt `sensorplatine.html` und prüft dabei die Netze beider Layouts:
  `python3 assets/gen_board.py sensorplatine.html`

Die ESPHome-Konfiguration folgt.
