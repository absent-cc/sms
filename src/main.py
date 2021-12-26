import threading, time, yaml
from textnow.sms import SMS
from textnow.ui import UI
from dataStructs import *
from driver.schoologyListener import *
from database.databaseHandler import *
from datetime import timedelta, datetime, timezone
from database.logger import Logger

logger = Logger()
logger.systemStartup()

# Open files.
with open('secrets.yml') as f:
    cfg = yaml.safe_load(f)

# Define API variables.
scCreds = SchoologyCreds(cfg['north']['key'], cfg['north']['secret'], cfg['south']['key'], cfg['south']['secret'])
textnowCreds = TextNowCreds(cfg['textnow']['username'], cfg['textnow']['sid'], cfg['textnow']['csrf'])

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
    activethreads = { # dictionary of active threads.
    }

    textnow.send('+16175059626', 'abSENT listener started!')
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
    saturday = 5
    sunday = 6
    holidays = []

    dailyCheckTimeStart = 7 # hour
    dailyCheckTimeEnd = 10 # hour
    
    resetTime = (0, 0) # midnight

    schoologySuccessCheck = False
    dayoffLatch = False
    while True:
        currentTime = datetime.now(timezone.utc) - timedelta(hours=5)
        currentDate = currentTime.strftime('%d/%m/%Y')
        dayOfTheWeek = currentTime.weekday()
        
        if dayOfTheWeek == saturday or dayOfTheWeek == sunday or currentDate in holidays:
            if dayoffLatch == False:
                logger.schoologyOffDay(currentDate)
                print("abSENT Day Off")
                dayoffLatch = True
        else:
            aboveStartTime: bool = currentTime.hour >= dailyCheckTimeStart
            belowEndTime: bool = currentTime.hour <= dailyCheckTimeEnde
            if aboveStartTime and belowEndTime and not schoologySuccessCheck:
                print("CHECKING SCHOOLOGY.")
                sc = SchoologyListener(textnowCreds, scCreds)
                schoologySuccessCheck = sc.run()
                print("CHECK COMPLETE.")
        
        if currentTime.hour == resetTime[0] and currentTime.minute == resetTime[1]:
            # Reset schoologySuccessCheck to false @ midnight
            # Only change value when it is latched (true)
            if schoologySuccessCheck == True:
                print("RESTART")
                logger.resetSchoologySuccessCheck()
                dayoffLatch = False
                schoologySuccessCheck = False
            
# Configure and start threads.
threads = {
        'sc': threading.Thread(target=threadwrapper(sc_listener), name='sc listener'),
        'sms': threading.Thread(target=threadwrapper(sms_listener), name='sms listener')
}

threads['sc'].start()
threads['sms'].start()