from database.sqlite import databaseHandler
from test_sqlite import *

test = databaseHandler()
print(test.get_all_data())