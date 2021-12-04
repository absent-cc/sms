from dataBaseHandler import *
from dataStructs import *

test_num = Number("6176868207")
test_teacher = Teacher("Kevin", "Yang")
test_schedule = Schedule(test_teacher, test_teacher, test_teacher, test_teacher, test_teacher, test_teacher, None)
test_student = Student("Kevin", "Yang", test_num, test_schedule)

print(test_teacher)
print(test_student)

test_handle = DatabaseHandler("src/database/test.pkl")
print(test_handle.readSavedDirectory('data/directory.pkl'))
# test_handle.writeDirectory(test_handle.directory_path)