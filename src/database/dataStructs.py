from dataclasses import dataclass

@dataclass
class Teacher:
    first: str
    last: str

    def __str__(self):
        return f"{self.first} {self.last}"

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
    
@dataclass
class Student:
    first: str
    last: str
    number: Number
    schedule: Schedule

    def __str__(self):
        return f"{self.first} {self.last}: {self.number} {self.schedule}"
