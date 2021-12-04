from absence import absence
import schoolopy
import yaml
from datetime import datetime, timedelta

with open('secrets.yml', 'r') as f:
    cfg = yaml.safe_load(f)

keys = [cfg['north']['key'], cfg['south']['key']]
secrets = [cfg['north']['secret'], cfg['south']['secret']]
absent = absence(keys, secrets)

date = datetime.now() - timedelta(hours=5)

print(absent.filter_absences_north(date))
print(absent.filter_absences_south(date))
