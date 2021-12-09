import pytextnow
import time
from dataStructs import *

class sms:

    def __init__(self, creds: TextNowCreds):
        self.client = pytextnow.Client(creds.username, sid_cookie=creds.sid, csrf_cookie=creds.csrf)

    def send(self, num: int, message: str):
        self.client.send_sms(num, message)

    def receive(self):
        unreads = []
        for msg in self.client.get_unread_messages():
            msg.mark_as_read()
            entry = Message(Number(msg.number),msg.content)
            unreads.append(entry)
        return unreads

    def listen(self):
        messages = []
        for msg in self.client.get_unread_messages():
            entry = msg
            messages.append(entry)
        return messages
    
    def mark_as_read(self, msg):
        msg.mark_as_read()
        return True

    def await_response(self, num: Number):
        start_time = time.time()
        while True:
            # Timeout functionality.
            if start_time + 60 < time.time():
                return False

            unreads = []

            for msg in self.receive():
                if str(msg.number) in str(num):
                    unreads.append(msg)

            if len(unreads) == 0:
                time.sleep(0.2)
                continue
            return unreads[0]
