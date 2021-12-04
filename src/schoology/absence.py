from absentTeacher import AbsentTeacher
import schoolopy
import yaml
import webbrowser as wb
import json
from datetime import date

class absence:
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.sc = schoolopy.Schoology(schoolopy.Auth(self.key, self.secret))
        self.sc.limit = 10

    def get_feed(self, teachers=["Tracy Connolly","Casey Friend","Suzanne Spirito"]):
        feed = []
        for update in self.sc.get_feed():
            user = self.sc.get_user(update.uid)
            if user.name_display == teachers[0] or user.name_display == teachers[1] or user.name_display == teachers[2]:
                feed.append(update.body)
        return feed

    def get_absences_table(self, date: date):
        feed = self.get_feed()
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

    def filter_absences_north(self, date: date):
        absences = []

        raw = self.get_absences_table(date)
        raw = raw.split("\n")

        for i in range(12):
            raw.pop(0)
        
        if raw is None:
            return None
        else:
            for i in range(int(len(raw)/8)):
                if raw[i*8+3] == '':
                    note = None
                else:
                    note = raw[i*8+3]

                entry = AbsentTeacher(raw[i*8+2],raw[i*8+1],raw[i*8+4],None,note)
                absences.append(entry)
        
        return absences

    def filter_absences(self, date: date):
        absences = []
             
        raw = self.get_absences_table(date)
        raw = raw.split("\r\n")
        
        if raw is None:
            return None
        else:
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
