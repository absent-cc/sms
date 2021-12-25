from dataStructs import *
from textnow.sms import SMS
from database.databaseHandler import *
from schoology.absence import Absence
from datetime import date

class NotificationDriver:
    
    # Configures a dict of DB objects and a dict of blocks keyed by day as returned by datetime.
    def __init__(self, textnowCreds: TextNowCreds, scCreds: SchoologyCreds):
        self.sms = SMS(textnowCreds)
        self.db = {
            SchoolName.NEWTON_NORTH: DatabaseHandler(SchoolName.NEWTON_NORTH), 
            SchoolName.NEWTON_SOUTH: DatabaseHandler(SchoolName.NEWTON_SOUTH)
        }
        self.blockDict = {
            0: (SchoolBlock.A, SchoolBlock.B, SchoolBlock.C, SchoolBlock.D, SchoolBlock.E),
            1: (SchoolBlock.A, SchoolBlock.B, SchoolBlock.F, SchoolBlock.G),
            2: (SchoolBlock.C, SchoolBlock.D, SchoolBlock.E, SchoolBlock.F),
            3: (SchoolBlock.A, SchoolBlock.B, SchoolBlock.G, SchoolBlock.E),
            4: (SchoolBlock.C, SchoolBlock.D, SchoolBlock.F, SchoolBlock.G),
            5: None,
            6: None
        }
        self.sc = Absence(scCreds)

    # Runtime code, calls the various functions within the class and sends the appropriate messages to people with absent teachers.
    def run(self, date, school: SchoolName):
        self.date = date
        absences = self.getAbsenceList(school)
        print(absences)
        if absences == None:
            print("NO DATA AVAILABLE.")
            return False
        notificationList = self.getStudentsToNotify(absences, school) 
        messages = self.genMessages(notificationList)
        attemptSend = self.sendMessages(messages)
        return True

    # Fetchs absent
    def getAbsenceList(self, school: SchoolName):
        if school == SchoolName.NEWTON_NORTH:
            absenceList = self.sc.filterAbsencesNorth(self.date)
        elif school == SchoolName.NEWTON_SOUTH:
            absenceList = self.sc.filterAbsencesSouth(self.date)
        else:
            return None
        return absenceList

    # Returns students in each class that a teacher is absent in.
    def getStudentsToNotify(self, absences: list, school: SchoolName):
        notificationList = []
        for teacher in absences:
            for block in self.blockDict[self.date.weekday()]:
                # To-Do: Implement casting between AbsentTeacher and Teacher classes
                queryStudents = self.db[school].queryStudentsByAbsentTeacher(Teacher(teacher.first, teacher.last, school), block)
                if queryStudents != []:
                    # Send notification to each student if there are students to sent to.
                    notificationList.append(NotificationInformation(teacher, queryStudents, block)) 
        return notificationList

    # Generates a dict of messages to send to each student.
    ## Each absent class for a student is smushed into one message to save TextNow API calls.
    def genMessages(self, notificationList: list):
        messageDict = {}
        messageStart = "Hey there! You have absent teachers!"
        for notification in notificationList:
            for student in notification.students:
                number = Number(student.number)
                messageContent = f"   | {notification.teacher.first} {notification.teacher.last} Note: {notification.teacher.note}. |"     
                # Map a number its update message. 
                ## Meant to prevent duplicate messages (Dict entries are unique)
                if messageDict.get(number) == None:
                    # Create number entry if it doesn't exist.
                    messageDict[number] = messageStart + messageContent
                else:
                    # Append to existing message.
                    messageDict.update({number: messageDict[number] + messageContent})
        return messageDict

    # Send messages to each student.
    def sendMessages(self, messageDict: dict):
        if len(messageDict) == 0:
            print("No users to notify.")
            return False
        for number in messageDict:
            self.sms.send(str(number), messageDict[number])
            print(f"Notification sent to {str(number)}.")
        return True