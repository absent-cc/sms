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

date = datetime.now() - timedelta(hours=5)

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

def sms_listener():
    
    txt = sms(sid, csrf, username)
    txtui = ui(txt) 

    while True:
        for msg in txt.receive():
            print(msg)
            txtui.main(msg)
            time.sleep(0.2)

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

#threads = {
#        'sc': threading.Thread(target=threadwrapper(sc_listener), name='sc listener'),
#        'sms': threading.Thread(target=threadwrapper(sms_listener), name='sms listener')
#}

rknum = Number('+16175059626')
creds = TextNowCreds(username, sid, csrf)

msg = Message("+16175059626",'Subscribe')

th = ui(rknum, creds, msg)
th.start()

for i in range(50000):
    print('please make the pain stop')
    time.sleep(1)

th.join()

#threads['sms'].start()
#threads['sc'].start()
