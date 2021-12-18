from dataStructs import *
from textnow.sms import sms
from database.databaseHandler import *
from schoology.absence import Absence
from datetime import date
class LogicDriver:
    
    # Configures a dict of DB objects and a dict of blocks keyed by day as returned by datetime.
    def __init__(self, textnowCreds: TextNowCreds, scCreds: SchoologyCreds):
        self.sms = sms(textnowCreds)
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

    def getStudentsToNotify(self, absences: list, school: SchoolName):
        notificationList = []
        for teacher in absences:
            for block in self.blockDict[self.date.weekday()]:
                queryStudents = self.db[school].queryStudentsByAbsentTeacher(Teacher(teacher.first, teacher.last, school), block)
                if queryStudents != []:
                    notificationList.append(NotificationInformation(teacher, queryStudents, block)) 

        return notificationList

    def genMessages(self, notificationList: list):
        messageDict = {}
        messageStart = "You are recieving a notification because you have (an) absent teacher(s)."
        for notification in notificationList:
            for student in notification.students:
                number = Number(student.number)
                messageContent = f" {notification.teacher.first} {notification.teacher.last} is absent. They leave the following note: {notification.teacher.note}."        
                if messageDict.get(number) == None:
                    messageDict[number] = messageStart + messageContent
                else:
                    messageDict.update({number: messageDict[number] + messageContent})
        return messageDict

    def sendMessages(self, messageDict: dict):
        if len(messageDict) == 0:
            print("No users to notify.")
            return False
        for number in messageDict:
            self.sms.send(str(number), messageDict[number])
            print(f"Notification sent to {str(number)}.")
        return True