# Husqvarna AutoMower parken bei DWD-Warnung

Der Deutsche Wetterdienst (DWD) bietet eine Schnittstelle an, die kostenlos abgefragt werden kann und die für alle Regionen in Deutschland die aktuellen Wetterwarnungen bereitstellt. Die Informationen werden alle 10min aktualisiert.

Über das Husqvarna API können dem Mähroboter Befehle geschickt werden.

Diese Python-Scripte fragen die aktuellen Warnungen des Deutschen Wetterdienstes ab und parken ggf. den Mähroboter bis zum Ende des Warnungs-Zeitraums.

- Konfigurierbare Ereignisse, die zum Parken führen (Gewitter, Starkregen, Sturm, Hitze, ...)
- Park-Befehl bis zum gemeldeten Ende-Zeitpunkt des Ereignisses
- Auf Wunsch Email-Versand bei Eintreten eines Park-Ereignisses

## Voraussetzungen
Ein Husqvarna AutoMower mit WLAN-Verbindung.

Um mit dem AutoMower kommunizieren zu können, muss zunächst im [Husqvarna Developer Portal](https://developer.husqvarnagroup.cloud/docs/get-started) ein API-Key erstellt werden (Schritte der Beschreibung befolgen). Nach erfolgreicher Registrierung erhält man einen Application Key (`client_id`) und ein Application Secret (`client_secret`).

## Installation
Zur Verwendung dieser Scripte eignet sich ein kleiner Server, der mit dem heimischen WLAN verbunden ist und auf dem Python installiert ist (z.B. ein Raspberry Pi).

- Das Repository in einem beliebigen Verzeichnis clonen
- Die Datei `mower_weather.ini_example` kopieren mit dem Namen `mower_weather.ini`. Anschließend die oben erhaltene `client_id` und `client_secret` in der Sektion `[HUSQVARNA_API]` eintragen.
- Zur Ermittlung der ID des AutoMowers kann jetzt das Script `./mower_info.py` gestartet werden. Man erhält einen JSON-Datenblock mit den Informationen über den mit dem Account verknüpften AutoMower. Ganz oben findet man die `id`. Den Wert kopieren und in die `mower_weather.ini` unter `mower_id` in der Sektion `[MOWER]` eintragen.
- Die Datei `DWD_warncellids.csv` öffnen und die gewünschte Region suchen. Es empfiehlt sich, nicht nur die Stadt zu ermitteln, sondern zusätzlich auch noch den übergeordneten Landreis. Dann die gefundenen Zellen in der `mower_weather.ini` unter `cell_ids` in der Sektion `[DWD]` eintragen. Das Format sollte sein `cell_id;beschreibung,cell_id;beschreibung, ...` (Siehe Beispiel in der `mower_weather.ini`).
- Unter `park_events` in der Sektion `[DWD]` müssen die Warn-Ereignisse eingetragen werden, die zu einem Parken des AutoMowers führen sollen. Die Datei `DWD_events.txt` enthält die gesammelten Ereignisse und wird automatisch erweitert, wenn neue Ereignisse auftreten.

### Email-Versand (optional)
Auf Wunsch kann das Script eine Email verschicken, wenn eine Wetterwarnung zum Parken des AutoMowers geführt hat. Dazu in der `mower_weather.ini` in der Sektion `[EMAIL]` den Eintrag `use_email` auf `1` setzen und unter `[SMTP]` die Daten des SMTP-Servers eintragen. Mit dem Script `email_test.py` kann getestet werden, ob der Email-Versand funktioniert.

### crontab
Wenn alles korrekt eingerichtet ist, sollte das Script `mower_weather.py` regelmäßig (z.B. alle 30min) in den Stunden des AutoMower-Zeitplans laufen, z.B. über einen Eintrag in der crontab.
