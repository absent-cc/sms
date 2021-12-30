from dataStructs import Schedule, SchoolBlock, SchoolName, Student, Teacher
from database.databaseHandler import DatabaseHandler 

test = DatabaseHandler(SchoolName.NEWTON_SOUTH)

student = Student("6176868207", "Kevin", "Yang", SchoolName.NEWTON_SOUTH, "10")
teacher1 = Teacher("Joe", "Smith", SchoolName.NEWTON_SOUTH)
schedule = Schedule(teacher1)
new_schedule = Schedule(None, teacher1)

new_teacher = Teacher("NEw", "HI", SchoolName.NEWTON_SOUTH)

test.addStudent(student, schedule)
test.changeClass(student, SchoolBlock.A,  new_teacher)