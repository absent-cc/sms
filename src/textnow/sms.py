import pytextnow
from dataStructs import Number, Message
from database.dataBaseHandler import DatabaseHandler

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

    def gen_response(self, msg):
        response = False
        print(str(msg.content.lower()))
        if msg.content.lower() in 'c':
            response = "Service cancelled! Sorry to see you go."
        elif msg.content.lower() in 'e':
            response = "something something edit something"
        elif msg.number in self.db.directory.directory:
            response = "You are already subscribed to our service! Respond 'c' to cancel or 'e' to edit your schedule."
        
        if msg.content.lower() == 'subscribe':
            response = "something something subcribe"
        return response
