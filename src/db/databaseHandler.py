from types import resolve_bases
from dataStructs import *

import sqlite3

from typing import Tuple

class DatabaseHandler():

    def __init__(self, school: SchoolName, db_path = "abSENT.db"):
        self.classes_id = 0
        self.user_id = 0
        self.teacher_id = 0

        self.db_path = f"data/{school.name}_{db_path}"

        #self.reset()

        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        create_student_directory = """
        CREATE TABLE IF NOT EXISTS student_directory (
                student_id INTEGER PRIMARY KEY,
                number TEXT,
                first_name TEXT,
                last_name TEXT,
                school TEXT,
                grade TEXT
            )
            """
        create_teacher_directory = """
        CREATE TABLE IF NOT EXISTS teacher_directory (
                teacher_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                school TEXT
            )
            """
        create_classes = """
        CREATE TABLE IF NOT EXISTS classes (
                class_id INTEGER PRIMARY KEY,
                teacher_id INTEGER,
                block TEXT,
                student_id INTEGER,
                FOREIGN KEY(student_id) 
                    REFERENCES student_directory(student_id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
                FOREIGN KEY(teacher_id) 
                    REFERENCES teacher_directory(teacher_id)
            )
            """

        self.cursor.execute(create_student_directory)
        self.cursor.execute(create_teacher_directory)
        self.cursor.execute(create_classes)

    def reset(self):
        import os
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    # Generate new ids for user, teacher, and class
    def newUserID(self):
        self.user_id += 1
        return self.user_id
    
    def newTeacherID(self):
        self.teacher_id += 1
        return self.teacher_id

    def newClassID(self):
        self.classes_id += 1
        return self.classes_id

    def getTeacher(self, teacher: Teacher):
        if teacher.id == None:
            query = f"SELECT * FROM teacher_directory WHERE first_name = '{teacher.first}' AND last_name = '{teacher.last}' LIMIT 1"
        else:
            query = f"SELECT * FROM teacher_directory WHERE teacher_id = '{teacher.id}' LIMIT 1"
        res = self.cursor.execute(query).fetchone()
        if res != None:
            teacher = Teacher(res[1], res[2], SchoolNameMapper()[res[3]], res[0])
            return teacher
        return None
    
    def getStudent(self, student: Student):
        if student.id == None:
            query = f"SELECT * FROM student_directory WHERE number = '{student.number}' LIMIT 1"
        else:
            query = f"SELECT * FROM student_directory WHERE student_id = '{student.id}' LIMIT 1"
        res = self.cursor.execute(query).fetchone()
        if res != None:
            student = Student(res[1], res[2], res[3], SchoolNameMapper()[res[4]], res[5], res[0])
            return student
        return None
    
    def getTeacherID(self, teacher: Teacher):
        if teacher.id == None:
            query = f"SELECT teacher_id FROM teacher_directory WHERE first_name = '{teacher.first}' AND last_name = '{teacher.last}' LIMIT 1"
            res = self.cursor.execute(query).fetchone()
            if res != None:
                return res[0]
            else:
                return None
        else:
            return teacher.id
    
    def getStudentID(self, student: Student):
        if student.id == None:
            query = f"SELECT student_id FROM student_directory WHERE number = '{student.number}' LIMIT 1"
            res = self.cursor.execute(query).fetchone()
            if res != None:
                return res[0]
            else:
                return None
        else:
            return student.id
        
    def addStudentToUserDirectory(self, student: Student):
        new_id = self.newUserID()
        query = f"""
        INSERT INTO student_directory VALUES (
            '{new_id}',
            '{student.number}',
            '{student.first}',
            '{student.last}',
            '{student.school}',
            '{student.grade}'
            )
        """
        self.cursor.execute(query)
        self.connection.commit()
        return new_id
    
    def removeStudentFromUserDirectory(self, student: Student) -> bool:
        if student.id == None:
            return False
        query = f"DELETE FROM student_directory WHERE student_id = '{student.id}'"
        self.cursor.execute(query)
        self.connection.commit()
        return True

    def addTeacherToTeacherDirectory(self, teacher: Teacher):
        new_id = self.newTeacherID()
        query = f"""
        INSERT INTO teacher_directory VALUES (
            '{new_id}',
            '{teacher.first}',
            '{teacher.last}',
            '{teacher.school}'
            )
        """
        self.cursor.execute(query)
        self.connection.commit()
        return new_id
    
    def addClassToClasses(self, teacher_id: int, block: SchoolBlock, student_id: int) -> Tuple[bool, int]:
        str_block = BlockMapper()[block] 
        if teacher_id == None or str_block == None or student_id == None:
            return False, None
        new_id = self.newClassID()
        query = f"""
        INSERT INTO classes VALUES (
            '{new_id}',
            '{teacher_id}',
            '{str_block}',
            '{student_id}'
            )
        """
        self.cursor.execute(query)
        self.connection.commit()
        return True, new_id
    
    def changeClass(self, student: Student, block: SchoolBlock, new_teacher: Teacher) -> bool:
        new_teacher_id = self.getTeacherID(new_teacher)
        student_id = self.getStudentID(student)
        if new_teacher_id == None:
            self.addTeacherToTeacherDirectory(new_teacher)
        if student_id != None:
            str_block = BlockMapper()[block] 
            query = f"""
            UPDATE classes 
            SET teacher_id = '{new_teacher_id}' 
            WHERE student_id = '{student_id}' AND block = '{str_block}'
            """
            self.cursor.execute(query)
            self.connection.commit()
            return True
        return False
    
    def addStudent(self, student: Student, schedule: Schedule) -> bool:
        res_student = self.getStudent(student)
        if res_student == None:
            student_id = self.addStudentToUserDirectory(student)
        else:
            student_id = res_student.id
        for block in schedule:
            teacher = schedule[block]
            if teacher != None:
                teacher_id = self.getTeacherID(teacher)
                if teacher_id == None:
                    teacher_id = self.addTeacherToTeacherDirectory(teacher)
                self.addClassToClasses(teacher_id, block, student_id)
        return True


if __name__ == "__main__":
    kevin = Student("6176868207", "Kevin", "Yang", SchoolName.NEWTON_SOUTH, 10)
    roshan = Student("6175525098", "Roshan", "Karim", SchoolName.NEWTON_NORTH, 10)
    
    NORM = Teacher("RYAN", "NORMANDIN", SchoolName.NEWTON_SOUTH)
    PAL = Teacher("ALEX", "PALILUNAS", SchoolName.NEWTON_SOUTH)
    BECKER = Teacher("RACHEL", "BECKER", SchoolName.NEWTON_SOUTH)
    KOZUCH = Teacher("MICAEL", "KOZUCH", SchoolName.NEWTON_SOUTH)
    CROSBY = Teacher("ALAN", "CROSBY", SchoolName.NEWTON_SOUTH)
    RUGG = Teacher("ILANA", "RUGG", SchoolName.NEWTON_SOUTH)

    schedule = Schedule(NORM, PAL, BECKER, KOZUCH, CROSBY, RUGG)

    db = DatabaseHandler(SchoolName.NEWTON_SOUTH)
    db.addStudentToUserDirectory(kevin)
    db.addTeacherToTeacherDirectory(NORM)
    db.addTeacherToTeacherDirectory(BECKER)
    # print(db.addClassToClasses(db.getTeacherID(NORM), SchoolBlock.A, db.getStudentID(kevin)))
    # db.addStudentToUserDirectory(roshan) 
    db.addTeacherToTeacherDirectory(PAL)
    print(db.getStudent(kevin))
    print(db.getStudent(roshan))
    print(db.getTeacher(NORM))
    print(db.addStudent(kevin, schedule))
    # print(db.removeStudentFromUserDirectory(kevin))