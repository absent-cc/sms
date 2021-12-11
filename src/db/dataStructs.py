from enum import Enum
from dataclasses import FrozenInstanceError, dataclass

class SchoolNameMapper(dict):
    def __init__(self):
        super().__init__()
        self.update({
            "NSHS": SchoolName.NEWTON_SOUTH,
            "NNHS": SchoolName.NEWTON_NORTH
        })

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

class BlockMapper(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update({
            SchoolBlock.A: "A",
            SchoolBlock.B: "B",
            SchoolBlock.C: "C",
            SchoolBlock.D: "D",
            SchoolBlock.E: "E",
            SchoolBlock.F: "F",
            SchoolBlock.G: "G",
        })

class SchoolBlock(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"

    def __str__(self) -> str:
        mapper = BlockMapper()
        return mapper[self]

@dataclass
class Student:
    number: str
    first: str
    last: str
    school: SchoolName
    grade: int
    id: int = None

    def __str__(self) -> str:
        return f"{self.first} {self.last}"

@dataclass
class Teacher:
    first: str
    last: str
    school: SchoolName
    id: int = None

    def __str__(self) -> str:
        return f"{self.first} {self.last}"

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
            SchoolBlock.A: A,
            SchoolBlock.B: B,
            SchoolBlock.C: C,
            SchoolBlock.D: D,
            SchoolBlock.E: E,
            SchoolBlock.F: F,
            SchoolBlock.G: G,
        }
    
    def __str__(self):
        return f"""A: {self.schedule[SchoolBlock.A]},
                    B: {self.schedule[SchoolBlock.B]},
                    C: {self.schedule[SchoolBlock.C]},
                    D: {self.schedule[SchoolBlock.D]},
                    E: {self.schedule[SchoolBlock.E]},
                    F: {self.schedule[SchoolBlock.F]},
                    G: {self.schedule[SchoolBlock.G]}"""
    
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