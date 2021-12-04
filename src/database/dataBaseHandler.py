from dataStructs import *
import pickle

import os # To edit PYTHONHASHSEED environment variable

class DatabaseHandler:
    classes: dict[Teacher: list[Student]]
    directory: dict[Number: Student]

    def __init__(self, directory_path='data/directory.pkl', classes_path='data/classes.pkl'):
        os.environ['PYTHONHASHSEED'] = '0' # Set hash seed to 0 to ensure reproducibility between sessions
        self.directory_path = directory_path
        self.directory = self.readPickle(directory_path)
        self.classes = self.readPickle(classes_path)
    
    def readPickle(self, path):
        if path.lower().endswith(('.pkl')):
            with open(path, 'rb') as f:
                return pickle.load(f)
        else:
            raise Exception('Directory Path is not a pickle file')

    def writeToPickle(self, object, path):
        with open(path, 'wb') as f:
            pickle.dump(object, f)
    
    def saveDirectory(self, directory, path='data/directory.pkl'):
        self.writeToPickle(directory, path)

    def saveClasses(self, classes, path='data/classes.pkl'):
        self.writeToPickle(classes, path)
    
    def addStudent(self, student: Student) -> bool:
        if student.number not in self.directory:
            self.directory[student.number] = student
            return True
        return False
    
    def removeStudent(self, student: Student) -> bool:
        if student.number in self.directory:
            del self.directory[student.number]
            return True
        return False
    
    def addTeacher(self, teacher: Teacher) -> bool:
        if teacher not in self.classes:
            self.classes[teacher] = []
            return True
        return False
    
    def removeTeacher(self, teacher: Teacher) -> bool:
        if teacher in self.classes:
            del self.classes[teacher]
            return True
        return False
    
    def addStudentToClass(self, student: Student, teacher: Teacher) -> bool:
        if teacher in self.classes:
            self.classes[teacher].append(student)
            return True
        return False
    
    def removeStudentFromClass(self, student: Student, teacher: Teacher) -> bool:
        if student.number in self.directory and teacher in self.classes:
            self.classes[teacher].remove(student)
            return True
        return False