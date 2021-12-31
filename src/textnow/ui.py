import time
import threading
from threading import Thread
from dataStructs import *
from database.databaseHandler import DatabaseHandler
from textnow.controlPanel import ControlConsole
from .sms import SMS
from database.logger import Logger
from typing import Tuple

class UI(Thread):

    def __init__(self, textnowCreds: TextNowCreds, msg: Message):
        Thread.__init__(self)
        self.db = None
        self.sms = SMS(textnowCreds)
        self.msg = msg
        self.number = Number(msg.number)

        # Logginng:
        self.logger = Logger()

    # Main function for SMS UI. Decides what other functions to call within the UI class based off of what the initial contact message is.
    def run(self) -> bool: 
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
        alreadySubscribedMessage = "You are already subscribed. Type in 'HELP' to see a list of commands."
        timeoutMessage = "You timed out! Please start your task again."
        askForSubscription = "Hi! You've texted abSENT, an SMS based monitoring system for the NPS absent lists.\\nTo subscribe, please enter 'SUBSCRIBE'."

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
            'schedule': self.returnSchedule,
            'about': self.about,
            'help': self.help,
            'tos': self.returnTOS
        }

        # Check if response in responsesDict, if so run response function.
        if db != None:
            content = self.msg.content.lower()
            if content in responsesDict:
                response = responsesDict[content](db, resStudent)
                if not response:
                    self.sms.send(str(self.number), timeoutMessage)
                    return False
            elif content == 'admin':
                ControlPanel = ControlConsole(self.sms, self.msg)
                return True
            else:
                self.sms.send(str(self.number), alreadySubscribedMessage)
                return True
            
        # If they aren't subscribed and would like to be, run the welcome function.
        elif self.msg.content.lower() == "subscribe":
            welcome = self.welcome(self.msg)
            if not welcome:
                self.sms.send(str(self.number), timeoutMessage)
                return False
        else:
            self.sms.send(str(self.number), askForSubscription)

        return True

    # For new users, upon sending a subscribe message.
    def welcome(self, msg: Message) -> bool:
        # Sends welcome.
        welcomeMessage = "Welcome to abSENT - a monitoring system for the Newton Public Schools absent lists."

        self.sms.send(str(self.number), welcomeMessage)
        self.returnTOS(None, None)
        self.logger.accountSetupStarted(str(self.number))

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
        successMessageOne = f"Hi {name[0]}! You've sucessfully signed up! Here is your schedule:"
        successMessageTwo = f"ADV: {schedule[SchoolBlock.ADV]}\\nA: {schedule[SchoolBlock.A]}\\nB: {schedule[SchoolBlock.B]}\\nC: {schedule[SchoolBlock.C]}\\nD: {schedule[SchoolBlock.D]}\\nE: {schedule[SchoolBlock.E]}\\nF: {schedule[SchoolBlock.F]}\\nG: {schedule[SchoolBlock.G]}"
        successMessageThree = "If you have errors in your schedule, you can change it by texting 'EDIT'."
        successMessageFour = "Check out our site at beacons[.]ai/absent for more information or follow us on Instagram @nps_absent."
        successMessageFive = "Welcome to abSENT!"
        
        self.sms.send(str(self.number), successMessageOne) # Welcome
        time.sleep(3.75)
        self.sms.send(str(self.number), successMessageTwo) # Schedule
        time.sleep(5)
        self.sms.send(str(self.number), successMessageThree) # Edit
        time.sleep(3)
        self.sms.send(str(self.number), successMessageFour) # Edit
        self.sms.send(str(self.number), successMessageFive) # Welcome

        self.logger.accountSetupFinished(str(self.number))
        return True

    def help(self, db: DatabaseHandler, resStudent: Student) -> bool:
        helpMessage = "COMMANDS:\\n'SUBSCRIBE' to subscribe to abSENT.\\n'CANCEL' to cancel the service.\\n'EDIT' to edit your schedule.\\n'SCHEDULE' to view your schedule.\\n'ABOUT' to learn more about abSENT.\\n'TOS' to view our terms of service.\\n'HELP' to view this help message."
        self.sms.send(str(self.number), helpMessage)
        return True
    
    # Upon a cancel message.
    def cancel(self, db: DatabaseHandler, resStudent: Student) -> bool: 
        # Cancels and sends message.
        db.removeStudent(resStudent)
        self.logger.removedStudent(resStudent)
        cancelledMessage = "Service cancelled. Sorry to see you go!"
        self.sms.send(str(self.number), cancelledMessage)
        self.logger.canceledService(resStudent)
        return True

    # Upon an about request.
    def about(self, x, y) -> bool:
        # Sets message and sends.
        aboutMessage = "Visit us at beacons[.]ai/absent for more information or follow us on Instagram @nps_absent."
        self.sms.send(str(self.number), aboutMessage)
        return True

    # Upon an edit request.
    def edit(self, db: DatabaseHandler, resStudent: Student) -> bool:
        # A bunch of messages.
        initialMessage = "I see you'd like to edit your teachers. Please type the block you'd like to edit followed by your new teacher's name.\\nFor example: D John Doe. Alternatively, for a free block: D Free Block."
        invalidMessageTeacher = "You've provided an invalid teacher. Please restart the edit process."
        invalidMessageBlock = "You've entered an invalid block. Please restart the edit process."
        successMessage = "Great! Your schedule has been updated."

        self.sms.send(str(self.number), initialMessage)

        rawInput = self.sms.awaitResponse(str(self.number))

        # Check timeout.
        if rawInput == None:
            return False
        
        # SQL injection protection.
        if self.sqlInjectionCheck(rawInput):
            return False
        
        # Format input.
        teacherAttributes = rawInput.content.upper().split(" ", 2)

        # Check if teacher is good.
        if len(teacherAttributes) != 3:
            self.sms.send(str(self.number), invalidMessageTeacher)
            return False
    
        # Check if block is good.
        if teacherAttributes[0] not in ReverseBlockMapper():
            self.sms.send(str(self.number), invalidMessageBlock)
            return False
        
        school = resStudent.school
        block = teacherAttributes[0]
        first = teacherAttributes[1]
        last = teacherAttributes[2]
        teacher = Teacher(first, last, school)
        enumBlock = ReverseBlockMapper()[block]

        if teacher.first == "FREE" and teacher.last == "BLOCK":
            teacher = None

        db.changeClass(resStudent, enumBlock, teacher)
        self.logger.editSchedule(resStudent, enumBlock, teacher)

        self.sms.send(str(self.number), successMessage)
        self.returnSchedule(db, resStudent)
        return True
    
    # Upon a printSchedule request.
    def returnSchedule(self, db: DatabaseHandler, student: Student) -> bool:
        
        # Get the schedule.
        schedule = db.getScheduleByStudent(student)
        if schedule == None:
            return False

        # Messages.
        statusMessageOne = f"Your schedule is as follows:"
        statusMessageTwo = f"A: {schedule[SchoolBlock.A]}\\nADV: {schedule[SchoolBlock.ADV]}\\nB: {schedule[SchoolBlock.B]}\\nC: {schedule[SchoolBlock.C]}\\nD: {schedule[SchoolBlock.D]}\\nE: {schedule[SchoolBlock.E]}\\nF: {schedule[SchoolBlock.F]}\\nG: {schedule[SchoolBlock.G]}"
        
        # Send messages.
        self.sms.send(str(self.number), statusMessageOne)
        time.sleep(.05)
        self.sms.send(str(self.number), statusMessageTwo)

        return True
    
    # For use when parsing user input: checks if the names provided users are containing characters needed for SQL injection attacks.
    ## Returns true if invalid input
    ## Return false if valid input
    def sqlInjectionCheck(self, msg: Message) -> bool:
        
        # Message.  
        sqlInjectionMessage = "You are a filthy SQL injector. Please leave immediately."
        singleQuoteMessage = "You inputted an invalid single quote ('). Please try again."

        # Check for the invalid symbols, and send message if invalid symbol is used.
        if ';' in msg.content:
            self.sms.send(str(self.number), sqlInjectionMessage)
            self.logger.sqlInjectionAttempted(self.number)
            return True
        elif '\'' in msg.content:
            self.sms.send(str(self.number), singleQuoteMessage)
            self.logger.sqlInjectionAttempted(self.number)
            return True
        return False

    def getName(self) -> Tuple[str, str] or None:

        # Initial variables including messages and blank names.
        last = None
        first = None
        initialMessage = "Please text your first and last name, separated by spaces.\\n(e.g: John Doe)"
        invalidMessage = "That's not a valid name. Enter your first and last name separated by spaces."

        # Send initial message.
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
    
    # Get the school name of the user.
    def getSchool(self, name: Tuple[str, str]) -> SchoolName or None:
        
        # Initial vars, messages + blank school value.
        school = None
        initialMessage = f"Hello {name[0]}! Please enter the school you go to,\\n(N)orth or (S)outh."
        invalidMessage = "You've sent an invalid school name. Please reply with (N)orth or (S)outh."
        self.sms.send(str(self.number), initialMessage)
        
        # Main thread.
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
    
    # Get the grade of the user.
    def getYear(self) -> int or None:

        # Initial vars, including blank year value.
        year = None
        initialMessage = "Please enter your grade, a number from 9 to 12."
        invalidMessage = "That is not a valid grade number. Please enter a number from 9 to 12."
        validNumbers = {
            '9': 9,
            '10': 10,
            '11': 11,
            '12': 12
        }
        
        # Send initial message.
        self.sms.send(str(self.number), initialMessage)

        # Main thread.
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
    
    # By far the most complex function, generates a schedule object based off of user input which it grabs.
    def getSchedule(self, school: SchoolName) -> Schedule or None:

        # Temporary schedule dictionary.
        schedule = {
            SchoolBlock.A: set(),
            SchoolBlock.ADV: set(),
            SchoolBlock.B: set(),
            SchoolBlock.C: set(),
            SchoolBlock.D: set(),
            SchoolBlock.E: set(),
            SchoolBlock.F: set(),
            SchoolBlock.G: set()
        }

        # A bunch of messages.
        initialMessageOne = "Please send a new text message for each teacher that you have in the following format:"
        initialMessageTwo = "A First Last"
        initialMessageThree = "ADV John Doe"
        initialMessageFour = "B Joe Mama"
        initialMessageFive = "When done, text 'DONE'. For free blocks, don't send a message at all."
        initialMessageSix = "For help with this process, check out our getting started post on our Instagram: @nps_absent."
        invalidMessageTeacher = "Please type that teacher's name again. You used the wrong formatting."
        invalidMessageBlock = "Please correct your block formatting. It is invalid."
        invalidMessageNewline = "You've put more than one teacher in this message. Please send a new text message for each teacher."

        # Send initial messages.
        self.sms.send(str(self.number), initialMessageOne)
        self.sms.send(str(self.number), initialMessageTwo)
        self.sms.send(str(self.number), initialMessageThree)
        self.sms.send(str(self.number), initialMessageFour)
        self.sms.send(str(self.number), initialMessageFive)
        self.sms.send(str(self.number), initialMessageSix)

        # Get sms.
        rawInput = self.sms.awaitResponse(self.number)
        # Check for timeout.
        if rawInput == None:
            return None
        content = rawInput.content.upper()

        # Main thread.
        while content != "DONE":
            # Obligatory SQL injection.
            if self.sqlInjectionCheck(rawInput):
                return None
            
            # No newlines.
            if "\n" in content:
                self.sms.send(str(self.number), invalidMessageNewline) # Tell user they have more than one teacher.
                rawInput = self.sms.awaitResponse(self.number)
                # Check for timeout.
                if rawInput == None:
                    return None
                content = rawInput.content.upper()
                continue

            # Split up the content got from the user.
            teacherAttributes = content.split(" ", 2)
            
            # Check if teacher is good.
            if len(teacherAttributes) != 3:
                self.sms.send(str(self.number), invalidMessageTeacher)
                rawInput = self.sms.awaitResponse(self.number)
                # Check for timeout.
                if rawInput == None:
                    return None
                content = rawInput.content.upper()
                continue

            # Check if block is good.
            if teacherAttributes[0] not in ReverseBlockMapper():
                self.sms.send(str(self.number), invalidMessageBlock)
                rawInput = self.sms.awaitResponse(self.number)
                # Check for timeout.
                if rawInput == None:
                    return None
                content = rawInput.content.upper()
                continue
            
            # Creates a teacher object.
            block = teacherAttributes[0]
            first = teacherAttributes[1]
            last = teacherAttributes[2]
            teacher = Teacher(first, last, school)
            enumBlock = ReverseBlockMapper()[block]

            # Adds the teacher object to dict of block: set(teacher)
            schedule[enumBlock].add(teacher)
            
            rawInput = self.sms.awaitResponse(self.number)
            # Check for timeout.
            if rawInput == None:
                return None
            content = rawInput.content.upper()
        
        scheduleClass = Schedule()

        for block in schedule:
            if schedule[block] != set():
                scheduleClass[block] = schedule[block]

        return scheduleClass

    def returnTOS(self, x, y) -> bool:
        # Vars.
        message = "By signing up for and continuing to use our service, you implicity agree to the terms outlined at the following link:\\nabsent[.]igneus[.]org/terms"
        # Send links to TOS.
        self.sms.send(str(self.number), message)
        return True