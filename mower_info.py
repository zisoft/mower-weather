#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# Mähroboter Infos ermittlen
#
# Mario Zimmermann <mail@zisoft.de>
# 2024-06-03
# ---------------------------------------------------------------------------

from configparser import ConfigParser
import requests
import json


# ConfigFile lesen
config_object = ConfigParser()
config_object.read("mower_weather.ini")

HUSQVARNA_API = config_object["HUSQVARNA_API"]

# ---------------------------------------------------------------------------
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

# Daten abfragen
response = requests.get(
    f"{HUSQVARNA_API['base_url']}/mowers",
    headers = {
        "Authorization-Provider": "husqvarna",
        "Authorization": f"Bearer {access_token}",
        "X-Api-Key": HUSQVARNA_API["client_id"]
    }
)

data = json.loads(response.text)
print(json.dumps(data, indent=2, ensure_ascii=False))

