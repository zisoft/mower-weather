#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# Mähroboter parken, wenn der Deutsche Wetterdienst (DWD) eine Warnmeldung
# für die Region ausgibt.
#
# Mario Zimmermann <mail@zisoft.de>
# 2024-06-03
# ---------------------------------------------------------------------------

import os
from configparser import ConfigParser
import requests
import re
import json
import datetime
import time
import smtplib
from email.mime.text import MIMEText


# ---------------------------------------------------------------------------
# OpenData Hilfe:
# https://www.dwd.de/DE/leistungen/opendata/hilfe.html
#
# DWD Produktübersicht:
# https://www.dwd.de/DE/leistungen/opendata/help/warnungen/dwd_warnings_products_overview_de_pdf.pdf?__blob=publicationFile&v=7
#
# DWD WarnCell-IDs:
# https://www.dwd.de/DE/leistungen/opendata/help/warnungen/cap_warncellids_csv.csv?__blob=publicationFile&v=6
#
# Hochaktueller Landreis-Status (JSON):
# https://www.dwd.de/DWD/warnungen/warnapp/json/warnings.json
#
# Husqvarna API:
# https://developer.husqvarnagroup.cloud/apis/automower-connect-api?tab=openapi
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Configfile einlesen
config_object = ConfigParser()
config_object.read("./mower_weather.ini")

HUSQVARNA_API = config_object["HUSQVARNA_API"]
MISC          = config_object["MISC"]
DWD           = config_object["DWD"]
MOWER         = config_object["MOWER"]
SMTP          = config_object["SMTP"]
EMAIL         = config_object["EMAIL"]


# ---------------------------------------------------------------------------
def parkMower(duration_minutes):
    # Authentifizierung
    response = requests.post(
        HUSQVARNA_API["auth_url"],
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data = {
            "grant_type": "client_credentials",
            "client_id": HUSQVARNA_API["client_id"],
            "client_secret": HUSQVARNA_API["client_secret"]
        }
    )

    data = json.loads(response.text)
    access_token = data["access_token"]

    # Mower parken
    response = requests.post(
        f"{HUSQVARNA_API['base_url']}/mowers/{MOWER['mower_id']}/actions",
        headers = {
            "Content-Type": "application/vnd.api+json",
            "Authorization-Provider": "husqvarna",
            "Authorization": f"Bearer {access_token}",
            "X-Api-Key": HUSQVARNA_API["client_id"]
        },
        json = {
            "data": {
                "type": "Park",
                "attributes": {
                    "duration": duration_minutes
                }
            }
        }
    )

    # print(response.text)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
def send_email(email_address: str, subject: str, body: str):
    server = smtplib.SMTP(SMTP["server"])
    server.starttls()
    server.login(SMTP["user"], SMTP["password"])

    msg = MIMEText(body, _charset='utf-8')
    msg["From"] = EMAIL["from"]
    msg["Subject"] = subject

    server.sendmail(EMAIL["from"], email_address, msg.as_string())
    server.quit()
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Aktueller Zeitstempel
now = datetime.datetime.now()
now_timestamp = int(now.timestamp())


# ---------------------------------------------------------------------------
# Zeitstempel einlesen, bis zu dem der Mower geparkt ist. Wenn der noch in der
# Zukunft liegt, gibt es nichts zu tun
park_timestamp = 0
if os.path.isfile(MISC["statusfile"]):
    with open(MISC["statusfile"], 'r') as statusfile:
        park_timestamp = int(statusfile.readline())

if park_timestamp > now_timestamp:
    exit()


# ---------------------------------------------------------------------------
# Wetter-Warnungen des DWD abfragen.
# Da der Service manchmal mit einem Fehler antwortet, max. 10 Versuche
try_count = 0
success = False

while not success and try_count < 10: 
    response = requests.get(DWD["url"])

    text = response.text
    text = re.sub("warnWetter.loadWarnings\(", "", text)
    text = re.sub("\);", "", text)

    try:
        data = json.loads(text)
        success = True
    except json.decoder.JSONDecodeError as e:
        try_count += 1
        time.sleep(1)

if not success:
    exit()


# ---------------------------------------------------------------------------
# Alle vorkommenden DWD-Events sammeln und in der Events-Datei ablegen
events = {}

# bisherige Einträge einlesen
if os.path.isfile(DWD["events_file"]):
    with open(DWD["events_file"], 'r') as file:
        file_events = file.readlines()
        for event in file_events:
            events[event.rstrip()] = 1

event_count = len(events)

for cellId in data["warnings"]:
    for warning in data["warnings"][cellId]:
        events[warning["event"]] = 1

if len(events) > event_count:
    # Neue Events gefunden
    with open(DWD["events_file"], 'w') as file:
        for event in events:
            file.write(f'{event}\n')
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Daten für die gewünschten Regionen verarbeiten
if data["warnings"]:
    for cell_info in DWD["cell_ids"].split(","):
        cell_id,location = cell_info.split(";")

        if cell_id in data["warnings"].keys():
            cell_data = data["warnings"][cell_id]

            with open(MISC["logfile"], 'a') as logfile:
                logfile.write(f'{now.strftime("%Y-%m-%d %H:%M:%S")}\n')
                logfile.write(f'cell-id: {cell_id}\n')
                logfile.write(f'location: {location}\n')
            
                for cd in cell_data:
                    logfile.write(f'{cd["event"]}\n')
                    logfile.write(f'type: {cd["type"]}\n')
                    logfile.write(f'level: {cd["level"]}\n')

                    if cd["start"]:
                        s_dt = int(int(cd["start"]) / 1000)
                        start_dt = datetime.datetime.fromtimestamp(s_dt)
                        start_dt = f"{start_dt:%Y-%m-%d %H:%M:%S}"
                    else:
                        start_dt = ""

                    if cd["end"]:
                        e_dt = int(int(cd["end"]) / 1000)
                        end_dt = datetime.datetime.fromtimestamp(e_dt)
                        end_dt = f"{end_dt:%Y-%m-%d %H:%M:%S}"
                    else:
                        end_dt = ""

                    logfile.write(f'start_dt: {start_dt}\n')
                    logfile.write(f'end_dt: {end_dt}\n')

                    for park_event in DWD["park_events"].split(","):
                        if park_event in cd["event"]:
                            park_duration = int((e_dt - now_timestamp) / 60)

                            with open(MISC["statusfile"], 'w') as statusfile:
                                statusfile.write(f'{e_dt}\n')

                            parkMower(park_duration)
                            logfile.write(f"*** MOWER GEPARKT BIS {end_dt}\n")

                            if EMAIL["use_mail"] == "1":
                                # Send email
                                mail_text = cd["description"]
                                mail_text += "\n\n"
                                mail_text += f"{cd['event']}\n"
                                mail_text += f"Ort: {location}\n"
                                mail_text += f"Beginn: {start_dt}\n"
                                mail_text += f"Ende: {end_dt}\n\n"
                                mail_text += f"Mähroboter geparkt bis {end_dt}\n"
                                
                                send_email(EMAIL["to"], cd["headline"], mail_text)

                    logfile.write('------\n')
