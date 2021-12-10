from dataStructs import *

import sqlite3

class DatabaseHandler():
    classes_id = 0
    user_id = 0
    teacher_id = 0

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
            grade TEXT)
            """
        create_teacher_directory = """
        CREATE TABLE IF NOT EXISTS teacher_directory (
            teacher_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            school TEXT)
            """
        create_classes = """
        CREATE TABLE IF NOT EXISTS classes (
            class_id INTEGER PRIMARY KEY,
            teacher_id INTEGER,
            block TEXT,
            student_id INTEGER,
            FOREIGN KEY(teacher_id) REFERENCES student_directory(teacher_id),
            FOREIGN KEY(student_id) REFERENCES teacher_directory(student_id))
            """
        self.cursor.execute(create_student_directory)
        self.cursor.execute(create_teacher_directory)
        self.cursor.execute(create_classes)

    def reset(self):
        import os
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def add_user(self, user: Student):
        pass
if __name__ == "__main__":
    schedule = Schedule()
    print(schedule)
    # db = DatabaseHandler(SchoolName.NEWTON_SOUTH)

