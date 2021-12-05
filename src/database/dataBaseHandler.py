from dataStructs import *
import pickle

import os # To edit PYTHONHASHSEED environment variable

class DatabaseHandler:
    # abSENT's database consists of two structures:
    # 1. Classes: a dictionary that maps a teacher to a set of students
    # 2. Directory: a dictionary that maps a unique number its coorsponding student

    # Classes is used to notify each student when a teacher is absent
    # Directory is meant to keep track of who is part of the abSENT system (think of user directory)

    # Type defintions:
    classes: dict[Teacher: set()]
    directory: dict[Number: Student]

    # Note: For classes, teacher maps to a set of students in order to ensure uniquness and no repeats, rather than a non-unique list.

    def __init__(self, directory_path: str ='data/directory.pkl', classes_path: str ='data/classes.pkl'):
        os.environ['PYTHONHASHSEED'] = '1' # Set hash seed to 0 to ensure reproducibility between sessions for dictionary keys
        self.directory_path = directory_path
        self.directory = self.readPickle(directory_path)
        self.classes = self.readPickle(classes_path)
    
    # Read objects from pickle file
    def readPickle(self, path):
        if path.lower().endswith(('.pkl')): # Check if path points to a pickle file
            if not os.stat(path).st_size == 0: # Check if pickle file is empty
                with open(path, 'rb') as f: 
                    return pickle.load(f) # Load pickle file
            else:
                return {} # There is no file, so return an empty dictionary
        else:
            raise Exception('Directory Path is not a pickle file')

    # Write objects to a pickle file
    def writeToPickle(self, object, path) -> bool:
        with open(path, 'wb') as f:
            pickle.dump(object, f)
            return True
    
    # Save current instance of directory to pickle file
    def saveDirectory(self, directory, path='data/directory.pkl') -> bool:
        return self.writeToPickle(directory, path)

    # Save current instance of classes to pickle file
    def saveClasses(self, classes, path='data/classes.pkl') -> bool:
        return self.writeToPickle(classes, path)
        
    # Add student to user directory
    def addStudent(self, student: Student) -> bool:
        if student.number not in self.directory:
            self.directory[student.number] = student
            self.saveDirectory(self.directory)
            return True
        return False
    
    # Remove student from entire abSENT system (directory and classes)
    def removeStudent(self, student: Student) -> bool:
        # Remove student from directory
        if student.number in self.directory:
            del self.directory[student.number]
            self.saveDirectory(self.directory)

            # Remove student from classes
            for block in student.schedule: # Iterate through the student's schedule
                # Remove student from its respective class 
                self.removeStudentFromClass(student, block)
            return True
        return False
    
    # Add teacher to classes
    def addTeacher(self, teacher: Teacher) -> bool:
        if teacher not in self.classes:
            self.classes[teacher] = set()
            self.saveClasses(self.classes)
            return True
        return False
    
    # Remove teacher from classes
    def removeTeacher(self, teacher: Teacher) -> bool:
        if teacher in self.classes:
            del self.classes[teacher]
            self.saveClasses(self.classes)
            return True
        return False
    
    # Add student to its respective teacher's classes
    def addStudentToClass(self, student: Student, teacher: Teacher) -> bool:
        if teacher in self.classes:
            print(self.classes[teacher])
            print(type(self.classes[teacher]))
            self.classes[teacher].add(student)
            self.saveClasses(self.classes)
            return True
        return False
    
    # Remove student from its respective teacher's classes
    def removeStudentFromClass(self, student: Student, teacher: Teacher) -> bool:
        if student.number in self.directory and teacher in self.classes:
            self.classes[teacher].remove(student)
            self.saveClasses(self.classes)
            return True
        return False