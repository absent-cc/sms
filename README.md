# abSENT

### What is it?
A Python based server software utilizing the Schoolopy API for schoology and the pytextnow "API" for TextNow to send alerts to students when their teachers are absent. 

### How's it work?
Students sign up by texting our phone number, and input their full schedule. This is then saved to our SQLite database using 5 tables. One table stores students and their characteristics (name and phone number), another stores teachers and their characteristics (just name, here), and the final data table is simple a list of classes that each teacher teaches. Because of the lack of information, it is assumed that a teacher teaches every block and classes are indexed as such although this is likely inaccurate. The remaining two tables are used as reference tables, the first used to link student-ids to their class-ids and the latter to link teacher-ids with class-ids. 

That said and done, a call to the last DB with the teacher Ids will return a list of classes that that teacher teaches, and now it is simply a matter of recursing through the fourth DB and sending messages to each student within all class-ids of the absent teacher.

### Why?
Why not?
