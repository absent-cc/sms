import threading, time, yaml
from textnow.sms import *
from schoology.absence import *
from datetime import datetime, timedelta

# Open secrets file.

with open('secrets.yml', 'r') as f:
    cfg = yaml.safe_load(f)

# Define API variables.

sid = cfg['textnow']['sid']
csrf = cfg['textnow']['csrf']
username = cfg['textnow']['username']

sckeys = [cfg['north']['key'], cfg['south']['key']]
scsecrets = [cfg['north']['secret'], cfg['south']['secret']]

# Define objects. 

sms = sms(sid, csrf, username)
ui = ui(sms) 
absent = absence(sckeys, scsecrets)

# Define date.

date = datetime.now() - timedelta(hours=5)

# Functions for threads.

def sms_listener(sms, ui):
    while True:
        for msg in sms.receive():
            print(msg)
            ui.main(msg)
        time.sleep(0.2)

def sc_listener(absent, date):
    while True:
        print(absent.filter_absences_north(date))
        print("\n\n")
        print(absent.filter_absences_south(date))
        print("\n\n\n\n")
        time.sleep(10)

# Configure and start threads.

schoology = threading.Thread(target=sms_listener, args=(sms, ui))
textnow = threading.Thread(target=sc_listener, args=(absent, date))

schoology.start()
textnow.start()
