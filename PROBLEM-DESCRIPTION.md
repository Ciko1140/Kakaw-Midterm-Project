# Penjadwalan Kelas Menggunakan Local Search — Panduan Tim

Dokumen ini menjelaskan problem, state, dan cara kerja solver dengan bahasa yang mudah. Untuk definisi formal dan lengkap, lihat `PROBLEM.md`.

## 1. Masalah yang diselesaikan

Kita punya daftar **kelas** (misal `IF101_A`), daftar **ruangan**, dan **mahasiswa** yang terdaftar di beberapa kelas. Tugas kita: menentukan **hari, jam mulai, dan ruangan** untuk setiap kelas supaya:

1. tidak ada mahasiswa yang bentrok jadwal,
2. tidak ada ruangan dipakai dua kelas sekaligus,
3. jadwal senyaman mungkin: ruangan cukup, tidak jauh dari jadwal awal, dan tidak banyak jam kosong.

Setiap kelas diasumsikan bertemu **sekali per minggu**. Durasi pertemuan = `SKS × 50 menit`. Kelas 2 SKS = 100 menit, 3 SKS = 150 menit.

Aturan waktu:

- Hari Senin–Jumat.
- Jam 07:00–18:00.
- Waktu mulai hanya boleh kelipatan 5 menit (07:00, 07:05, 07:10, ...).
- Antara dua kelas yang diambil mahasiswa sama, atau yang memakai ruangan sama, harus ada jeda minimal **20 menit** (kalau waktunya berdempetan di hari yang sama).

## 2. Data instance (input)

Data memuat daftar ruangan, daftar kelas, dan daftar mahasiswa. Contoh kecil:

```json
{
  "ruangan": [
    {"kode": "R1", "kapasitas": 30},
    {"kode": "R2", "kapasitas": 45}
  ],
  "kelas": [
    {"kode": "IF101_A", "sks": 2, "jadwal_awal": {"hari": "Senin", "mulai": "09:00", "kode_ruangan": "R1"}},
    {"kode": "IF101_B", "sks": 2, "jadwal_awal": {"hari": "Selasa", "mulai": "07:00", "kode_ruangan": "R2"}}
  ],
  "mahasiswa": [
    {"nrp": "S001", "kelas": ["IF101_A", "IF101_B"], "prioritas": [1, 3]},
    {"nrp": "S002", "kelas": ["IF101_A"], "prioritas": [2]}
  ]
}
```

Arti tiap bagian:

| Bagian | Arti |
|---|---|
| `kode` (ruangan) | Nama ruangan, unik |
| `kapasitas` | Jumlah kursi |
| `kode` (kelas) | Nama kelas, unik; biasanya `MATAKULIAH_KELAS`, misal `IF101_A` |
| `sks` | SKS kelas; menentukan durasi |
| `jadwal_awal` | Posisi awal kelas sebelum dioptimalkan |
| `nrp` (mahasiswa) | Nama/identitas mahasiswa, unik |
| `kelas` (mahasiswa) | Daftar kelas yang diambil mahasiswa itu |
| `prioritas` (mahasiswa) | Daftar prioritas sejajar dengan `kelas`: `prioritas[i]` berlaku untuk `kelas[i]` |
| `prioritas` | 1–4; makin kecil makin penting, makin mahal kalau jadwalnya dipindah |

## 3. State: apa yang sebenarnya berubah

**State = satu jadwal lengkap untuk semua kelas dalam satu minggu.**

Bayangkan satu tabel:

| Kelas | Hari | Mulai | Ruangan |
|---|---|---|---|
| IF101_A | Senin | 09:20 | R2 |
| IF101_B | Selasa | 07:00 | R1 |
| ... | ... | ... | ... |

Perhatikan:

- Setiap kelas muncul **tepat satu kali** di tabel.
- Isi tabel = hari, jam mulai, ruangan. **Durasi tidak ikut disimpan** karena sudah otomatis dari SKS.
- Data mahasiswa, SKS, kapasitas ruangan, dan jadwal awal **bukan bagian dari state**. Data itu tetap; state hanya posisi jadwalnya.

Satu assignment ditulis sebagai `(hari, mulai, ruangan)`. Contoh:

```text
IF101_A → ("Senin", 560, "R2")
IF101_B → ("Selasa", 420, "R1")
```

`mulai` adalah menit sejak tengah malam; `560` berarti 09:20.

Tiga istilah yang sering tertukar:

- **Lengkap** — semua kelas sudah dapat jadwal.
- **Valid** — tiap jadwal masuk aturan: hari dan ruangan dikenal, mulai kelipatan 5 menit, selesai ≤ 18:00.
- **Layak** — tidak ada bentrok mahasiswa dan tidak ada bentrok ruangan.

Jadwal awal biasanya lengkap dan valid, tetapi **belum tentu layak**. Semua kelas bisa saja ditaruh pada hari dan jam yang sama, sehingga bentrok di mana-mana. Tugas solver: mengubah state sampai layak dan penaltinya kecil.

## 4. Penalti: cara kita menilai jadwal

Ada penalti **keras** (tidak boleh) dan penalti **lunak** (sebaiknya dihindari).

### 4.1 Penalti keras

Dihitung per pasangan kelas yang waktunya berdempetan (selisih kurang dari 20 menit) di hari yang sama:

| Kejadian | Hitungan |
|---|---|
| Dua kelas berbagi mahasiswa dan waktunya berdempetan | Setiap mahasiswa bersama dihitung 1 |
| Dua kelas memakai ruangan sama dan waktunya berdempetan | Dihitung 1 per pasangan |

Jadwal disebut **layak** kalau kedua angka ini nol.

### 4.2 Penalti lunak

| Kejadian | Hitungan |
|---|---|
| Ruangan kekurangan kursi | Jumlah kursi kurang × SKS kelas |
| Kelas pindah hari/jam dari jadwal awal | Total bobot prioritas mahasiswa kelas itu (pindah ruangan saja tidak dihitung) |
| Mahasiswa punya jam kosong | Menit kosong dikurangi buffer 20 menit, dibagi 50 |

Bobot prioritas untuk perpindahan: prioritas 1 = 1,25; prioritas 2 = 1,00; prioritas 3 = 0,75; prioritas 4 = 0,50.

### 4.3 Cara menggabungkan

Kita pakai satu angka supaya mudah dibandingkan:

```text
F = W × (jumlah penalti keras) + (total penalti lunak)
```

`W` dibuat sangat besar: `W = batas atas penalti lunak + 1`. Akibatnya, mengurangi **satu** bentrok selalu lebih menguntungkan daripada menghilangkan **semua** penalti lunak sekaligus. Ini memaksa solver berburu jadwal layak dulu, baru merapikan kenyamanan.

## 5. Successor: langkah yang boleh diambil

Successor (tetangga) adalah jadwal baru yang didapat dari jadwal sekarang lewat **satu perubahan kecil**. Ada dua gerakan.

### 5.1 Pindah satu kelas

Ambil satu kelas, ganti jadwalnya:

- boleh ganti hari saja,
- boleh ganti jam saja,
- boleh ganti ruangan saja,
- boleh ganti semuanya sekaligus.

```text
Sebelum:  IF101_A → Senin, 09:20, R2
Sesudah:  IF101_A → Rabu, 13:00, R5
Kelas lain: tidak berubah
```

Jam baru harus tetap kelipatan 5 menit dan kelas harus selesai ≤ 18:00.

### 5.2 Tukar waktu dua kelas

Ambil dua kelas, tukar hari dan jam mulainya. Ruangan tetap milik masing-masing:

```text
Sebelum:  IF101_A → Senin, 09:20, R2
          IF101_B → Selasa, 07:00, R1

Sesudah:  IF101_A → Selasa, 07:00, R2
          IF101_B → Senin, 09:20, R1
```

Catatan: tukar waktu tidak mengubah ruangan.

### 5.3 Berapa banyak tetangga?

Untuk setiap kelas, kandidat "pindah" bisa ribuan: (5 hari) × (puluhan pilihan jam) × (jumlah ruangan). Belum lagi pasangan kelas untuk ditukar.

## 6. Ringkasan istilah

| Istilah | Arti singkat |
| --- | --- |
| State | Satu jadwal lengkap semua kelas |
| Successor / neighbor | Jadwal baru hasil satu perubahan kecil |
| Layak (feasible) | Tidak ada bentrok mahasiswa dan ruangan |
| Penalti keras | Bentrok; wajib nol |
| Penalti lunak | Kenyamanan: kapasitas, pindah jadwal, jam kosong |
| Relocate | Memindahkan satu kelas |
| Swap | Menukar waktu dua kelas |

## 7. Referensi Pseudocode Algoritma
[Steepest Ascent Hill Climbing](https://github.com/aimacode/aima-pseudocode/blob/master/md/Hill-Climbing.md)
[Simulated Annealing](https://github.com/aimacode/aima-pseudocode/blob/master/md/Simulated-Annealing.md)
[Genetic Algorithm](https://github.com/aimacode/aima-pseudocode/blob/master/md/Genetic-Algorithm.md)
