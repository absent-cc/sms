import time
import threading
from threading import Thread
from dataStructs import *
from database.dataBaseHandler import DatabaseHandler
from .sms import sms

class ui(Thread):

    def __init__(self, creds: TextNowCreds, msg: Message):
        Thread.__init__(self)
        self.db = DatabaseHandler() 
        self.sms = sms(creds.sid, creds.csrf, creds.username)
        self.msg = msg
        self.number = msg.number

    # Main function for SMS UI. Decides what other functions to call within the UI class based off of what the initial contact message is.

    def run(self):
        # Check if they are already subscribed.
        if str(self.number) in self.db.directory:
            # Cancellation
            if self.msg.content.lower() == "c":
                self.db.removeStudent(self.db.directory[str(self.number)])
                self.sms.send(str(self.number), "Service cancelled. Sorry to see you go!")
            # Editing
            elif self.msg.content.lower() == "e":
                #self.edit(self.msg)
                pass
            # Neither
            else:
                self.sms.send(str(self.number), "You are already subscribed. Text 'c' to cancel or 'e' to edit.")
        
        # If they aren't subscribed and would like to be, run the welcome function.
        elif self.msg.content.lower() == "subscribe":
            self.welcome(self.msg)
    
    # Creates schedule object

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
        
        number = msg.number
        self.sms.send(str(number), "Welcome to abSENT - a monitoring system for the Newton Public Schools absent lists. Please text your first and last name, seperated by spaces.")

        # Get first and last name, as well as number.
        while True:
            msg = str(self.sms.await_response(str(number)).content)
            msg = msg.split(' ')
            try:
                first = msg[0]
                last = msg[1]
                break;
            except IndexError:
                self.sms.send(str(number), "That's not a valid name. Enter your first and last name seperated by spaces.")
                continue

        # Get schedule
        self.sms.send(str(number), f"Hello {first} {last}! Please enter your teachers below, in order from A-Block to G-Block. Place each teacher on a new line. Use 'None' to represent free blocks.")
        msg = self.sms.await_response(str(number)).content
        msg = msg.split('\n')
                                                                                                                                                                                                                  
        # Define schedule.                                                                                                                                                                                        
        while True:                                                                                                                                                                                               
            schedule = self.gen_schedule(msg)                                                                                                                                                                     
            if schedule != False:                                                                                                                                                                                 
                break;                                                                                                                                                                                            
            else:                                                                                                                                                                                                 
                self.sms.send(str(number), "You have entered invalid teacher names. Please correct this and try again")                                                                                         
                msg = self.sms.await_response(str(number)).content                           
                msg = msg.split('\n')                                                                                                                                                                                                                                                                                                                                                                                               
        # Define student object.                                                                                                                                                                                  
        student = Student(first,last,number,schedule)                                                                                                                                                         
                                                                                                                                                          
        # Add student.                                                                                                                                                                                            
        self.db.addStudent(student)
        
        # Confirmation.
        self.sms.send(str(number), "Subscription complete. Welcome to abSENT!")
        self.sms.send(str(number), f"Here is your information. If anything is incorrect or if your schedule changes in the future, edit it by texting 'e'. {student.first} {student.last} @ {student.number}")
        self.sms.send(str(number), f"{student.schedule}")
