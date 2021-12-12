# abSENT
 ![abSENT Github Banner](marketing/banner.png)

## What is it?
An SMS schoology bot that texts NPS students when their teachers are absent. Supports both Newton high schools, [Newton South](https://www.newton.k12.ma.us/nshs) & [Newton North](https://www.newton.k12.ma.us/nnhs).

Running on a Python based server, it uses the [Schoolopy](https://github.com/ErikBoesen/schoolopy) API to grab teacher absences from Schoology, which is processed and then texted through using the [PyTextNow](https://github.com/leogomezz4t/PyTextNow_API) API to the students who have absent teachers.

## How does it work?
Students sign up by texting abSENT's phone number and inputting their schedule. The schedule is then saved as an SQLite database using 5 tables:

- One table stores students and their characteristics (name and phone number)
- Another stores teachers and their characteristics (name)
- The third table is an array of classes that maps teacher & block -> student. 
- The remaining tables are relational that connect the class IDs to student IDs, and class IDs to teacher IDs. 

Every school day, abSENT retrives the day's teacher absences and then queries the SQLite database by teacher ID and block to find students who have absent teachers. These students are then notifed over text that their teacher is absent.

## Why?
Refreshing Schoology 20 times every morning is somewhat draining.

## Contributors
- [Kevin Yang](https://github.com/bykevinyang) - (primarily) DB management, UI/UX, & marketing
- [Roshan Karim](https://github.com/karimroshan) - (primarily) SMS code, threading, & UI/UX

## Disclaimer:
abSENT as a project is not affiliated with any of the entities who's students it serves. We are students and have written this project just for fun, as a minor QOL improvement in the morning.
