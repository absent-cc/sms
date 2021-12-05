from database.testTools import *
from database.dataBaseHandler import *
from dataStructs import *
from database.dataBaseHandler import *
from database.testTools import *

test_num = Number("6176868207")
test_teacher = Teacher("Kevin", "Yang")
test_schedule = Schedule(test_teacher, test_teacher, test_teacher, test_teacher, test_teacher, test_teacher, None)

test_student1 = Student("Kevin", "Yang", test_num, test_schedule)
test_student2 = Student("Roshan", "Karim", test_num, test_schedule)

teacher1 = Teacher("RYAN", "NORMANDIN")
teacher2 = Teacher("JOSHUA", "HUANG")

test_classes = {teacher1: {test_student1, test_student2}, teacher2: {test_student1}}
test_directory = {test_student1.number: test_student1, test_student2.number: test_student2}

writeToPickle(test_classes, "data/classes.pkl")
writeToPickle(test_directory, "data/directory.pkl")