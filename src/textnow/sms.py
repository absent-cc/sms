import pytextnow
import time
from dataStructs import *


class sms:

    # "Logs" into API. In reality, each API request is simply using auth header. There is no concept of a session.

    def __init__(self, creds: TextNowCreds):
        self.client = pytextnow.Client(creds.username, sid_cookie=creds.sid, csrf_cookie=creds.csrf)

    # Sends a message.

    def send(self, num: str, message: str):
        self.client.send_sms(num, message)

    # Gets all unreads and marks them as read.

    def receive(self):
        unreads = []
        for msg in self.client.get_unread_messages():
            msg.mark_as_read()
            entry = Message(Number(msg.number),msg.content)
            unreads.append(entry)
        return unreads

    # Gets all unreads.

    def listen(self):
        messages = []
        for msg in self.client.get_unread_messages():
            entry = msg
            messages.append(entry)
        return messages
    
    # Marks a message as read.

    def markAsRead(self, msg):
        msg.mark_as_read()
        return True

    # Blocks and waits for a message from a specific number.

    def awaitResponse(self, num: Number):
        start_time = time.time()
        while True:
            # Timeout functionality.
            if start_time + 60 < time.time():
                return False

            unreads = []

            for msg in self.listen():
                if str(msg.number) in str(num):
                    unreads.append(Message(Number(msg.number),msg.content))
                    self.markAsRead(msg)
                    
            if len(unreads) == 0:
                time.sleep(0.2)
                continue
            return unreads[0]
