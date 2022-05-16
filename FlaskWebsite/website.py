#!/usr/bin/env python
from flask import Flask, render_template, request
import pygame # sounds abspielen
import threading
import time
from datetime import datetime
import RPi.GPIO as GPIO
import I2C_LCD_driver 
import json
import os

app = Flask(__name__)  # __name__ = name der Datei also "website"

# Config
button = 12
rotary_button = 13


########################
####      Data      ####
########################
# Pfad zu Programm
path_programm = __file__[:-11] 
#print(path_programm+"/website_settings.json") 


# Wecker
alarms = [
    {
        "Aktiv" : "Ja",
        "Tag" : "Montag",
        "Uhrzeit" : "06:30",
        "Weckton" : "Rock",  # Rock, Chill, Radio
        "Licht vorher" : 15,
        "Sonnenaufgang" : "Ja"
    },
    {
        "Aktiv" : "Ja",
        "Tag" : "Dienstag",
        "Uhrzeit" : "06:30",
        "Weckton" : "Rock",  # Rock, Chill, Radio
        "Licht vorher" : 15,
        "Sonnenaufgang" : False
    },
    {
        "Aktiv" : "Ja",
        "Tag" : "Mittwoch",
        "Uhrzeit" : "06:30",
        "Weckton" : "Rock",  # Rock, Chill, Radio
        "Licht vorher" : 15,
        "Sonnenaufgang" : False
    },
    {
        "Aktiv" : "Ja",
        "Tag" : "Donnerstag",
        "Uhrzeit" : "06:30",
        "Weckton" : "Rock",  # Rock, Chill, Radio
        "Licht vorher" : 15,
        "Sonnenaufgang" : False
    },
    {
        "Aktiv" : "Ja",
        "Tag" : "Freitag",
        "Uhrzeit" : "06:30",
        "Weckton" : "Rock",  # Rock, Chill, Radio
        "Licht vorher" : 15,
        "Sonnenaufgang" : False
    },
    {
        "Aktiv" : "Ja",
        "Tag" : "Samstag",
        "Uhrzeit" : "08:30",
        "Weckton" : "Rock",  # Rock, Chill, Radio
        "Licht vorher" : 15,
        "Sonnenaufgang" : False
    },
    {
        "Aktiv" : "Ja",
        "Tag" : "Sonntag",
        "Uhrzeit" : "08:30",
        "Weckton" : "Rock",  # Rock, Chill, Radio
        "Licht vorher" : 15,
        "Sonnenaufgang" : False
    },
]

# Einstellungen
settings = {
    "Snooze Time" : 5
}

# Dateien erstellen mit Werkseinstellungen (falls gelöscht)
def create_files():
    if not os.path.isfile(path_programm+"/website_settings.json"):
        with open(path_programm+"/website_settings.json", "w") as file_data: 
            file_data.write(json.dumps(settings))

    if not os.path.isfile(path_programm+"/website_alarms.json"):
        with open(path_programm+"/website_alarms.json", "w") as file_data:
            file_data.write(json.dumps(alarms))

create_files()

def reset_files():
    if os.path.isfile(path_programm+"/website_settings.json"):
        os.remove(path_programm+"/website_settings.json")
    if os.path.isfile(path_programm+"/website_alarms.json"):
        os.remove(path_programm+"/website_alarms.json")
    create_files()


# Überschreiben der im Programm verwendeten Daten mit den Daten aus der Datei
with open(path_programm+"/website_settings.json", "r") as file_data: 
    settings_string = file_data.read()
    settings = json.loads(settings_string)

with open(path_programm+"/website_alarms.json", "r") as file_data:
    alarms_string = file_data.read()
    alarms = json.loads(alarms_string) 



########################
#### Flask Website  ####
########################
@app.route("/", methods=["GET", "POST"])
def start():
    #if request.method == 'POST':
        
    return render_template("start.html", name="Start") 

@app.route("/einstellungen", methods=["GET", "POST"])
def einstellungen(): 
    if request.method == 'POST':
        settings["Snooze Time"] = request.form.get("snoozetime")
    # write new data to file
    with open(path_programm+"/website_settings.json", "w") as file_data:
        file_data.write(json.dumps(settings))
    return render_template("einstellungen.html", name="Einstellungen", settings=settings)

@app.route("/werkseinstellungen", methods=["GET", "POST"])
def werkseinstellungen():
    reset_thread.start()
    return render_template("start.html", name="Start", alarms=alarms)

@app.route("/altes_vom_wecker", methods=["GET", "POST"])
def altes_vom_wecker():
    if request.method == 'POST':
        for x in range(0,7):
            alarms[x]["Aktiv"] = request.form.get("active_"+str(x))   
            alarms[x]["Weckton"] = request.form.get("sound_"+str(x))   
            alarms[x]["Uhrzeit"] = request.form.get("wtime_"+str(x))  
            alarms[x]["Licht vorher"] = request.form.get("ltime_"+str(x))   
            alarms[x]["Sonnenaufgang"] = request.form.get("sunrise_"+str(x))   
        # write new data to file
        with open(path_programm+"/website_alarms.json", "w") as file_data:
            file_data.write(json.dumps(alarms))
    return render_template("altes_vom_wecker.html", 
                            name="Altes vom Wecker", 
                            alarms=alarms,
                            nr_of_alarms=len(alarms)
                            ) 


########################
####    Embedded    ####
########################

### Inits ####
mylcd = I2C_LCD_driver.lcd()

# GPIOs
GPIO.setmode(GPIO.BCM)
GPIO.setup(rotary_button, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Rotary Button
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Button
#GPIO.add_event_detect( button, GPIO.FALLING, callback=callback, bouncetime=200)


def lcd_func():
    while(1):
        time_now = datetime.now().replace(microsecond=0)
        mylcd.lcd_display_string("{:>16}".format(str(time_now.strftime('%d %b: %H:%M:%S '))) , 1)

def reset_func():
    os.remove(path_programm+"/website_settings.json")
    os.remove(path_programm+"/website_alarms.json")
    time.sleep(2)
    print("Rebooting...")
    os.system("sudo reboot")


# Threads
lcd_thread = threading.Thread(target=lcd_func,)
lcd_thread.start()

reset_thread = threading.Thread(target=reset_func,)


# Start Website
if __name__ == '__main__':
    app.run(host='0.0.0.0')
    #app.run(debug=False, port=5000, host='127.0.0.1')

print("Beende Main")

