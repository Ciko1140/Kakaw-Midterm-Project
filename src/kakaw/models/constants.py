"""Konstanta domain penjadwalan kelas."""

DAYS: tuple[str, ...] = ("Senin", "Selasa", "Rabu", "Kamis", "Jumat")

DAY_START_MINUTES: int = 420  # 07:00, paling awal kelas boleh mulai
DAY_END_MINUTES: int = 1080  # 18:00, paling lambat kelas boleh selesai
START_GRID_MINUTES: int = 5  # grid waktu mulai
MINUTES_PER_SKS: int = 50  # durasi = 50 * sks
BUFFER_MINUTES: int = 20  # buffer keras antar pertemuan
GAP_DIVISOR: int = 50  # pembagi penalti jeda

PRIORITY_WEIGHT: dict[int, float] = {1: 1.25, 2: 1.00, 3: 0.75, 4: 0.50}


def minutes_to_hhmm(minutes: int) -> str:
    """Ubah menit sejak tengah malam menjadi "HH:MM"."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"
