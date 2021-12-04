from schoology.absence import absence
from sms.sms import sms
import yaml
from datetime import datetime, timedelta

with open('secrets.yml', 'r') as f:
    cfg = yaml.safe_load(f)

sckeys = [cfg['north']['key'], cfg['south']['key']]
scsecrets = [cfg['north']['secret'], cfg['south']['secret']]
absent = absence(sckeys, scsecrets)

sms = sms(cfg['textnow']['sid'], cfg['textnow']['csrf'], cfg['textnow']['username'])

date = datetime.now() - timedelta(hours=24)
# date = datetime.datetime(2021, 12, 3)

test_arr = absent.filter_absences_north(date)

for i in test_arr:
    print(i)

sms.send('6175059626',"Text")