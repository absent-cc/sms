from dataclasses import dataclass

@dataclass
class Teacher:
    first: str
    last: str

    def __str__(self):
        return f"{self.first} {self.last}"

@dataclass
class Student:
    first: str
    last: str
    number: str
    schedule: [Teacher]

    def __str__(self):
        return f"{self.first} {self.last}: {self.number} {self.schedule}"

