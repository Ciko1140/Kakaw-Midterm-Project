import random
from collections.abc import Iterator

from kakaw.models import Assignment, Instance
from kakaw.models.constants import (
    DAY_END_MINUTES,
    DAY_START_MINUTES,
    DAYS,
    MINUTES_PER_SKS,
    START_GRID_MINUTES,
)
from kakaw.problems.objective import ObjectiveFunction
from kakaw.problems.state import State


class Problem:
    """Instance + objective + primitif domain/neighborhood untuk algoritma."""

    def __init__(self, instance: Instance) -> None:
        self.instance = instance
        self.objective = ObjectiveFunction(instance)
        self._classes = {
            course_class.id: course_class for course_class in instance.classes
        }
        self._rooms = {room.id: room for room in instance.rooms}

    def initial_state(self) -> State:
        return State.from_instance(self.instance)

    def start_domain(self, sks: int) -> tuple[int, ...]:
        """T_s (§4.1): grid 5 menit dari 07:00 sampai selesai <= 18:00."""
        last_start = DAY_END_MINUTES - MINUTES_PER_SKS * sks
        return tuple(range(DAY_START_MINUTES, last_start + 1, START_GRID_MINUTES))

    def relocate_candidates(self, state: State, class_id: str) -> Iterator[State]:
        """N_relocate untuk satu kelas (§5.1), urut tetap untuk tie-break HC."""
        current = state.assignments[class_id]
        for day in DAYS:
            for start in self.start_domain(self._classes[class_id].sks):
                for room_id in self._rooms:
                    if (day, start, room_id) == (
                        current.day,
                        current.start,
                        current.room_id,
                    ):
                        continue
                    yield state.replace({class_id: Assignment(day, start, room_id)})

    def swap_candidates(self, state: State) -> Iterator[State]:
        """N_swap semua pasangan kelas i<j (§5.2), hanya yang valid lokal."""
        class_ids = list(self._classes)
        for i in range(len(class_ids)):
            for j in range(i + 1, len(class_ids)):
                swapped = self._swapped_state(state, class_ids[i], class_ids[j])
                if swapped is not None:
                    yield swapped

    def random_relocate(self, state: State, class_id: str, rng: random.Random) -> State:
        """Relocate acak lengkap (hari/waktu/ruangan), selalu != posisi sekarang."""
        current = state.assignments[class_id]
        domain = self.start_domain(self._classes[class_id].sks)
        while True:
            candidate = Assignment(
                rng.choice(DAYS), rng.choice(domain), rng.choice(tuple(self._rooms))
            )
            if candidate != current:
                return state.replace({class_id: candidate})

    def random_room_change(
        self, state: State, class_id: str, rng: random.Random
    ) -> State:
        """Ganti ruangan saja; jika hanya satu ruangan, jatuh ke relocate penuh."""
        room_ids = tuple(self._rooms)
        if len(room_ids) < 2:
            return self.random_relocate(state, class_id, rng)
        current = state.assignments[class_id]
        room_id = rng.choice(room_ids)
        while room_id == current.room_id:
            room_id = rng.choice(room_ids)
        return state.replace(
            {class_id: Assignment(current.day, current.start, room_id)}
        )

    def random_swap(self, state: State, rng: random.Random) -> State | None:
        """Satu pasangan acak; None bila tidak valid (pemanggil pakai relocate, §5.4)."""
        class_ids = tuple(self._classes)
        if len(class_ids) < 2:
            return None
        first, second = rng.sample(class_ids, 2)
        return self._swapped_state(state, first, second)

    def _swapped_state(self, state: State, first: str, second: str) -> State | None:
        a = state.assignments[first]
        b = state.assignments[second]
        if (a.day, a.start) == (b.day, b.start):
            return None
        if b.start + self._classes[first].duration > DAY_END_MINUTES:
            return None
        if a.start + self._classes[second].duration > DAY_END_MINUTES:
            return None
        return state.replace(
            {
                first: Assignment(b.day, b.start, a.room_id),
                second: Assignment(a.day, a.start, b.room_id),
            }
        )
