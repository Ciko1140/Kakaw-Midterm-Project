from .course_class import CourseClass
from .room import Room
from .student import Student


class Instance:
    """Data tetap satu instance. Urutan list mengikuti urutan di file."""

    def __init__(
        self,
        rooms: list[Room],
        classes: list[CourseClass],
        students: list[Student],
    ):
        self.rooms = rooms
        self.classes = classes
        self.students = students
