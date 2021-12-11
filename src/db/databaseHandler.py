from dataStructs import *
import sqlite3
from typing import Tuple, List

class DatabaseHandler():
    def __init__(self, school: SchoolName, db_path = "abSENT.db"):
        self.db_path = f"data/{school.name}_{db_path}"
        
        self.reset()

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

        self.student_id, self.teacher_id, self.classes_id = self.loadMaxIDs()
    
    def loadMaxIDs(self) -> Tuple[int, int, int]:

        grab_max_student_id = """
        SELECT MAX(student_id) FROM student_directory
        """
        grab_max_teacher_id = """
        SELECT MAX(teacher_id) FROM teacher_directory
        """
        grab_max_class_id = """
        SELECT MAX(class_id) FROM classes
        """
        
        self.cursor.execute(grab_max_student_id)
        res = self.cursor.fetchone()[0]
        if res != None:
            student_id = res[0]
        else:
            student_id = 0

        self.cursor.execute(grab_max_teacher_id)
        res = self.cursor.fetchone()[0]
        if res != None:
            teacher_id = res
        else:
            teacher_id = 0

        self.cursor.execute(grab_max_class_id)
        res = self.cursor.fetchone()[0]
        if res != None:
            classes_id = res
        else:
            classes_id = 0
        
        return (student_id, teacher_id, classes_id)
        
    # Reset the database, for development purposes only!
    def reset(self):
        import os
        # If the database exists, delete it
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    # Generate new ids for user, teacher, and class
    ## Generate new user id
    def newStudentID(self):
        # user_id universal for instance
        # Used to generate new user id's for table entries
        self.student_id += 1
        return self.student_id
    
    ## Generate new teacher id
    def newTeacherID(self):
        # teacher_id universal for instance
        # Used to generate new teacher ids for table entries
        self.teacher_id += 1
        return self.teacher_id

    ## Generate new class id
    def newClassID(self):
        # classes_id universal for instance
        # Used to generate new user id's for table entries
        self.classes_id += 1
        return self.classes_id

    # Get teacher object from DB based off of inputted teacher
    def getTeacher(self, teacher: Teacher):
        # Check if teacher object already has an id
        if teacher.id == None:
            # If not, search teachers in DB by first + last name
            query = f"SELECT * FROM teacher_directory WHERE first_name = '{teacher.first}' AND last_name = '{teacher.last}' LIMIT 1"
        else:
            # If teacher object already has an id, search teachers in DB by id
            query = f"SELECT * FROM teacher_directory WHERE teacher_id = '{teacher.id}' LIMIT 1"
        # Conduct query
        res = self.cursor.execute(query).fetchone()
        # If teacher is found (not None), return teacher object
        if res != None:
            teacher = Teacher(res[1], res[2], SchoolNameMapper()[res[3]], res[0])
            return teacher
        return None
    
    # Get student object from DB based off of inputted student
    def getStudent(self, student: Student):
        # Check if student object already has an id
        if student.id == None:
            # If not, search students in DB by number
            query = f"SELECT * FROM student_directory WHERE number = '{student.number}' LIMIT 1"
        else:
            # If student object already has an id, search students in DB by id
            query = f"SELECT * FROM student_directory WHERE student_id = '{student.id}' LIMIT 1"
        # Conduct query
        res = self.cursor.execute(query).fetchone()
        # If student is found (not None), return student object
        if res != None:
            student = Student(res[1], res[2], res[3], SchoolNameMapper()[res[4]], res[5], res[0])
            return student
        return None
    
    # Get teacher id from DB based off of inputted teacher
    ## Used to check if a teacher is in DB or not
    def getTeacherID(self, teacher: Teacher):
        # Check if teacher object already has an id
        if teacher.id == None:
            # If not, search teachers in DB by first + last name
            query = f"SELECT teacher_id FROM teacher_directory WHERE first_name = '{teacher.first}' AND last_name = '{teacher.last}' LIMIT 1"
            # Conduct query
            res = self.cursor.execute(query).fetchone()
            # If teacher is found (not None), return teacher id (first in results list)
            if res != None:
                return res[0]
            else:
                return None
        else:
            # If teacher object already has an id, return id
            return teacher.id
    
    # Get student id from DB based off of inputted student
    ## Used to check if a student is in DB or not
    def getStudentID(self, student: Student):
        # Check if student object already has an id
        if student.id == None:
            # If not, search students in DB by number
            query = f"SELECT student_id FROM student_directory WHERE number = '{student.number}' LIMIT 1"
            # Conduct query
            res = self.cursor.execute(query).fetchone()
            # If student is found (not None), return student id (first in results list)
            if res != None:
                return res[0]
            else:
                return None
        else:
            # If student object already has an id, return id
            return student.id

    # Add student to student directory
    ## Does not check whether or not student is already in DB, assumes not
    def addStudentToStudentDirectory(self, student: Student):
        # Generate new student id
        new_id = self.newStudentID()
        # Insert student into student directory
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
        # Conduct query
        self.cursor.execute(query)
        self.connection.commit()
        # Return the newly generated id for student object manipulation
        return new_id
    
    # Remove student from student directory
    def removeStudentFromStudentDirectory(self, student: Student) -> bool:
        # You can only remove student if there is a student id 
        if student.id == None:
            return False
        # Remove student from student directory
        query = f"DELETE FROM student_directory WHERE student_id = '{student.id}'"
        self.cursor.execute(query)
        self.connection.commit()
        return True

    # Add teacher to teacher directory
    ## Does not check whether or not teacher is already in DB, assumes not
    def addTeacherToTeacherDirectory(self, teacher: Teacher):
        # Generate new teacher id
        new_id = self.newTeacherID()
        # Insert teacher into teacher directory
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
    
    # Create a class entry for data table classes
    def addClassToClasses(self, teacher_id: int, block: SchoolBlock, student_id: int) -> Tuple[bool, int]:
        # Mapp enum SchoolBlock to string savable to DB
        str_block = BlockMapper()[block]
        # If any of the inputs are invalid, return False
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
    
    # Change existing class entry in data table classes
    def changeClass(self, student: Student, block: SchoolBlock, new_teacher: Teacher) -> bool:
        new_teacher_id = self.getTeacherID(new_teacher)
        student_id = self.getStudentID(student)
        if new_teacher_id != None and student_id != None:
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

    # Creates a new class entry in data table classes for student + teachers in their schedule
    ## General function to call when you want to add a user to abSENT system
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

    def queryStudentsByAbsentTeacher(self, teacher: Teacher, block: SchoolBlock) -> List[Student]:
        teacher_id = self.getTeacherID(teacher)
        if teacher_id == None:
            return []
        str_block = BlockMapper()[block]
        query = f"""
        SELECT *
        FROM student_directory
        WHERE student_id IN (
            SELECT student_id
            FROM classes
            WHERE teacher_id = '{teacher_id}' AND block = '{str_block}'
        )
        """
        res = self.cursor.execute(query).fetchall()
        students = []
        for col in res:
            students.append(Student(col[1], col[2], col[3], col[4], col[5], col[0]))
        return students

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