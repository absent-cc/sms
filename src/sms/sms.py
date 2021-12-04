import pytextnow

class sms:

    def __init__(sid, csrf, username):
        self.sid = sid
        self.csrf = csrf
        self.username = username
        self.client = client = pytextnow.Client(csrf.username, sid_cookie=self.sid, csrf_cookie=self.csrf)

    def send(num, message):
        self.client.send_sms(num, message)
