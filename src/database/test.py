from dataBaseHandler import *
from dataStructs import *
from dataBaseHandler import *
from testTools import *

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

# print(test_classes)
# pp.pprint(test_classes)
# print(test_teacher)
# print(test_student)

# test_dict = {"Kevin": test_student}
# writeToPickle(test_dict, "data/test.pkl")
# test_handle = DatabaseHandler("src/database/test.pkl")
test_handle = DatabaseHandler("data/test.pkl")
print(test_handle.readSavedDirectory)
# print(test_handle.readSavedDirectory('data/directory.pkl'))
# test_handle.writeDirectory(test_handle.directory_path)