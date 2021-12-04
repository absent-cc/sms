from dataclasses import dataclass

@dataclass
class AbsentTeacher:
    first: str
    last: str 
    length: str
    date: str
    note: str

    def __str__(self):
        return f"{self.first} {self.last} {self.length} {self.date} {self.note}"
