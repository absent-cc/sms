import threading, time, yaml
from textnow.sms import sms
from textnow.ui import ui
from schoology.absence import *
from datetime import datetime, timedelta
from dataStructs import *
from driver.logic import LogicDriver

# Open secrets file.
with open('secrets.yml', 'r') as f:
    cfg = yaml.safe_load(f)

# Define API variables.
sid = cfg['textnow']['sid']
username = cfg['textnow']['username']
csrf = cfg['textnow']['csrf']
sckeys = [cfg['north']['key'], cfg['south']['key']]
scsecrets = [cfg['north']['secret'], cfg['south']['secret']]
creds = TextNowCreds(username, sid, csrf)

# Make threads regenerate on fault.
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
    
    # Define initial vars.
    textnow = sms(creds) 
    activethreads = {
    }

    textnow.send('+16175059626', 'abSENT listener started!')

    while True:

        # Create thread for each new initial contact.
        for msg in textnow.listen():
            number = Number(msg.number)
            if number not in activethreads:
                textnow.markAsRead(msg)
                activethreads.update({number: ui(creds, msg)})
                activethreads[number].start()
                print(f"Thread created: {str(number)} with initial message '{msg.content}'.")

        # Thread cleaner.
        dead = []
        for number in activethreads:
            if not activethreads[number].is_alive():
                dead.append(number)
        for number in dead:
            print(f"Thread terminated: {str(number)}.")
            activethreads.pop(number)

        # Wait for a bit.
        time.sleep(1)

# Listen for Schoology updates.
def sc_listener():
    
    # Define initial var.
    absent = absence(sckeys, scsecrets)

    # Print Schoology.
    while True:
        # Grab current date, run functions using current date + print.
        date = datetime.now() - timedelta(hours=5)
        print(absent.filterAbsencesNorth(date))
        print("\n\n")
        print(absent.filterAbsencesSouth(date))
        print("\n\n\n\n")

        # Wait for a bit.
        time.sleep(100)

# Configure and start threads.
threads = {
        'sc': threading.Thread(target=threadwrapper(sc_listener), name='sc listener'),
        'sms': threading.Thread(target=threadwrapper(sms_listener), name='sms listener')
}

threads['sms'].start()
#threads['sc'].start()

driver = LogicDriver(creds, sckeys, scsecrets)
date = datetime.now() - timedelta(hours=5)

driver.run(date)
