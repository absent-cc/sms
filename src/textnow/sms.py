import pytextnow
import time
import threading
from threading import Thread
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

    def listen(self):
        messages = []
        for msg in self.client.get_unread_messages():
            entry = msg
            messages.append(entry)
        return messages
    
    def mark_as_read(self, msg):
        msg.mark_as_read()
        return True

    def await_response(self, num):
        while True:

            unreads = []

            for msg in self.receive():
                if str(msg.number) in str(num):
                    unreads.append(msg)

            if len(unreads) == 0:
                time.sleep(0.2)
                continue
            return unreads[0]

class ui(Thread):

    def __init__(self, num: Number, creds: TextNowCreds, msg: Message):
        Thread.__init__(self)
        self.db = DatabaseHandler() 
        self.sms = sms(creds.sid, creds.csrf, creds.username)
        self.msg = msg
        self.num = num

    # Main function for SMS UI. Decides what other functions to call within the UI class based off of what the initial contact message is.

    def run(self):
        # Check if they are already subscribed.
        if self.msg.number in self.db.directory:
            # Cancellation
            if self.msg.content.lower() == "c":
                self.db.removeStudent(self.db.directory.directory[self.msg.number])
                self.sms.send(self.msg.number.number, "Service cancelled. Sorry to see you go!")
            # Editing
            elif self.msg.content.lower() == "e":
                self.edit(self.msg)
            # Neither
            else:
                self.sms.send(self.msg.number.number, "You are already subscribed. Text 'c' to cancel or 'e' to edit.")
        
        # If they aren't subscribed and would like to be, run the welcome function.
        elif self.msg.content.lower() == "subscribe":
            self.welcome(self.msg)
            pass
    
    # Takes a list of teacher names (both first and last within a string) ordered from A to G block, returns a Schedule object comprised of Teacher objects.

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
        
        if len(teachers) != 7:
            return False

        schedule=Schedule(teachers[0], teachers[1], teachers[2], teachers[3], teachers[4], teachers[5], teachers[6])
        return schedule

    # Welcome function for new users. Is called upon receipt of 'subscribe'.

    def welcome(self, msg):
        
        num = msg
        self.sms.send(num.number, "Welcome to abSENT - a monitoring system for the Newton Public Schools absent lists. Please text your first and last name, seperated by spaces.")

        # Get first and last name, as well as number.
        while True:
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
                self.sms.send(num.number, "You have entered invalid teacher names. Please correct this and try again")
                msg = self.sms.await_response(num.number).content
                msg = msg.split('\n') 

        # Define student object.
        student = Student(first,last,num.number,schedule)
        
        # Add student.
        self.db.addStudent(student)
        
        # Confirmation.
        self.sms.send(num.number, "Subscription complete. Welcome to abSENT!")
        self.sms.send(num.number, f"Here is your information. If anything is incorrect or if your schedule changes in the future, edit it by texting 'e'. {student.first} {student.last} @ {student.number}")
        self.sms.send(num.number, f"{student.schedule}")

    # Edit function for users who mispelled teacher names or wish to update their schedule term by term.

"""

    def edit(self, msg):

        # Preliminary.
        num = msg.number
        student = self.db.directory.directory[num]
        self.sms.send(num.number, "Thanks for using abSENT. I understand you'd like to edit your classes. Please respond with the block you'd like to change, any letter A to G.")
        msg = str(self.sms.await_response(num.number).content.upper())

        # Acquire block of teacher that is to be changed.
        while True:
            try:
                oldTeacher = getattr(student.schedule, msg)
                break;

            except AttributeError:
                self.sms.send(num.number, "That isn't a valid block. Please enter a letter from A to G.")
                msg = str(self.sms.await_response(num.number).content.upper())
        
        # Acquire name of teacher to be added.
        self.sms.send(num.number, f"Got it! You are no longer in {oldTeacher}'s class. Please tell me the first and last name of the teacher you now have, seperated by spaces.")
        msg = str(self.sms.await_response(num.number).content.lower())
        
        # Create teacher object and test if teacher name is valid.
        while True:
            try:
                msg = msg.split(' ')
                newTeacher = Teacher(msg[0],msg[1])
                break;
            except IndexError:
                self.sms.send(num.number, "The teacher name you provided is invalid. Please send the first and last name of the teacher desired, seperated by spaces.")
                msg = str(self.sms.await_response(num.number).content.lower())
        
        # Change class in DB and send confirmation.
        self.db.changeClass(student, oldTeacher, newTeacher)
        self.sms.send(num.number, "Confirmed! Your new schedule is as follows:")
        self.sms.send(num.number, f"{student.schedule}")


"""
