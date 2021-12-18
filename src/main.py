import threading, time, yaml
from textnow.sms import sms
from textnow.ui import ui
from schoology.absence import *
from datetime import datetime, timedelta
from dataStructs import *
from driver.logic import LogicDriver

# Open files.
with open('secrets.yml') as f:
    cfg = yaml.safe_load(f)
with open('state.yml') as f:
    state = yaml.safe_load(f)

# Define API variables.
scCreds = SchoologyCreds(cfg['north']['key'], cfg['north']['secret'], cfg['south']['key'], cfg['south']['secret'])
textnowCreds = TextNowCreds(cfg['textnow']['username'], cfg['textnow']['sid'], cfg['textnow']['csrf'])

# Function for writing state.
def writeState(school: SchoolName, date):
    dict = {}
    dict[str(school)] = date.strftime('%m/%-d/%Y')
    if school == SchoolName.NEWTON_NORTH:
        dict[str(SchoolName.NEWTON_SOUTH)] = state[str(SchoolName.NEWTON_SOUTH)]
    else:
        dict[str(SchoolName.NEWTON_NORTH)] = state[str(SchoolName.NEWTON_NORTH)]
    with open('state.yml', 'w') as f:
        yaml.safe_dump(dict, f)

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
    textnow = sms(textnowCreds) 
    activethreads = {
    }

    textnow.send('+16175059626', 'abSENT listener started!')

    while True:

        # Create thread for each new initial contact.
        for msg in textnow.listen():
            number = Number(msg.number)
            if number not in activethreads:
                textnow.markAsRead(msg)
                activethreads.update({number: ui(textnowCreds, msg)})
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
    
    # Define initial vars.
    logic = LogicDriver(textnowCreds, scCreds)
    north = SchoolName.NEWTON_NORTH
    south = SchoolName.NEWTON_SOUTH

    # Print Schoology.
    while True:
        # Grab current date, run functions using current date.
        date = datetime.now() - timedelta(hours=5)
        
        if state[str(north)] != date.strftime('%m/%-d/%Y'):
            # NNHS Runtime.
            update = logic.run(date, north)
            if update:
                writeState(north, date)
        else:
            print("Users already notified!")
        if state[str(south)] != date.strftime('%m/%-d/%Y'):
            # NSHS Runtime.
            update = logic.run(date, north)
            if update:
                writeState(south, date)
        else:
            print("Users already notified!")

        print("Looped once!")
        # Wait for a bit.
        time.sleep(100)

# Configure and start threads.
threads = {
        'sc': threading.Thread(target=threadwrapper(sc_listener), name='sc listener'),
        'sms': threading.Thread(target=threadwrapper(sms_listener), name='sms listener')
}

threads['sms'].start()
threads['sc'].start()