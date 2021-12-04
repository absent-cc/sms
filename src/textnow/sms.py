import pytextnow

class sms:

    def __init__(self, sid, csrf, username):
        self.client = pytextnow.Client(username, sid_cookie=sid, csrf_cookie=csrf)

    def send(self, num, message):
        self.client.send_sms(num, message)

    def receive(self):
        unreads = self.client.get_unread_messages()
        for msg in unreads:
            msg.mark_as_read()
        return unreads
