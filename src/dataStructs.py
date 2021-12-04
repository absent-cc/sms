from dataclasses import dataclass

@dataclass
class Teacher:
    first: str
    last: str

    def __str__(self):
        return f"{self.first} {self.last}"

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if not isinstance(other, Teacher):
            return False
        return self.first == other.first and self.first == other.last

@dataclass
class Schedule:
    A: Teacher
    B: Teacher
    C: Teacher
    D: Teacher
    E: Teacher
    F: Teacher
    G: Teacher

    def __str__(self):
        return f"A: {self.A}, B: {self.B}, C: {self.C}, D: {self.D}, E: {self.E}, F: {self.F}, G: {self.G}"

@dataclass
class Number:
    number: str

    def __str__(self):
        return self.number
    
    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if not isinstance(other, Number):
            return False
        return self.number == other.number

@dataclass
class Student:
    first: str
    last: str
    number: Number
    schedule: Schedule

    def __str__(self):
        return f"{self.first} {self.last}: {self.number} {self.schedule}"

@dataclass
class AbsentTeacher:
    first: str
    last: str 
    length: str
    date: str
    note: str

    def __str__(self):
        return f"{self.first} {self.last} {self.length} {self.date} {self.note}"