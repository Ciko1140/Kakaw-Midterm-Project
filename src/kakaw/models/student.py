class Enrollment:
    """Satu kelas yang diambil mahasiswa, dengan prioritas pendaftaran 1..4."""

    def __init__(self, class_id: str, priority: int):
        self.class_id = class_id
        self.priority = priority


class Student:
    """Mahasiswa dan kelas-kelas yang diambilnya."""

    def __init__(self, id: str, enrollments: tuple[Enrollment, ...]):
        self.id = id
        self.enrollments = enrollments

    @property
    def class_ids(self) -> tuple[str, ...]:
        return tuple(enrollment.class_id for enrollment in self.enrollments)
