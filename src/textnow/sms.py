import pytextnow
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
                self.db.removeStudent(self.db.directory.directory[msg.number])
                self.sms.send(msg.number.number, "Service cancelled. Sorry to see you go!")
            elif msg.content.lower() == "e":
                self.edit(msg)
            else:
                self.sms.send(msg.number.number, "You are already subscribed. Text 'c' to cancel or 'e' to edit.")
        
        elif msg.content.lower() == "subscribe":
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
            try:
                teacher = Teacher(teacher[0],teacher[1])
            except IndexError:
                return False
            teachers.append(teacher)
        
        for teacher in teachers:
            if teacher not in self.db.classes.classes:
                self.db.addTeacher(teacher)

        schedule=Schedule(teachers[0],teachers[1],teachers[2],teachers[3],teachers[4],teachers[5],teachers[6])
        return schedule

    def welcome(self, msg):
        
        num = msg.number
        self.sms.send(num.number, "Welcome to abSENT - a monitoring system for the Newton Public Schools absent lists. Please text your first and last name, seperated by spaces.")

        while True:
            # Get first and last name, as well as number.

            msg = str(self.sms.await_response(num.number).content)
            msg = msg.split(' ')
            try:
                first = msg[0]
                last = msg[1]
                break;
            except IndexError:
                self.sms.send(num.number, "That's not a valid name. Enter your first and last name seperated by spaces.")
                continue
        
        # Get schedule

        self.sms.send(num.number, f"Hello {first} {last}! Please enter your teachers below, in order from A-Block to G-Block. Place each teacher on a new line. Use 'None' to represent free blocks.")
        msg = self.sms.await_response(num.number).content
        msg = msg.split('\n')

        # Define schedule.
        while True:
            schedule = self.gen_schedule(msg)
            if schedule != False:
                break;
            else:
                self.sms.send(num.number, f"You have entered invalid teacher names. Please correct this and try again")
                msg = self.sms.await_response(num.number).content
                msg = msg.split('\n') 

        # Define student object.

        student = Student(first,last,num,schedule)
        
        # Add student.
        self.db.addStudent(student)
        
        # Confirmation.
        self.sms.send(num.number, f"Subscription complete. Welcome to abSENT!")
        self.sms.send(num.number, f"Here is your information. If anything is incorrect or if your schedule changes in the future, edit it by texting 'e'. {student.first} {student.last} @ {student.number}")
        self.sms.send(num.number, f"{student.schedule}")

    def edit(self, msg):
        pass
