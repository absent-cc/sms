import threading, time, yaml
from textnow.sms import SMS
from textnow.ui import UI
from schoology.absence import *
from datetime import datetime, timedelta
from dataStructs import *
from driver.logic import LogicDriver

# Open files.
with open('secrets.yml') as f:
    cfg = yaml.safe_load(f)

# Define API variables.
scCreds = SchoologyCreds(cfg['north']['key'], cfg['north']['secret'], cfg['south']['key'], cfg['south']['secret'])
textnowCreds = TextNowCreds(cfg['textnow']['username'], cfg['textnow']['sid'], cfg['textnow']['csrf'])

# Function for writing state.
def writeState(school: SchoolName, date, statePath = 'state.yml'):
    # Read state yaml file.
    with open(statePath, 'r') as f:
        state = yaml.safe_load(f)
    
    state[str(school)] = date.strftime('%m/%-d/%Y')
    if school == SchoolName.NEWTON_NORTH:
        state[str(SchoolName.NEWTON_SOUTH)] = state[str(SchoolName.NEWTON_SOUTH)]
    else:
        state[str(SchoolName.NEWTON_NORTH)] = state[str(SchoolName.NEWTON_NORTH)]

    # Write new state to state file
    with open('state.yml', 'w') as f:
        yaml.safe_dump(state, f)
    return state

def fetchStates(date, statePath = 'state.yml'):
    stateDict = {
        SchoolName.NEWTON_NORTH: False,
        SchoolName.NEWTON_SOUTH: False
    }
    # Read state yaml file.
    with open(statePath, 'r') as f:
        state = yaml.safe_load(f)
    if state[str(SchoolName.NEWTON_NORTH)] == date.strftime('%m/%-d/%Y'):
        stateDict[SchoolName.NEWTON_NORTH] = True
    if state[str(SchoolName.NEWTON_SOUTH)] == date.strftime('%m/%-d/%Y'):
        stateDict[SchoolName.NEWTON_SOUTH] = True
    return stateDict

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
    textnow = SMS(textnowCreds) # Create textnow API instance
    activethreads = { # stateionary of active threads.
    }

    textnow.send('+16176868207', 'abSENT listener started!')

    while True:
        # Create thread for each new initial contact.
        for msg in textnow.listen():
            # Create number object
            number = Number(msg.number)
            if number not in activethreads:
                textnow.markAsRead(msg) # Mark msg as read
                activethreads.update({number: UI(textnowCreds, msg)}) # Add new thread to active threads.
                activethreads[number].start() # Start the thread.
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
    
    restTime = timedelta(seconds=10) # Time between each check.
    lastCheckTime = datetime.now() - restTime # Last time a check was made.

    # Define initial vars.
    logic = LogicDriver(textnowCreds, scCreds)
    north = SchoolName.NEWTON_NORTH
    south = SchoolName.NEWTON_SOUTH

    while True:
        date = datetime.now() - timedelta(hours=5)
        states = fetchStates(date)
        while not states[north] or not states[south]:
            currentTime = datetime.now()
            if lastCheckTime + restTime < currentTime: # Sleep without delay   
                if not states[north]:
                # NNHS Runtime.
                    update = logic.run(date, north)
                    if update:
                        writeState(north, date)
                if not states[south]:
                    # NSHS Runtime
                    update = logic.run(date, south)
                    if update:
                        writeState(south, date)
                states = fetchStates(date)
                lastCheckTime = currentTime

# Configure and start threads.
threads = {
        'sc': threading.Thread(target=threadwrapper(sc_listener), name='sc listener'),
        'sms': threading.Thread(target=threadwrapper(sms_listener), name='sms listener')
}

threads['sms'].start()
threads['sc'].start()