import threading, time, yaml
from textnow.sms import sms
from textnow.ui import ui
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

creds = TextNowCreds(username, sid, csrf)

# Functions for threads.

def threadwrapper(func):
    def wrapper():
        while True:
            try:
                func()
            except BaseException as error:
                print('abSENT - {!r}; restarting thread'.format(error))
            else:
                print('abSENT - Exited normally, bad thread, restarting')
    return wrapper

# Listen for SMS and call threadclass upon new initial contact.

def sms_listener():
    
    txt = sms(creds) 
    activethreads = {
    }
    
    while True:

        for msg in txt.listen():
            print(msg)
            if Number(msg.number) not in activethreads:
                txt.mark_as_read(msg)
                activethreads.update({Number(msg.number): ui(creds, msg)})
                activethreads[Number(msg.number)].start()
                print(activethreads[Number(msg.number)], "started")

        # Thread cleaner.

        dead = []

        for number in activethreads:
            if not activethreads[number].is_alive():
                dead.append(number)

        for number in dead:
            print(activethreads[number], "killed")
            activethreads.pop(number)

        time.sleep(0.2)

# Listen for Schoology updates.

def sc_listener():
    
    absent = absence(sckeys, scsecrets)

    while True:
        date = datetime.now() - timedelta(hours=5)
        print(absent.filter_absences_north(date))
        print("\n\n")
        print(absent.filter_absences_south(date))
        print("\n\n\n\n")
        
        time.sleep(10)

# Configure and start threads.

threads = {
        'sc': threading.Thread(target=threadwrapper(sc_listener), name='sc listener'),
        'sms': threading.Thread(target=threadwrapper(sms_listener), name='sms listener')
}


threads['sms'].start()
threads['sc'].start()
