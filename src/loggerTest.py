from database.logger import *

NORM = Teacher("RYAN", "NORMANDIN")
PAL = Teacher("ALEX", "PALILUNAS")
BECKER = Teacher("RACHEL", "BECKER")
KOZUCH = Teacher("MICAEL", "KOZUCH")
CROSBY = Teacher("ALAN", "CROSBY")
RUGG = Teacher("ILANA", "RUGG")

Kevin_Schedule = Schedule(NORM, PAL, BECKER, KOZUCH, None, CROSBY, RUGG)
Kevin_Num = Number("6176868207")
kevin = Student("Kevin", "Yang", Kevin_Num, Kevin_Schedule)

test_log = Logger()
test_log.resetLog()
test_log.addedStudent(kevin)
test_log.removedStudent(kevin)
test_log.addedTeacher(NORM)
test_log.removedTeacher(NORM)