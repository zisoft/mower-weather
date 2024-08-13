#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# Aktuelle DWD-Warnungen ermitteln
#
# Mario Zimmermann <mail@zisoft.de>
# 2024-06-03
# ---------------------------------------------------------------------------

from configparser import ConfigParser
import requests
import json
import re
import time

# ConfigFile lesen
config_object = ConfigParser()
config_object.read("mower_weather.ini")

DWD = config_object["DWD"]

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

print(json.dumps(data, indent=2, ensure_ascii=False))
