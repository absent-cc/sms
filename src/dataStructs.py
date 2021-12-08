from dataclasses import dataclass

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
    
    def __iter__(self):
            yield self.A
            yield self.B
            yield self.C
            yield self.D
            yield self.E
            yield self.F
            yield self.G

    # Creates a mapper dictionary that maps blocks to teachers
    @property
    def mapper(self):
        return {
            "A": self.A,
            "B": self.B,
            "C": self.C,
            "D": self.D,
            "E": self.E,
            "F": self.F,
            "G": self.G
        }

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
class Classes:
    classes: dict[Teacher: set()]

    def __init__(self, classes = {}):
        self.classes = classes
    
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
        return self.classes[key]
    
    def __setitem__(self, key, value):
        self.classes[key] = value
    
    def __delitem__(self, key):
        del self.classes[key]
    
@dataclass
class Directory:
    directory: dict[Number: Student]

    def __init__(self, directory = {}):
        self.directory = directory

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
