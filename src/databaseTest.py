from database.dataBaseHandler import *


NORM = Teacher("RYAN", "NORMANDIN")
PAL = Teacher("ALEX", "PALILUNAS")
BECKER = Teacher("RACHEL", "BECKER")
KOZUCH = Teacher("MICAEL", "KOZUCH")
CROSBY = Teacher("ALAN", "CROSBY")
RUGG = Teacher("ILANA", "RUGG")

JOE = Teacher("JOE", "SMITH")
MAMA = Teacher("MAMA", "STRIKE")
ALFRED = Teacher("ALFRED", "CURTIS")
JACK = Teacher("JACK", "ALLEN")
JOHN = Teacher("JOHN", "JACOBS")
CENA = Teacher("CENA", "MILLER")

Kevin_Schedule = Schedule(NORM, PAL, BECKER, KOZUCH, None, CROSBY, RUGG)
Kevin_Num = Number("6176868207")
Kevin = Student("Kevin", "Yang", Kevin_Num, Kevin_Schedule)

Roshan_schedule = Schedule(JOE, MAMA, ALFRED, JACK, JOHN, CENA, None)
Roshan_Num = Number("6175525098")
Roshan = Student("Roshan", "Karim", Roshan_Num, Roshan_schedule)

print(Kevin)
print(Roshan)

db = DatabaseHandler()