from enum import Enum
from dataclasses import FrozenInstanceError, dataclass

class SchoolName(Enum):
    NEWTON_SOUTH = "NSHS"
    NEWTON_NORTH = "NNHS"

    def __str__(self) -> str:
        if self == SchoolName.NEWTON_SOUTH:
            return "NSHS"
        elif self == SchoolName.NEWTON_NORTH:
            return "NNHS"
        else:
            return "Unknown School"

@dataclass
class Student:
    number: str
    first: str
    last: str
    school: SchoolName
    grade: int
    id: int = None

@dataclass
class Teacher:
    first: str
    last: str
    school: SchoolName
    id: int = None

@dataclass
class Schedule(dict):
    def __init__(self,  A: Teacher = None, 
                        B: Teacher = None,
                        C: Teacher = None, 
                        D: Teacher = None, 
                        E: Teacher = None, 
                        F: Teacher = None, 
                        G: Teacher = None):
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
        return f""" A: {self.schedule['A']}, 
                    B: {self.schedule['B']}, 
                    C: {self.schedule['C']}, 
                    D: {self.schedule['D']}, 
                    E: {self.schedule['E']}, 
                    F: {self.schedule['F']}, 
                    G: {self.schedule['G']}"""
    
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