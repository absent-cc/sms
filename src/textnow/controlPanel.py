import time
from threading import Thread
from dataStructs import *
from database.databaseHandler import DatabaseHandler
from .sms import SMS
import yaml

# Control Panel for admin
class ControlConsole(Thread):

    def __init__(self, sms: SMS, msg: Message, secretPath: str = 'secrets.yml'):
        Thread.__init__(self)
        self.db = None
        self.sms = sms
        self.msg = msg
        self.number = Number(msg.number)

        with open(secretPath) as f:
            cfg = yaml.safe_load(f)
        self.adminNumbers = map(Number, cfg['admin']['numbers'])
        self.password = cfg['admin']['password']

        if self.checkIsAdmin():
            self.run()
        
    def checkIsAdmin(self):
        # Wait for password:
        rawInput = self.sms.awaitResponse(str(self.number))

        if self.number in self.adminNumbers:
            if rawInput.content == self.password:
                return True
        return False
    
    def run(self):
        adminConsoleExit = "You exited admin mode."
        successMessage = "Admin access granted. Text 'QUIT' to exit out of admin mode."

        self.sms.send(str(self.number), successMessage)

        # Creates temporary DBs.
        dbNorth = DatabaseHandler(SchoolNameMapper()['NNHS'])
        dbSouth = DatabaseHandler(SchoolNameMapper()['NSHS'])

        # Dict of MSG: Response
        responsesDict = {
            'HELP': self.help,
            'ANNOUNCE': self.announce,
        }
        
        content = self.sms.awaitResponse(str(self.number)).content.upper()
        while content != 'QUIT':
            if content in responsesDict:
                responsesDict[content]()
            content = self.sms.awaitResponse(str(self.number)).content.upper()
        
        # Quitting admin mode.
        self.sms.send(str(self.number), adminConsoleExit)

    def announce(self):
        schools = ["SOUTH", "NORTH"]
        grades = ["9", "10", "11", "12"]

        announceInit = "You've entered announcement mode. To exit at any time, text 'EXIT'."
        announcementPromptMsg = "Enter the message you would like to send."
        announcementPromptConfirmation = "Here is the announcement you want to send"
        confirmationProcess = "Type 'YES' to confirm, or 'NO' to cancel."
        announceSuccess = "Announcement sent."
        announceExit = "Exiting announcement mode."
        
        self.sms.send(str(self.number), announceInit)
        self.sms.send(str(self.number), announcementPromptMsg)

        content = self.sms.awaitResponse(str(self.number)).content

        if content.upper() != 'EXIT':
            announcement = content
            self.sms.send(str(self.number), announcementPromptConfirmation) 
            self.sms.send(str(self.number), announcement)
            self.sms.send(str(self.number), confirmationProcess)
        
        content = self.sms.awaitResponse(str(self.number)).content.upper()
        
        if content == 'YES':
            schoolPresent = False
            gradePresent = False

            responses = self.announcementGrabToSend()

            if len(responses) != 0:
                if "ALL" in responses:
                    schoolPresent = True
                    print("GOING TO SEND TO ALL")
                    # Send to all
                else:
                    for response in responses:
                        if response in schools:
                            schoolPresent = True
                            school = SchoolNameMapper()[response]
                            print(school)
                            # Send to school
                        elif response in grades:
                            gradePresent = True
                            grade = response
                            print(grade)
                            # Send to grade
                    if gradePresent and schoolPresent:
                        pass
                        # Send to school and grade
                    elif not gradePresent and schoolPresent:
                        pass
                    else:
                        # responses.announcementGrabToSend()
                        pass
            elif content == "NO":
                self.sms.send(str(self.number), announceExit)
                return True
            else:
                self.sms.send(str(self.number), "Invalid input. Please start process again.")

        self.sms.send(str(self.number), announceExit)
        print(responses)
        # School: South; Grade: 9;

    # def analytics(self):
    #     pass
    
    def announcementGrabToSend(self):
        announcePromptSend = "To whom would you want to send to? Enter school and grade in different messages. Enter 'DONE' when finished. Enter 'ALL' if you want to send to all"
        
        content = self.sms.send(str(self.number), announcePromptSend)

        responses = []
        while content != 'DONE':
            responses.append(content)
            content = self.sms.awaitResponse(str(self.number)).content.upper()

        return responses
        
    def help(self):
        helpMessage = "Enter 'SUBSCRIBE' to subscribe to abSENT. Enter 'CANCEL' to cancel the service. Enter 'EDIT' to edit your schedule. Enter 'SCHEDULE' to view your schedule. Enter 'ABOUT' to learn more about abSENT. Enter 'HELP' to view this help message."
        self.sms.send(str(self.number), helpMessage)
        return True
    
    def massSend(self, message: str, numbers: list):
        for number in numbers:
            self.sms.send(number, message)
