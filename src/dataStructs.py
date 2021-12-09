from dataclasses import dataclass
import pretty_errors

@dataclass
class Teacher:
    first: str
    last: str

    def __init__(self, first, last):
        self.first = first.upper()
        self.last = last.upper()
    
    def __repr__(self) -> str:
        return f"Teacher: {self.first} {self.last}"

    def __str__(self):
        return f"{self.first} {self.last}"

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if not isinstance(other, Teacher):
            return False
        return self.first == other.first and self.last == other.last

# @dataclass
# class Schedule:
#     A: Teacher
#     B: Teacher
#     C: Teacher
#     D: Teacher
#     E: Teacher
#     F: Teacher
#     G: Teacher

#     def __str__(self):
#         return f"A: {self.A}, B: {self.B}, C: {self.C}, D: {self.D}, E: {self.E}, F: {self.F}, G: {self.G}"
    
#     def __iter__(self):
#             yield self.A
#             yield self.B
#             yield self.C
#             yield self.D
#             yield self.E
#             yield self.F
#             yield self.G

@dataclass
class Schedule(dict):
    # schedule: dict[str, Teacher]
    # kevin: str

    def __init__(self, A=None, B=None, C=None, D=None, E=None, F=None, G=None):
        self.schedule = {
            'A': A,
            'B': B,
            'C': C,
            'D': D,
            'E': E,
            'F': F,
            'G': G
        }
    
    def __str__(self):
        return f"A: {self.schedule['A']}, B: {self.schedule['B']}, C: {self.schedule['C']}, D: {self.schedule['D']}, E: {self.schedule['E']}, F: {self.schedule['F']}, G: {self.schedule['G']}"
    
    def __iter__(self):
        yield from self.schedule.keys()

    def __getitem__(self, key):
        return self.schedule[key]
    
    def __setitem__(self, key, value):
        self.schedule[key] = value

    def __delitem__(self, key):
        del self.schedule[key]
    
    def keys(self):
        return self.schedule.keys()
    
    def values(self):
        return self.schedule.values()
    
    def __contains__(self, item):
        return item in self.schedule.keys()

    # Remove self.schedule, make it self and see if that works
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
        return f"{self.first} {self.last}: {self.number}"
    
    def __repr__(self):
        return f"{self.first} {self.last}"

    def __eq__(self, other):
        if not isinstance(other, Student):
            return False
        return self.number == other.number
    
    def __hash__(self):
        return hash(str(self))
    
    
    
@dataclass
class AbsentTeacher:
    first: str
    last: str 
    length: str
    date: str
    note: str

    def __str__(self):
        return f"{self.first} {self.last} {self.length} {self.date} {self.note}"
      
@dataclass
class Message:
    number: Number
    content: str

    def __str__(self):
        return f"{self.number} {self.content}"

@dataclass
class Classes(dict):

    def __init__(self, classes = {}):
        self.classes: dict[Teacher: set(Student)] = classes
    
    def __str__(self):
        string = ""
        for teacher in self.classes:
            string += f"{teacher}:\n"
            for student in self.classes[teacher]:
                string += f"\t{student.first} {student.last}\n"
        return string

    def __iter__(self):
        yield from self.classes.keys()

    def __getitem__(self, key):
        if key in self.classes:
            return self.classes[key]
        raise KeyError(f"{key} not in classes")
    
    def __setitem__(self, key, value):
        self.classes[key] = value
    
    def __delitem__(self, key):
        del self.classes[key]
    
    def __contains__(self, item):
        return item in self.classes.keys()
    
@dataclass
class Directory:
    def __init__(self, directory = {}):
        self.directory: dict[Number: Student] = directory

    def __str__(self):
        string = ""
        for number in self.directory:
            string += f"{number}: {self.directory[number].first} {self.directory[number].last}\n"
        return string

    def __iter__(self):
        yield from self.directory.keys()
    
    def __getitem__(self, key):
        return self.directory[key]
    
    def __setitem__(self, key, value):
        self.directory[key] = value
    
    def __delitem__(self, key):
        del self.directory[key]
    
    def __contains__(self, item):
        return item in self.directory.keys()
