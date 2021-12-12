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
        self.number = Number(msg.number)

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

        # Creates messages
        alreadySubscribedMessage = "You are already subscribed. Enter 'CANCEL' to cancel the service, 'EDIT' to edit your schedule, or 'STATUS' to view your schedule. To learn more about how we made it happen, enter 'ABOUT'."
        timeoutMessage = "You timed out! Start the process again by entering 'SUBSCRIBE'."
        askForSubscription = "You have texting the phone number of abSENT, a monitoring system for the NPS absent lists. To subscribe, please enter 'SUBSCRIBE'."

        # Sets the correct DB for the student if they exist.
        if resNorth != None:
            db = dbNorth
            resStudent = resNorth
        elif resSouth != None:
            db = dbSouth
            resStudent = resSouth
        
        # Dict of MSG: Response
        responsesDict = {
            'cancel': self.cancel,
            'edit': self.edit,
            'status': self.status,
            'about': self.about
        }

        if db != None:
            content = self.msg.content.lower()
            if content in responsesDict:
                responsesDict[content](db, resStudent)
            else:
                self.sms.send(str(self.number), alreadySubscribedMessage)
            
        # If they aren't subscribed and would like to be, run the welcome function.
        elif self.msg.content.lower() == "subscribe":
            welcome = self.welcome(self.msg)
            if not welcome:
                self.sms.send(str(self.number), timeoutMessage)
        else:
            self.sms.send(str(self.number), askForSubscription)

    def welcome(self, msg: Message):

        # Sends welcome.
        welcomeMessage = "Welcome to abSENT - a monitoring system for the Newton Public Schools absent lists."

        self.sms.send(str(self.number), welcomeMessage)

        # Gets names.
        name = self.getName()
        if name == None:
            return False

        # Get school, make DB.
        school = self.getSchool(name)
        if school == None:
            return False
        db = DatabaseHandler(school)

        # Get grade.
        grade = self.getYear()
        if grade == None:
            return False
        
        # Get schedule.
        schedule = self.getSchedule(school)
        if schedule == None:
            return False

        # Create student.
        student = Student(self.number, name[0], name[1], school, grade)
        if student == None:
            return False

        # Add student to DB.
        db.addStudent(student, schedule)

        # Confirmation message.
        successMessageOne = "Great! You've signed up sucessfully. Here is your schedule"
        successMessageTwo = f"A: {schedule[SchoolBlock.A]}, B: {schedule[SchoolBlock.B]}, C: {schedule[SchoolBlock.C]}, D: {schedule[SchoolBlock.D]}, E: {schedule[SchoolBlock.E]}, F: {schedule[SchoolBlock.F]}, G: {schedule[SchoolBlock.G]}"
        successMessageThree = "Make any edits by entering 'EDIT'."
        successMessageFour = f"Welcome to abSENT, {name[0]} {name[1]}!"

        self.sms.send(str(self.number), successMessageOne)
        self.sms.send(str(self.number), successMessageTwo)
        self.sms.send(str(self.number), successMessageThree)
        self.sms.send(str(self.number), successMessageFour)

        return True

    def cancel(self, db: DatabaseHandler, resStudent: Student):
        
        # Cancels and sends message.
        db.removeStudentFromStudentDirectory(resStudent)
        cancelledMessage = "Service cancelled. Sorry to see you go!"
        self.sms.send(str(self.number), cancelledMessage)

        return True

    def about(self, x, y):

        # Sets message and sends.
        aboutMessage = "Visit https://github.com/bykevinyang/abSENT to learn more about abSENT. abSENT is developed by Roshan Karim and Kevin Yang, students at North and South respectively."
        self.sms.send(str(self.number), aboutMessage)

        return True

    def edit(self, db: DatabaseHandler, resStudent: Student):

        # A bunch of messages.
        initialMessageOne = "I see you'd like to edit your teachers. Please type the block you'd like to edit, a single letter from A to G, followed by your new teacher's name."
        initialMessageTwo = "For example: D John Doe"
        invalidMessageTeacher = "You have provided an invalid teacher. Please restart the edit process."
        invaldMessageBlock = "You have entered an invalid block. Please restart the edit process."
        successMessage = "Great! Your schedule has been updated."

        self.sms.send(str(self.number), initialMessageOne)
        self.sms.send(str(self.number), initialMessageTwo)

        rawInput = self.sms.awaitResponse(str(self.number))

        # Check timeout.
        if rawInput == None:
            return False

        # Format input.
        rawInput = rawInput.content.upper()
        teacherAttributes = rawInput.split(" ", 2)

        # Check if teacher is good.
        if len(teacherAttributes) != 3:
            sms.send(str(self.number), invalidMessageTeacher)
            return False
    
        # Check if block is good.
        if teacherAttributes[0] not in ReverseBlockMapper():
            sms.send(str(self.number), invalidMessageBlock)
            return False
        
        school = resStudent.school
        block = teacherAttributes[0]
        first = teacherAttributes[1]
        last = teacherAttributes[2]
        teacher = Teacher(first, last, school)
        enumBlock = ReverseBlockMapper()[block]

        db.changeClass(resStudent, enumBlock, teacher)
        self.sms.send(str(self.number), successMessage)

        return True

    def status(self, db: DatabaseHandler, student: Student):
        
        # Get the schedule.
        schedule = db.getScheduleByStudent(student)
        if schedule == None:
            return False

        # Messages.
        statusMessageOne = f"Your schedule is as follows:"
        statusMessageTwo = f"A: {schedule[SchoolBlock.A]}, B: {schedule[SchoolBlock.B]}, C: {schedule[SchoolBlock.C]}, D: {schedule[SchoolBlock.D]}, E: {schedule[SchoolBlock.E]}, F: {schedule[SchoolBlock.F]}, G: {schedule[SchoolBlock.G]}"
        
        # Send messages.
        self.sms.send(str(self.number), statusMessageOne)
        self.sms.send(str(self.number), statusMessageTwo)

        return True

    def sqlInjectionCheck(self, msg: Message):

        sqlInjectionMessage = "You are a filthy SQL injector. Please leave immediately."
    
        if '\'' in msg.content or ';' in msg.content:
            self.sms.send(str(self.number), sqlInjectionMessage)
            return True
        else:
            return False

    def getName(self):

        last = None
        first = None

        initialMessage = "Please text your first and last name, seperated by spaces."
        invalidMessage = "That's not a valid name. Enter your first and last name seperated by spaces."

        self.sms.send(str(self.number), initialMessage)

        # Test name, return name if tests correctly.
        while last == None or first == None:
            msg = self.sms.awaitResponse(str(self.number))
            
            # Check for timeout.
            if msg == None:
                return None
            
            # Obligatory SQL injection.
            if self.sqlInjectionCheck(msg):
                return None

            # Split name and check if valid.
            msg = str(msg.content).split(' ', 1) 
            if len(msg) == 2:
                first = msg[0]
                last = msg[1] 
            else:
                self.sms.send(str(self.number), invalidMessage)
        
        return (first, last)
    
    def getSchool(self, name: tuple):

        school = None

        initialMessage = f"Hello {name[0]} {name[1]}! Please enter the school you go to, (N)orth or (S)outh."
        invalidMessage = "You have sent an invalid school name. Please reply with (N)orth or (S)outh."
        self.sms.send(str(self.number), initialMessage)
        
        while school == None:
            msg = self.sms.awaitResponse(str(self.number))
            
            # Check for timeout.
            if msg == None:
                return None
            msg = msg.content.lower()

            # Check if school name is valid.
            if msg == 'north' or msg == 'n':
                school = SchoolNameMapper()["NNHS"]          
            elif msg == 'south' or msg == 's':
                school = SchoolNameMapper()["NSHS"]
            else:
                self.sms.send(str(self.number), invalidMessage)
        
        return school
    
    def getYear(self):

        year = None

        initialMessage = "Please enter your grade, a number from 9 to 12."
        invalidMessage = "That is not a valid grade number. Please enter a number from 9 to 12."
        
        validNumbers = {
            '9': 9,
            '10': 10,
            '11': 11,
            '12': 12
        }

        self.sms.send(str(self.number), initialMessage)

        while year == None:
            msg = self.sms.awaitResponse(str(self.number))

            # Check for timeout.
            if msg == None:
                return None
            msg = msg.content

            if validNumbers.get(msg) != None:
                year = validNumbers.get(msg)
            else:
                self.sms.send(str(self.number), invalidMessage)

        return year

    def getSchedule(self, school: SchoolName):

        initialMessageOne = "Please enter each of your teachers in a new message, in this format:"
        initialMessageTwo = "A John Doe"
        initialMessageThree = "B Joe Mama"
        invalidMessageTeacher = "Please type that teacher's name again. You used the wrong formatting."
        invalidMessageBlock = "Please correct your block formatting. It is invalid."

        # Send initial messages.
        self.sms.send(str(self.number), initialMessageOne)
        self.sms.send(str(self.number), initialMessageTwo)
        self.sms.send(str(self.number), initialMessageThree)

        schedule = Schedule()

        rawInput = self.sms.awaitResponse(self.number)
        content = rawInput.content.upper()

        while content != "DONE":
            
            # Obligatory SQL injection.
            if self.sqlInjectionCheck(rawInput):
                return None

            teacherAttributes = content.split(" ", 2)
            
            # Check if teacher is good.
            if len(teacherAttributes) != 3:
                self.sms.send(str(self.number), invalidMessageTeacher)
                rawInput = self.sms.awaitResponse(self.number)
                content = rawInput.content.upper()
                continue
            # Check if block is good.
            if teacherAttributes[0] not in ReverseBlockMapper():
                self.sms.send(str(self.number), invalidMessageBlock)
                rawInput = self.sms.awaitResponse(self.number)
                content = rawInput.content.upper()
                continue
            
            block = teacherAttributes[0]
            first = teacherAttributes[1]
            last = teacherAttributes[2]
            teacher = Teacher(first, last, school)
            enumBlock = ReverseBlockMapper()[block]
            schedule[enumBlock] = teacher

            rawInput = self.sms.awaitResponse(self.number)
            content = rawInput.content.upper()

        return schedule



