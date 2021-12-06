from schoology.absence import absence
from textnow.sms import sms, ui
import yaml
from datetime import datetime, timedelta
from database.dataBaseHandler import DatabaseHandler
from dataStructs import *
import time

with open('secrets.yml', 'r') as f:
    cfg = yaml.safe_load(f)

sckeys = [cfg['north']['key'], cfg['south']['key']]
scsecrets = [cfg['north']['secret'], cfg['south']['secret']]
absent = absence(sckeys, scsecrets)

sid = cfg['textnow']['sid']
csrf = cfg['textnow']['csrf']
username = cfg['textnow']['username']

sms = sms(sid,csrf,username)
ui = ui(sms)
db = DatabaseHandler()

date = datetime.now() - timedelta(hours=5)
# date = datetime.datetime(2021, 12, 3)

test_arr = absent.filter_absences_north(date)

for i in test_arr:
    print(i)

#sms.send('6175059626',"Text")

#test_num = Number("6175525098")
#test_teacher = Teacher("Kevin", "Yang")
#test_schedule = Schedule(test_teacher, test_teacher, test_teacher, test_teacher, test_teacher, test_teacher, None)

#test_student1 = Student("Roshan", "Karim", test_num, test_schedule)
#db.addStudentToDirectory(test_student1)

#print(db.classes.classes)
#print(db.directory.directory)

#while True:
#    for msg in sms.receive():
#        ui.main(msg)
#    time.sleep(0.2)
#for i in sms.receive():
#    print(ui.gen_response(i))
