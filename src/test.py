from database.dataBaseHandler import *
from dataStructs import *
from database.dataBaseHandler import *
from database.testTools import *

import pprint
pp = pprint.PrettyPrinter(indent=4)

test_num = Number("6176868207")
test_teacher = Teacher("Kevin", "Yang")
test_schedule = Schedule(test_teacher, test_teacher, test_teacher, test_teacher, test_teacher, test_teacher, None)
test_student1 = Student("Kevin", "Yang", test_num, test_schedule)
test_student2 = Student("Roshan", "Karim", test_num, test_schedule)

teacher1 = Teacher("RYAN", "NORMANDIN")
teacher2 = Teacher("JOSHUA", "HUANG")

test_classes = {teacher1: [test_student1, test_student2], teacher2: [test_student1]}
test_directory = {test_student1.number: test_student1, test_student2.number: test_student2}
# writeToPickle(test_classes, "data/classes.pkl")
# print(test_classes)
# pp.pprint(test_classes)
# print(test_teacher)
# print(test_student)

# test_dict = {"Kevin": test_student}
# writeToPickle(test_directory, "data/directory.pkl")
# test_handle = DatabaseHandler("src/database/test.pkl")
test_handle = DatabaseHandler()
# # print(test_handle.directory)
# # print(test_handle.classes)

test_student3 = Student("Joe", "Mama", Number("6175059606"), test_schedule)
test_handle.addStudent(test_student3)

teacher4 = Teacher("ASIDASUB", "ASDIBASUDB")

test_handle.addTeacher(teacher1)
# print(test_handle.classes)
for teacher in test_handle.classes:
    print(teacher)

print("\nAFTER CHANGE\n")
test_handle.removeTeacher(teacher4)
for teacher in test_handle.classes:
    print(teacher)



# print(test_handle.classes)
# print(test_handle.addStudentToClass(test_student3, teacher2))

# for key in test_handle.classes:
#     print(key)
#     for student in test_handle.classes[key]:
#         print(student)
# pp.pprint(test_handle.directory)
# print(test_handle.readSavedDirectory('data/directory.pkl'))
# test_handle.writeDirectory(test_handle.directory_path)