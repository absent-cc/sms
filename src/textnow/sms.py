import pytextnow
from dataStructs import Number, Message
from ..database.databaseHandler import DatabaseHandler

class sms:

    def __init__(self, sid, csrf, username):
        self.client = pytextnow.Client(username, sid_cookie=sid, csrf_cookie=csrf)

    def send(self, num, message):
        self.client.send_sms(num, message)

    def receive(self):
        unreads = []
        for msg in self.client.get_unread_messages():
            msg.mark_as_read()
            entry = Message(Number(msg.number),msg.content)
            unreads.append(entry)

        return unreads

class ui:

    def __init__(self):
        self.db = DatabaseHandler() 

    def gen_response(self, unreads):
        for msg in unreads:
            if msg.number in db.directory()
