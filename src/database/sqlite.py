import sqlite3
from dataStructs import *
from typing import Tuple, List

# MAKE SURE TO FILTER NAMES TO PREVENT SQL INJECTION

class databaseHandler():
    id = 0
    def __init__(self, db_path="data/absent.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        create_directory = """
        CREATE TABLE IF NOT EXISTS directory 
        (id STRING PRIMARY KEY,
        number STRING, 
        first STRING,
        last STRING, 
        A_Last STRING, A_First STRING,
        B_Last STRING, B_First STRING,
        C_Last STRING, C_First STRING,
        D_Last STRING, D_First STRING,
        E_Last STRING, E_First STRING,
        F_Last STRING, F_First STRING,
        G_Last STRING, G_First STRING)
        """

        create_classes = """
        CREATE TABLE IF NOT EXISTS classes 
        (teacher_first STRING,
        teacher_last STRING, 
        FOREIGN KEY(number) REFERENCES directory(number)
        """
        self.cursor.execute(create_directory)

    def new_id(self):
        databaseHandler.id += 1
        return databaseHandler.id

    def checkIfInDirectory(self, student: Student) -> bool:
        command = f"""SELECT EXISTS(SELECT 1 FROM directory WHERE number='{student.number}' LIMIT 1)
        """
        result = self.cursor.execute(command).fetchone()
        if result == (1,):
            return True
        return False
    
    def teacherTupleList(self, student: Student):
        teachers: list[Tuple(str, str)]= []
        for block in student.schedule:
            teacher = student.schedule[block]
            if teacher != None:
                teachers.append((teacher.first, teacher.last))
            else:
                teachers.append(("", ""))
        return teachers
    
    def addStudentToDirectory(self, student: Student) -> bool:
        if not self.checkIfInDirectory(student):
            teachers = self.teacherTupleList(student)
            new_id = self.new_id()
        
            command = f"""
            INSERT INTO directory VALUES
            ('{new_id}', '{student.number}', '{student.first}', '{student.last}',
            '{teachers[0][0]}', '{teachers[0][1]}',
            '{teachers[1][0]}', '{teachers[1][1]}',
            '{teachers[2][0]}', '{teachers[2][1]}',
            '{teachers[3][0]}', '{teachers[3][1]}',
            '{teachers[4][0]}', '{teachers[4][1]}',
            '{teachers[5][0]}', '{teachers[5][1]}',
            '{teachers[6][0]}', '{teachers[6][1]}')
            """
            self.connection.execute(command) 
            self.connection.commit()
            return True
        return False
    
    def removeStudentFromDirectory(self, student: Student) -> bool:
        if self.checkIfInDirectory(student):
            command = f"""
            DELETE FROM directory WHERE number='{student.number}'
            """
            self.connection.execute(command)
            self.connection.commit()
            return True
        return False
    
    def updateStudentInDirectory(self, student: Student) -> bool:
        if self.checkIfInDirectory(student): 
            teachers = self.teacherTupleList(student)
            command = f"""
            UPDATE directory SET
                number='{student.number}',
                first='{student.first}',
                last='{student.last}',
                A_Last='{teachers[0][0]}', A_First='{teachers[0][1]}',
                B_Last='{teachers[1][0]}', B_First='{teachers[1][1]}',
                C_Last='{teachers[2][0]}', C_First='{teachers[2][1]}',
                D_Last='{teachers[3][0]}', D_First='{teachers[3][1]}',
                E_Last='{teachers[4][0]}', E_First='{teachers[4][1]}',
                F_Last='{teachers[5][0]}', F_First='{teachers[5][1]}',
                G_Last='{teachers[6][0]}', G_First='{teachers[6][1]}'
                WHERE number='{student.number}'
            """
            self.connection.execute(command)
            self.connection.commit()
            return True
        return False

    def getStudentFromDirectory(self, id=None, Number=None) -> Student:
        if id != None:
            command = f"""
            SELECT * FROM directory WHERE id='{id}'
            """
            self.cursor.execute(command)
            row = self.cursor.fetchone()
            print(row)
            # student = Student(row[1], row[2], row[3])


    def __repr__(self) -> str:
        return self.print_directory() + self.print_classes()

    def print_directory(self) -> str:
        string = ""
        self.cursor.execute("SELECT * FROM directory")
        for row in self.cursor.fetchall():
            string += str(row) + "\n"
    
    def print_classes(self) -> str:
        string = ""
        self.cursor.execute("SELECT * FROM classes")
        for row in self.cursor.fetchall(): 
            string += str(row) + "\n"
    
            
    def __repr__(self) -> str:
        pass

if __name__ == "__main__":
    NORM = Teacher("RYAN", "NORMANDIN")
    PAL = Teacher("ALEX", "PALILUNAS")
    BECKER = Teacher("RACHEL", "BECKER")
    KOZUCH = Teacher("MICAEL", "KOZUCH")
    CROSBY = Teacher("ALAN", "CROSBY")
    RUGG = Teacher("ILANA", "RUGG")

    Kevin_Schedule = Schedule(NORM, PAL, BECKER, KOZUCH, None, CROSBY, PAL)
    Kevin_Num = Number("6176868207")
    Kevin = Student("Kevin", "Yang", Kevin_Num, Kevin_Schedule)

    test = databaseHandler()
    test.addStudentToDirectory(Kevin)
    Kevin.schedule["B"] = CROSBY
    print(Kevin.schedule["B"])
    print(test.updateStudentInDirectory(Kevin))
    test.getStudentFromDirectory(id=1)
    # def add_student(self, number, first, last, a, b, c, d, e, f):
    
# connection = sqlite3.connect("data/absent.db")

# cursor = connection.cursor()

# print(connection.total_changes)