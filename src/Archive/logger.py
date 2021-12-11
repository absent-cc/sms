from dataStructs import *
from datetime import datetime 
import os

# Logger to record actions of abSENT
class Logger():
    def __init__(self, path: str = "data/log.txt"):
        self.path = path
        # Check if log file exists
        # If not, create it
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                f.write("TIME | ACTION | DETAILS\n")      

    # Default method for logging
    def log(self, message):
        current_time = datetime.now()
        with open(self.path, 'a') as f:
            f.write(f"{current_time} | {message}\n")
    
    # Log when new student is added to database
    def addedStudent(self, user: Student):
        self.log(f"STUDENT ADDED \t| {user.first} {user.last} {user.number}")

    # Log when student is removed from database    
    def removedStudent(self, user: Student):
        self.log(f"STUDENT REMOVED \t| {user.first} {user.last} {user.number}")
    
    # Log when a new teacher is added to database
    def addedTeacher(self, teacher: Teacher):
        self.log(f"TEACHER ADDED \t| {teacher.first} {teacher.last}")
    
    # Log when a teacher is removed from database
    def removedTeacher(self, teacher: Teacher):
        self.log(f"TEACHER REMOVED \t| {teacher.first} {teacher.last}")

    # Method to reset log file
    def resetLog(self):
        with open(self.path, 'w') as f:
            f.write("TIME | ACTION | DETAILS\n")      