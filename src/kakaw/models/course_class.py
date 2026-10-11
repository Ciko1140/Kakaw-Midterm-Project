from .assignment import Assignment
from .constants import MINUTES_PER_SKS


class CourseClass:
    """Kelas mata kuliah: SKS dan jadwal awal."""

    def __init__(self, id: str, sks: int, initial: Assignment):
        self.id = id
        self.sks = sks
        self.initial = initial

    @property
    def duration(self) -> int:
        return MINUTES_PER_SKS * self.sks
