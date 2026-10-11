import json
from pathlib import Path

from kakaw.models import Assignment, CourseClass, Enrollment, Instance, Room, Student
from kakaw.models.constants import (
    DAY_END_MINUTES,
    DAY_START_MINUTES,
    DAYS,
    MINUTES_PER_SKS,
    PRIORITY_WEIGHT,
    START_GRID_MINUTES,
    minutes_to_hhmm,
)


class Parser:
    """Baca file JSON instance menjadi `Instance` tervalidasi."""

    def __init__(self, json_file_path: str | Path) -> None:
        self.json_file_path = Path(json_file_path)
        self.data: dict = self.load_json()

    def load_json(self) -> dict:
        try:
            with self.json_file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Error: File {self.json_file_path} not found"
            ) from None
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Error: Invalid JSON in {self.json_file_path} "
                f"({error.msg} at line {error.lineno})"
            ) from error
        return data

    def parse(self) -> Instance:
        rooms = self._parse_rooms(self.data)
        classes = self._parse_classes(self.data, rooms)
        students = self._parse_students(self.data, classes)
        self._check_class_capacity(students, classes, rooms)
        return Instance(rooms=rooms, classes=classes, students=students)

    def _parse_rooms(self, data: dict) -> list[Room]:
        rooms: list[Room] = []
        seen: set[str] = set()
        for entry in self._require_list(data, "ruangan"):
            room_id = self._require_str(entry, "kode", "ruangan")
            if room_id in seen:
                raise ValueError(f"Kode ruangan duplikat: {room_id}")
            seen.add(room_id)
            capacity = self._require_positive_int(
                entry, "kapasitas", f"ruangan {room_id}"
            )
            rooms.append(Room(id=room_id, capacity=capacity))
        if not rooms:
            raise ValueError("Instance tidak punya ruangan")
        return rooms

    def _parse_classes(self, data: dict, rooms: list[Room]) -> list[CourseClass]:
        room_ids = {room.id for room in rooms}
        classes: list[CourseClass] = []
        seen: set[str] = set()
        for entry in self._require_list(data, "kelas"):
            class_id = self._require_str(entry, "kode", "kelas")
            if class_id in seen:
                raise ValueError(f"Kode kelas duplikat: {class_id}")
            seen.add(class_id)
            sks = self._require_positive_int(entry, "sks", f"kelas {class_id}")
            initial = self._parse_initial(entry, class_id, sks, room_ids)
            classes.append(CourseClass(id=class_id, sks=sks, initial=initial))
        if not classes:
            raise ValueError("Instance tidak punya kelas")
        return classes

    def _parse_initial(
        self, entry: dict, class_id: str, sks: int, room_ids: set[str]
    ) -> Assignment:
        raw = entry.get("jadwal_awal")
        if not isinstance(raw, dict):
            raise ValueError(f"Kelas {class_id}: 'jadwal_awal' harus objek")
        day = raw.get("hari")
        if day not in DAYS:
            raise ValueError(f"Kelas {class_id}: hari tidak dikenal: {day!r}")
        start = self._to_minutes(class_id, raw.get("mulai"))
        if start + MINUTES_PER_SKS * sks > DAY_END_MINUTES:
            raise ValueError(f"Kelas {class_id}: jadwal awal selesai setelah 18:00")
        room_id = raw.get("kode_ruangan")
        if room_id not in room_ids:
            raise ValueError(f"Kelas {class_id}: ruangan tidak dikenal: {room_id!r}")
        return Assignment(day=day, start=start, room_id=room_id)

    def _parse_students(self, data: dict, classes: list[CourseClass]) -> list[Student]:
        class_ids = {course_class.id for course_class in classes}
        students: list[Student] = []
        seen: set[str] = set()
        for entry in self._require_list(data, "mahasiswa"):
            student_id = self._require_str(entry, "nrp", "mahasiswa")
            if student_id in seen:
                raise ValueError(f"NRP duplikat: {student_id}")
            seen.add(student_id)
            enrolled = entry.get("kelas")
            priorities = entry.get("prioritas")
            if not isinstance(enrolled, list) or not isinstance(priorities, list):
                raise ValueError(
                    f"Mahasiswa {student_id}: 'kelas' dan 'prioritas' harus list"
                )
            if len(enrolled) != len(priorities):
                raise ValueError(
                    f"Mahasiswa {student_id}: panjang 'kelas' dan 'prioritas' berbeda"
                )
            seen_classes: set[str] = set()
            enrollments: list[Enrollment] = []
            for class_id, priority in zip(enrolled, priorities, strict=True):
                if class_id not in class_ids:
                    raise ValueError(
                        f"Mahasiswa {student_id}: kelas tidak dikenal: {class_id!r}"
                    )
                if class_id in seen_classes:
                    raise ValueError(
                        f"Mahasiswa {student_id}: kelas duplikat: {class_id}"
                    )
                seen_classes.add(class_id)
                if (
                    not isinstance(priority, int)
                    or isinstance(priority, bool)
                    or priority not in PRIORITY_WEIGHT
                ):
                    raise ValueError(
                        f"Mahasiswa {student_id}: prioritas {priority!r} bukan 1..4"
                    )
                enrollments.append(Enrollment(class_id=class_id, priority=priority))
            students.append(Student(id=student_id, enrollments=tuple(enrollments)))
        return students

    @staticmethod
    def _check_class_capacity(
        students: list[Student],
        classes: list[CourseClass],
        rooms: list[Room],
    ) -> None:
        counts = {course_class.id: 0 for course_class in classes}
        for student in students:
            for enrollment in student.enrollments:
                counts[enrollment.class_id] += 1
        max_capacity = max(room.capacity for room in rooms)
        for class_id, count in counts.items():
            if count > max_capacity:
                raise ValueError(
                    f"Kelas {class_id}: {count} mahasiswa > kapasitas ruangan terbesar "
                    f"{max_capacity}"
                )

    @staticmethod
    def _to_minutes(class_id: str, value: object) -> int:
        if not isinstance(value, str) or len(value) != 5 or value[2] != ":":
            raise ValueError(f"Kelas {class_id}: format waktu tidak valid: {value!r}")
        hours, minutes = value[:2], value[3:]
        if not (hours.isdigit() and minutes.isdigit()):
            raise ValueError(f"Kelas {class_id}: format waktu tidak valid: {value!r}")
        total = int(hours) * 60 + int(minutes)
        if (
            total < DAY_START_MINUTES
            or (total - DAY_START_MINUTES) % START_GRID_MINUTES != 0
        ):
            raise ValueError(
                f"Kelas {class_id}: mulai {value} di luar grid {START_GRID_MINUTES} menit "
                f"dari {minutes_to_hhmm(DAY_START_MINUTES)}"
            )
        return total

    @staticmethod
    def _require_list(container: dict, key: str, context: str = "root") -> list:
        value = container.get(key)
        if not isinstance(value, list):
            raise ValueError(f"{context}: '{key}' harus list")
        return value

    @staticmethod
    def _require_str(container: dict, key: str, context: str) -> str:
        value = container.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"{context}: '{key}' harus string tidak kosong")
        return value

    @staticmethod
    def _require_positive_int(container: dict, key: str, context: str) -> int:
        value = container.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError(f"{context}: '{key}' harus bilangan bulat positif")
        return value
