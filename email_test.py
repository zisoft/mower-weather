#!/usr/bin/env python3
import os
from configparser import ConfigParser
import smtplib
from email.mime.text import MIMEText
import requests
import json


abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)



#Read config file
config_object = ConfigParser()
config_object.read("./mower_weather.ini")

SMTP          = config_object["SMTP"]
EMAIL         = config_object["EMAIL"]


server = smtplib.SMTP(SMTP["server"])
server.starttls()
server.login(SMTP["user"], SMTP["password"])

msg = MIMEText("Testmail\n", _charset='utf-8')
msg["From"] = EMAIL["from"]
msg["Subject"] = "Testmail von MowerWeather"

server.sendmail(EMAIL["from"], EMAIL["to"], msg.as_string())
server.quit()
