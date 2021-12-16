from dataStructs import *
from textnow.sms import sms
from database.databaseHandler import *
from schoology.absence import Absence

class LogicDriver:
    
    def __init__(self, creds: TextNowCreds, sckeys: list, scsecrets: list):
        self.sms = sms(creds)
        self.db = {
            SchoolName.NEWTON_NORTH: DatabaseHandler(SchoolName.NEWTON_NORTH), 
            SchoolName.NEWTON_SOUTH: DatabaseHandler(SchoolName.NEWTON_SOUTH)
        }
        self.blockDict = {
            0: None,
            1: (SchoolBlock.A, SchoolBlock.B, SchoolBlock.C, SchoolBlock.D, SchoolBlock.E),
            2: (SchoolBlock.A, SchoolBlock.B, SchoolBlock.F, SchoolBlock.G),
            3: (SchoolBlock.C, SchoolBlock.D, SchoolBlock.E, SchoolBlock.F),
            4: (SchoolBlock.A, SchoolBlock.B, SchoolBlock.G, SchoolBlock.E),
            5: (SchoolBlock.C, SchoolBlock.D, SchoolBlock.F, SchoolBlock.G),
            6: None
        }
        self.sc = Absence(sckeys, scsecrets)

    def run(self, date):
        #NNHS Runtime
        northAbsences = self.getAbsenceList(date, SchoolName.NEWTON_NORTH)
        notificationList = self.getStudentsToNotify(date, northAbsences, SchoolName.NEWTON_NORTH) 
        messages = self.genMessages(notificationList)
        print("NNHS:")
        self.sendMessages(messages)
        #NSHS Runtime
        southAbsences = self.getAbsenceList(date, SchoolName.NEWTON_SOUTH)
        notificationList = self.getStudentsToNotify(date, northAbsences, SchoolName.NEWTON_SOUTH) 
        messages = self.genMessages(notificationList)
        print("NSHS:")
        self.sendMessages(messages)
        return True

    def getAbsenceList(self, date, school):
        if school == SchoolName.NEWTON_NORTH:
            absenceList = self.sc.filterAbsencesNorth(date)
        elif school == SchoolName.NEWTON_SOUTH:
            absenceList = self.sc.filterAbsencesSouth(date)
        else:
            return None
        return absenceList

    def getStudentsToNotify(self, date, absences: list, school: SchoolName):
        notificationList = []
        for teacher in absences:
            for block in self.blockDict[int(date.strftime('%w'))]:
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
        for number in messageDict:
            self.sms.send(str(number), messageDict[number])
            print(f"Notification sent to {str(number)}.")