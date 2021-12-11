import time
import threading
from threading import Thread
from dataStructs import *
from database.databaseHandler import DatabaseHandler
from .sms import sms

class ui(Thread):

    def __init__(self, creds: TextNowCreds, msg: Message):
        Thread.__init__(self)
        self.db = None
        self.sms = sms(creds)
        self.msg = msg
        self.number = msg.number

    # Main function for SMS UI. Decides what other functions to call within the UI class based off of what the initial contact message is.

    def run(self):
        
        # Creates temporary DBs.
        dbNorth = DatabaseHandler(SchoolNameMapper()['NNHS'])
        dbSouth = DatabaseHandler(SchoolNameMapper()['NSHS'])

        # Creates "fake" student with just number.
        psuedoStudent = Student(str(self.number), None, None, None, None)

        # Checks if student number exists in DB.
        resNorth = dbNorth.getStudent(psuedoStudent)
        resSouth = dbSouth.getStudent(psuedoStudent)
        db = None

        # Sets the correct DB for the student if they exist.
        if resNorth != None:
            db = dbNorth
            resStudent = resNorth
        elif resSouth != None:
            db = dbSouth
            resStudent = resSouth
        
        if db != None:
            # Cancellation
            if self.msg.content.lower() == "c":
                db.removeStudentFromStudentDirectory(psuedoStudent)
                self.sms.send(str(self.number), "Service cancelled. Sorry to see you go!")
            # Editing
            elif self.msg.content.lower() == "e":
                self.edit(self.msg, db, resStudent)
            # Neither
            else:
                self.sms.send(str(self.number), "You are already subscribed. Text 'c' to cancel or 'e' to edit.")
            
        # If they aren't subscribed and would like to be, run the welcome function.
        elif self.msg.content.lower() == "subscribe":
             self.welcome(self.msg)

    def welcome(self, msg: Message):

        # Defines number and sends welcome.
        number = Number(msg.number)
        welcomeMessage = "Welcome to abSENT - a monitoring system for the Newton Public Schools absent lists."

        self.sms.send(str(number), welcomeMessage)

        # Gets names.
        name = self.getName(number)

        # Get school, make DB.
        school = self.getSchool(number, name)
        db = DatabaseHandler(school)

        # Get grade.
        grade = self.getYear(number)
        
        # Get schedule.
        schedule = self.getSchedule(number, school)

        # Create student.
        student = Student(number, name[0], name[1], school, grade)

        # Add student to DB.
        db.addStudent(student, schedule)

        # Confirmation message.
        successMessageOne = f"Great! You've signed up sucessfully. Here is your schedule:"
        successMessageTwo = str(schedule)
        successMessageThree = "Make any edits by texting the letter 'e'."
        successMessageFour = f"Welcome to abSENT, {name[0]} {name[1]}!"

        self.sms.send(str(number), successMessageOne)
        self.sms.send(str(number), successMessageTwo)
        self.sms.send(str(number), successMessageThree)
        self.sms.send(str(number), successMessageFour)

    def edit(self, msg: Message, db: DatabaseHandler, resStudent: Student):

        # A bunch of messages.
        initialMessageOne = "I see you'd like to edit your teachers. Please type the block you'd like to edit, a single letter from A to G, followed by your new teacher's name."
        initialMessageTwo = "For example: D John Doe"
        invalidMessageTeacher = "You have provided an invalid teacher. Please restart the edit process."
        invaldMessageBlock = "You have entered an invalid block. Please restart the edit process."
        successMessage = "Great! Your schedule has been updated."

        self.sms.send(str(msg.number), initialMessageOne)
        self.sms.send(str(msg.number), initialMessageTwo)

        rawInput = self.sms.awaitResponse(str(msg.number))
        rawInput = rawInput.content.upper()
        teacherAttributes = rawInput.split(" ", 2)

        # Check if teacher is good.
        if len(teacherAttributes) != 3:
            sms.send(str(number), invalidMessageTeacher)
            return False
    
        # Check if block is good.
        if teacherAttributes[0] not in ReverseBlockMapper():
            sms.send(str(number), invalidMessageBlock)
            return False
        
        school = resStudent.school
        block = teacherAttributes[0]
        first = teacherAttributes[1]
        last = teacherAttributes[2]
        teacher = Teacher(first, last, school)
        enumBlock = ReverseBlockMapper()[block]

        db.changeClass(resStudent, enumBlock, teacher)

    def getName(self, number: Number):

        last = None
        first = None

        initialMessage = "Please text your first and last name, seperated by spaces."
        invalidMessage = "That's not a valid name. Enter your first and last name seperated by spaces."
        self.sms.send(str(number),initialMessage)

        # Test name, return name if tests correctly.
        while last == None or first == None:
            msg = self.sms.awaitResponse(str(number))
            
            # Check for timeout.
            if msg == False:
                return False

            # Split name and check if valid.
            msg = str(msg.content).split(' ', 1) 
            if len(msg) == 2:
                first = msg[0]
                last = msg[1] 
            else:
                self.sms.send(str(number), invalidMessage)
        
        return (first, last)
    
    def getSchool(self, number: Number, name: tuple):

        school = None

        initialMessage = f"Hello {name[0]} {name[1]}! Please enter the school you go to, (N)orth or (S)outh."
        invalidMessage = "You have sent an invalid school name. Please reply with (N)orth or (S)outh."
        self.sms.send(str(number),initialMessage)
        
        while school == None:
            msg = self.sms.awaitResponse(str(number))
            
            # Check for timeout.
            if msg == False:
                return False
            msg = msg.content.lower()

            # Check if school name is valid.
            if msg == 'north' or msg == 'n':
                school = SchoolNameMapper()["NNHS"]          
            elif msg == 'south' or msg == 's':
                school = SchoolNameMapper()["NSHS"]
            else:
                self.sms.send(str(number),invalidMessage)
        
        return school
    
    def getYear(self, number: Number):

        year = None

        initialMessage = "Please enter your grade, a number from 9 to 12."
        invalidMessage = "That is not a valid grade number. Please enter a number from 9 to 12."
        
        validNumbers = {
            '9': 9,
            '10': 10,
            '11': 11,
            '12': 12
        }

        self.sms.send(str(number),initialMessage)

        while year == None:
            msg = self.sms.awaitResponse(str(number))

            # Check for timeout.
            if msg == False:
                return False
            msg = msg.content

            if validNumbers.get(msg) != None:
                year = validNumbers.get(msg)
            else:
                self.sms.send(str(number),invalidMessage)

        return year

    def getSchedule(self, number: Number, school: SchoolName):

        initialMessageOne = "Please enter each of your teachers in a new message, in this format:"
        initialMessageTwo = "A John Doe"
        initialMessageThree = "B Joe Mama"
        invalidMessageTeacher = "Please type that teacher's name again. You used the wrong formatting."
        invalidMessageBlock = "Please correct your block formatting. It is invalid."

        # Send initial messages.
        self.sms.send(str(number), initialMessageOne)
        self.sms.send(str(number), initialMessageTwo)
        self.sms.send(str(number), initialMessageThree)

        schedule = Schedule()

        rawInput = self.sms.awaitResponse(number)
        rawInput = rawInput.content.upper()
        while rawInput != "DONE":
            teacherAttributes = rawInput.split(" ", 2)

            # Check if teacher is good.
            if len(teacherAttributes) != 3:
                sms.send(str(number), invalidMessageTeacher)
                continue
            # Check if block is good.
            if teacherAttributes[0] not in ReverseBlockMapper():
                sms.send(str(number), invalidMessageBlock)
                continue
            
            block = teacherAttributes[0]
            first = teacherAttributes[1]
            last = teacherAttributes[2]
            teacher = Teacher(first, last, school)
            enumBlock = ReverseBlockMapper()[block]
            schedule[enumBlock] = teacher

            rawInput = self.sms.awaitResponse(number).content.upper()

        return schedule



