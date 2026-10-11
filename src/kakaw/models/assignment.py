class Assignment:
    """Penempatan satu kelas: (hari, menit mulai, kode ruangan)."""

    def __init__(self, day: str, start: int, room_id: str):
        self.day = day
        self.start = start
        self.room_id = room_id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Assignment):
            return NotImplemented
        return (self.day, self.start, self.room_id) == (
            other.day,
            other.start,
            other.room_id,
        )
