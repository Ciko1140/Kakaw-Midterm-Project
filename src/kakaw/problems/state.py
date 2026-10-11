from collections.abc import Mapping
from copy import deepcopy

from kakaw.models import Assignment, Instance


class State:
    """Satu jadwal lengkap: pemetaan kode kelas -> Assignment."""

    def __init__(self, assignments: dict[str, Assignment] | None = None):
        self.assignments: dict[str, Assignment] = (
            {} if assignments is None else assignments
        )

    @classmethod
    def from_instance(cls, instance: Instance) -> State:
        return cls(
            {course_class.id: course_class.initial for course_class in instance.classes}
        )

    def copy(self) -> State:
        new_state = deepcopy(State(dict(self.assignments)))
        return new_state

    def replace(self, updates: Mapping[str, Assignment]) -> State:
        """State baru dengan sebagian assignment diganti; state lama tidak berubah."""
        assignments = dict(self.assignments)
        assignments.update(updates)
        return State(assignments)
