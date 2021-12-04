from schoology.absentTeacher import AbsentTeacher
import schoolopy
import yaml
from datetime import datetime, timedelta

class absence:

    # Sets up the two API objects as entries within a list 'api' . 

    def __init__(self, keys, secrets):
        self.keys = keys
        self.secrets = secrets
        self.api = ["",""]

        for i in range(2):
            self.api[i] = schoolopy.Schoology(schoolopy.Auth(self.keys[i],self.secrets[i]))
            self.api[i].limit = 10

    # Gets the feed, accepting an argument 'school' which is either 0 or 1, 0 corresponding to North and 1 corresponding to South (this value being the same as the school's index within the API array). Grabs all updates posted by individuals of interest and saves them to an array 'feed', and returns that array.

    def get_feed(self, school):
        teachers=["Tracy Connolly","Casey Friend","Suzanne Spirito"]
        feed = []
        for update in self.api[school].get_feed():
            user = self.api[school].get_user(update.uid)
            if user.name_display in teachers:
                feed.append(update.body)
        return feed

    # Gets the absence table for the date requested as defined by 'date'. Returns just this update for furthing processing. The date argument ultimately comes from the call of this function in main.py.

    def get_absences_table(self, date, school):
        feed = self.get_feed(school)
        current_table = None
        for update in feed:
            text = update.split("\n")
            # Table has historically had date on 4th column, used to differentiate between update and actual attendance table
            if len(text) > 4:
                if str(date.strftime("%m/%-d/%Y")) in text[3]:
                    current_table = update
                elif str(date.strftime('%b. %-d')) in text[0]:
                    current_table = update
        return current_table

    # Takes the raw North attendance table from the prior function and parses it, using the AbsentTeacher dataclass. Returns an array of entries utilizing this class. 

    def filter_absences_north(self, date):       
        absences = []

        raw = self.get_absences_table(date,0)
        if raw is None:
            return None
        else:
            raw = raw.split("\n")
            for i in range(12):
                raw.pop(0)
            for i in range(int(len(raw)/8)):
                if raw[i*8+3] == '':
                    note = None
                else:
                    note = raw[i*8+3]
                entry = AbsentTeacher(raw[i*8+2],raw[i*8+1],raw[i*8+4],str(date.strftime("%m/%-d/%Y")),note)
                absences.append(entry)        
        return absences
    
    # Same as the above, but the parsing is handled slightly differently due to the South absence table being differenct in formatting.

    def filter_absences_south(self, date):
        absences = []
             
        raw = self.get_absences_table(date,1)
        if raw is None:
            return None
        else:
            raw = raw.split("\r\n")
            for i in range(int(len(raw)/7)): 
                if raw[i*7+4] == '':
                    note = None
                else:
                    note = raw[i*7+4]
                entry = AbsentTeacher(raw[i*7+1],raw[i*7],raw[i*7+2],raw[i*7+3],note)              
                absences.append(entry)
        return absences

    def __str__(self):
        return "{} is absent because {}".format(self.name, self.reason)
