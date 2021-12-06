i        teachers = []
        for teacher in msg:
            if teacher == 'None':
                teacher = None
                teachers.append(teacher)
                continue
            teacher = teacher.split(' ')
            teacher = Teacher(teacher[0],teacher[1])
            teachers.append(teacher)
        
        schedule=Schedule(teachers[0],teachers[1],teachers[2],teachers[3],teachers[4],teachers[5],teachers[6])mport pytextnow
import time
from dataStructs import *
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

    def await_response(self, num):
        while True:

            unreads = []

            for msg in self.receive():
                if str(msg.number) in str(num):
                    unreads.append(msg)

            if len(unreads) == 0:
                time.sleep(0.2)
                continue
            print("el fin")
            return unreads[0]

class ui:

    def __init__(self, sms):
        self.db = DatabaseHandler() 
        self.sms = sms

    def main(self, msg):
        if msg.number in self.db.directory.directory:
            if msg.content.lower() == "c":
                self.sms.send(msg.number.number, "Service cancelled. Sorry to see you go!")
            elif msg.content.lower() == "e":
                self.edit(msg)
        
        if msg.content.lower() == "subscribe":
            self.welcome(msg)
            pass
    
    def gen_schedule(self, raw):

        teachers = []
        for teacher in raw:
            if teacher == 'None':
                teacher = None
                teachers.append(teacher)
                continue
            teacher = teacher.split(' ')
            teacher = Teacher(teacher[0],teacher[1])
            teachers.append(teacher)
        
        schedule=Schedule(teachers[0],teachers[1],teachers[2],teachers[3],teachers[4],teachers[5],teachers[6])
        return schedule

    def welcome(self, msg):
        
        # Get first and last name, as well as number.

        num = msg.number

        self.sms.send(num.number, "Welcome to abSENT - a monitoring system for the Newton Public Schools absent lists. Please text your first and last name, seperated by spaces.")
        msg = str(self.sms.await_response(msg.number).content)
        msg = msg.split(' ')
        first = msg[0]
        last = msg[1]
        
        # Get schedule

        self.sms.send(num.number, f"Hello {first} {last}! Please enter your teachers below, in order from A-Block to G-Block. Place each teacher on a new line. Use 'None' to represent free blocks.")
        msg = self.sms.await_response(num.number).content
        msg = msg.split('\n')

        # Define schedule.
        
        schedule = self.gen_schedule(msg)

        # Define student object.

        student = Student(first,last,num,schedule)
        
        print(student)

        pass
    
    def edit(self, msg):
        pass
