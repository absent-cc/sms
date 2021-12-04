from absence import absence
import schoolopy
import yaml
from datetime import date

with open('secrets.yml', 'r') as f:
    cfg = yaml.safe_load(f)

absent = absence(cfg['key'], cfg['secret'])

print(absent.filter_absences_north(date = date.today()))
print(absent.filter_absences(date = date.today()))
