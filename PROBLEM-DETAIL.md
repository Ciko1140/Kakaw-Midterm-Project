# Penjadwalan Kelas Menggunakan Local Search

Dokumen ini mendefinisikan problem penjadwalan kelas sebagai sebuah **local search problem**: entitas dan data yang terlibat, definisi state, aturan waktu dan buffer, successor (neighborhood), dan fungsi objektif. Dokumen ini berdiri sendiri dan tidak bergantung pada implementasi tertentu.

## 1. Formulasi local search

Local search bekerja pada satu kandidat solusi dan memindahkannya ke kandidat tetangga. Untuk problem ini:

| Komponen | Isi |
|---|---|
| State | Satu jadwal mingguan lengkap: pemetaan setiap kelas ke `(hari, waktu mulai, ruangan)` |
| State awal | Jadwal awal setiap kelas dari data instance |
| Successor | Seluruh konfigurasi jadwal hasil satu move: relocate satu kelas atau swap waktu dua kelas |
| Fungsi objektif | $F(x) = W H(x) + P(x)$, diminimalkan |
| Solusi layak | State dengan $H(x) = 0$ |
| Kondisi berhenti | Hill Climbing: tidak ada neighbor yang memperbaiki. Simulated Annealing: batas iterasi atau temperatur minimum. Genetic Algorithm: jumlah generasi tercapai |

## 2. Entitas dan data instance

Himpunan dan parameter:

- $S$: himpunan kelas yang dijadwalkan, kode seperti `IF101_A`.
- $U$: himpunan mahasiswa.
- $R$: himpunan ruangan, masing-masing punya kapasitas $cap_r$.
- $D = \{\text{Senin}, \dots, \text{Jumat}\}$: hari kuliah.
- $U_s$: mahasiswa yang terdaftar di kelas $s$ beserta prioritas pendaftarannya ($1..4$).
- $k_s$: SKS kelas $s$.
- $d_s = 50 k_s$: durasi pertemuan kelas $s$ dalam menit.
- $B_s = \sum_{u \in U_s} w(\text{prioritas}_{u,s})$: bobot perpindahan kelas $s$, dengan bobot prioritas $1 \mapsto 1{,}25$, $2 \mapsto 1{,}00$, $3 \mapsto 0{,}75$, $4 \mapsto 0{,}50$.
- $x_s^0 = (hari_s^0, mulai_s^0, ruangan_s^0)$: jadwal awal kelas $s$.

Data instance memuat daftar ruangan, daftar kelas, dan daftar mahasiswa top-level. Contoh format:

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

`mahasiswa` adalah daftar top-level `{nrp, kelas[], prioritas[]}`; `prioritas[i]` berlaku untuk
`kelas[i]`, jadi kedua daftar dibaca sejajar kiri→kanan. Kelas tidak lagi memuat daftar mahasiswa.

Persyaratan validitas data:

- kode ruangan dan kode kelas unik;
- kapasitas ruangan bilangan bulat positif;
- SKS bilangan bulat positif;
- tidak ada kelas ganda di daftar kelas satu mahasiswa, dan panjang daftar kelas sama dengan panjang daftar prioritas;
- prioritas $1..4$;
- hari dan format waktu `HH:MM` dikenal;
- waktu mulai pada grid 5 menit;
- jadwal awal berakhir paling lambat 18:00;
- jumlah mahasiswa di satu kelas tidak melebihi kapasitas ruangan terbesar.

## 3. State

### 3.1 Definisi formal

Assignment satu kelas adalah triple:

$$
x_s = (hari_s, mulai_s, ruangan_s)
$$

Satu **state** $x$ adalah pemetaan lengkap yang memberi tepat satu assignment kepada setiap kelas:

$$
x = (x_s)_{s \in S}, \qquad x_s \in D \times T_s \times R
$$

dengan $T_s$ domain waktu mulai yang valid (lihat bagian 4). State adalah **satu kandidat jadwal mingguan lengkap**, bukan satu kelas, bukan data mahasiswa, dan bukan riwayat algoritma.

Contoh representasi:

```text
state["IF101_A"] = ("Senin", 560, "R2")
state["IF101_B"] = ("Selasa", 420, "R1")
```

`mulai` adalah menit sejak tengah malam; `560` berarti 09:20. Durasi tidak disimpan di state karena sudah ditentukan oleh SKS kelas. Nilai `hari` memakai string instance apa adanya: `Senin`, `Selasa`, `Rabu`, `Kamis`, `Jumat`; tidak ada mapping nama hari.

### 3.2 State vs data tetap

Data kelas, mahasiswa, SKS, kapasitas ruangan, dan jadwal awal berasal dari instance dan tidak berubah selama pencarian. Data itu dipakai untuk menghitung penalti; yang berpindah saat pencarian hanya state.

### 3.3 Lengkap, valid, dan layak

- **Lengkap:** setiap kelas mendapat tepat satu assignment.
- **Valid secara lokal:** setiap assignment memakai hari dan ruangan yang dikenal, waktu mulai pada grid 5 menit, dan pertemuan berakhir ≤ 18:00.
- **Layak:** $H(x) = 0$, yaitu tidak ada bentrok mahasiswa maupun bentrok ruangan.

Jadwal awal biasanya lengkap dan valid, tetapi belum tentu layak. Sebagai contoh, seluruh kelas dapat ditempatkan pada hari dan jam yang sama sehingga terjadi banyak bentrok. Tugas solver adalah mengubah state sampai layak dan penaltinya kecil.

## 4. Domain waktu dan relasi buffer

### 4.1 Cara membaca domain waktu

Waktu direpresentasikan dalam **menit sejak tengah malam**. Dua angka penting:

- `420` = 07:00, batas paling awal kelas boleh mulai.
- `1080` = 18:00, batas paling akhir kelas boleh **selesai**.

Domain waktu mulai kelas $s$ dengan durasi $d_s = 50 k_s$ menit adalah:

$$
T_s = \{t \in \mathbb{Z} \mid 420 \le t,\ (t - 420) \bmod 5 = 0,\ t + d_s \le 1080\}
$$

Tiga syaratnya:

1. $420 \le t$: tidak ada kelas yang mulai sebelum 07:00.
2. $(t - 420) \bmod 5 = 0$: waktu mulai harus berada di grid 5 menit dari 07:00. Nilai seperti 07:03 atau 09:23 bukan kandidat.
3. $t + d_s \le 1080$: kelas harus selesai paling lambat 18:00. Syarat ini dapat ditulis $t \le 1080 - d_s$, jadi kelas yang lebih panjang punya pilihan mulai lebih sedikit.

Himpunan kandidat ini dapat dibangkitkan dengan langkah 5 menit dari 07:00 sampai batas atas per durasi.

### 4.2 Contoh domain untuk tiap SKS

Durasi mengikuti $d_s = 50 \times \text{SKS}$:

| SKS | Durasi $d_s$ | Mulai pertama | Mulai terakhir | Batas selesai | Banyak pilihan mulai |
|---|---|---|---|---|---|
| 1 | 50 menit | 07:00 (420) | 17:10 (1030) | 18:00 | 123 |
| 2 | 100 menit | 07:00 (420) | 16:20 (980) | 18:00 | 113 |
| 3 | 150 menit | 07:00 (420) | 15:30 (930) | 18:00 | 103 |

Banyak pilihan dihitung $(\text{mulai terakhir} - 420) / 5 + 1$. Contoh untuk 2 SKS: $(980 - 420)/5 + 1 = 113$.

Deret kandidat untuk kelas 2 SKS:

```text
07:00  07:05  07:10  ...  16:10  16:15  16:20
```

Deret kandidat untuk kelas 3 SKS (berhenti lebih awal karena durasinya lebih panjang):

```text
07:00  07:05  07:10  ...  15:20  15:25  15:30
```

Contoh batas:

- Kelas 3 SKS mulai 15:30 berakhir tepat 18:00 → **valid**.
- Kelas 3 SKS mulai 15:40 berakhir 18:10 → **tidak valid**.
- Kelas 2 SKS mulai 16:20 berakhir 18:00 → **valid**.
- Kelas apa pun mulai 06:50 → **tidak valid** (sebelum 07:00).

### 4.3 Interval setengah terbuka

Pertemuan memakai interval setengah terbuka $[mulai, selesai)$ dengan $selesai_s = mulai_s + d_s$. Artinya, menit `selesai` sudah bukan milik kelas itu lagi.

Kelas 2 SKS yang mulai 09:20 menempati menit 09:20 sampai 10:59, dan selesai tepat saat menit 11:00 dimulai. Kelas lain yang mulai 11:00 karena itu **tidak overlap**; yang dihitung hanyalah jarak buffer.

### 4.4 Relasi "terlalu dekat" dan buffer 20 menit

Dua pertemuan $a$ dan $b$ dianggap **terlalu dekat** jika berada di hari yang sama dan:

$$
\operatorname{near}(a,b) \iff mulai_a < selesai_b + 20 \;\land\; mulai_b < selesai_a + 20
$$

Rumus ini setara dengan: selisih antara selesai kelas pertama dan mulai kelas kedua **kurang dari 20 menit**. Karena perbandingannya memakai tanda `<` (bukan `≤`), **jarak tepat 20 menit diperbolehkan**.

Contoh konkret. Misalkan kelas A berlangsung Senin 09:20–11:00 ($mulai_a = 560$, $selesai_a = 660$). Bandingkan dengan beberapa kemungkinan kelas B:

| Kelas B | $mulai_b$ | $selesai_b$ | `near(A,B)`? | Akibat |
|---|---|---|---|---|
| Senin 11:00–12:40 | 660 | 760 | Ya (jarak 0 menit) | bentrok |
| Senin 11:05–12:45 | 665 | 765 | Ya (jarak 5 menit) | bentrok |
| Senin 11:15–12:55 | 675 | 775 | Ya (jarak 15 menit) | bentrok |
| Senin 11:20–13:00 | 680 | 780 | Tidak (jarak tepat 20 menit) | aman |
| Senin 10:00–11:40 | 600 | 700 | Ya (overlap) | bentrok |
| Selasa 11:00–12:40 | 660 | 760 | Tidak (beda hari) | aman |

Pemeriksaan "Senin 11:20" secara manual:

```text
mulai_b < selesai_a + 20  →  680 < 660 + 20  →  680 < 680  →  false
```

Karena satu sisi sudah `false`, maka `near` bernilai false. Untuk 11:19: `679 < 680` bernilai true di kedua sisi, sehingga dianggap bentrok.

Dua sisi rumus diperlukan karena kedua kelas bisa punya durasi berbeda; arah mana pun yang jaraknya kurang dari 20 menit tetap dianggap bentrok.

Catatan: karena semua waktu mulai berada di grid 5 menit dan semua durasi kelipatan 50 menit (maka juga kelipatan 5), jarak antar dua kelas di hari yang sama selalu kelipatan 5 menit: 0, 5, 10, 15, 20, dan seterusnya. Jadi pada jadwal nyata yang valid, kasus jarak 0, 5, 10, dan 15 menit yang menjadi bentrok; jarak 20 menit ke atas aman.

### 4.5 Kapan relasi ini dipakai

Relasi `near` dipakai dua kali di objective:

- **Bentrok mahasiswa:** dua kelas dengan mahasiswa bersama tidak boleh `near` ($H_{student}$).
- **Bentrok ruangan:** dua kelas di ruangan sama tidak boleh `near` pada hari yang sama ($H_{room}$).

Relasi yang sama juga dipakai untuk menghitung **jeda kosong mahasiswa**. Untuk dua pertemuan berurutan di hari yang sama:

| Jeda | Status | Tambahan penalti |
|---|---|---|
| Overlap | bentrok keras | tidak dihitung sebagai jeda |
| Kurang dari 20 menit | bentrok keras | tidak dihitung sebagai jeda |
| Tepat 20 menit | aman | 0 |
| Lebih dari 20 menit | aman | `(jeda - 20) / 50` |

Jadi buffer 20 menit adalah batas keras, sedangkan kelebihan waktunya menjadi penalti lunak $P_{jeda}$.

## 5. Successor function (neighborhood)

Neighborhood $N(x)$ adalah himpunan state yang dicapai dari $x$ dengan satu move. Kandidat tetap harus valid secara lokal, tetapi boleh memiliki bentrok.

### 5.1 Relocate / reassign satu kelas

Pilih satu kelas $s$, lalu ganti assignment-nya dengan kombinasi hari, waktu mulai valid, dan ruangan yang valid:

$$
x'_s = (hari, t, r), \qquad hari \in D,\ t \in T_s,\ r \in R,\ x'_s \ne x_s
$$

Move ini mencakup perubahan hari, waktu, ruangan, atau kombinasinya.

### 5.2 Swap waktu dua kelas

Pilih dua kelas $s \ne t$ dengan $(hari_s, mulai_s) \ne (hari_t, mulai_t)$, lalu tukar hari dan waktu mulai keduanya; setiap kelas tetap memakai ruangannya sendiri:

$$
\begin{aligned}
x'_s &= (hari_t, mulai_t, ruangan_s) \\
x'_t &= (hari_s, mulai_s, ruangan_t)
\end{aligned}
$$

Pertukaran harus tetap menghasilkan assignment yang valid secara lokal, yaitu kedua kelas selesai paling lambat 18:00 setelah ditukar. Jika tidak, kandidat tersebut tidak boleh dimasukkan ke neighborhood.

### 5.3 Bentuk himpunan successor

$$
N(x) = N_{relocate}(x) \cup N_{swap}(x)
$$

Ukuran $N(x)$ tumbuh kuadratik-kubik terhadap jumlah kelas. Untuk satu kelas: $5 \times |T_s| \times |R| - 1$ kandidat relocate, dan $O(|S|^2)$ kandidat swap. Inilah alasan Hill Climbing satu iterasi jauh lebih mahal daripada Simulated Annealing.

### 5.4 Perbedaan cara algoritma memakai successor

- **Hill Climbing (steepest descent):** mengevaluasi **seluruh** anggota $N(x)$, memilih $x'$ dengan $F(x')$ terkecil, dan menerima hanya jika $F(x') < F(x)$.
- **Simulated Annealing:** membangkitkan **satu** successor acak per iterasi. Swap hanya dipilih jika kedua durasi masih muat setelah pertukaran; jika tidak, relocate yang dipakai. Move relocate dapat mengganti hari/waktu, atau ruangan saja.

## 6. Fungsi objektif

### 6.1 Hard violations $H$

Bentrok mahasiswa per pasangan kelas:

$$
H_{student}(x) = \sum_{\{s,t\} \subseteq S} |U_s \cap U_t| \cdot \mathbf{1}[hari_s = hari_t \land \operatorname{near}(s,t)]
$$

Bentrok ruangan per pasangan kelas:

$$
H_{room}(x) = \sum_{\{s,t\} \subseteq S} \mathbf{1}[ruangan_s = ruangan_t \land hari_s = hari_t \land \operatorname{near}(s,t)]
$$

$$
H(x) = H_{student}(x) + H_{room}(x)
$$

Jadwal layak jika $H(x) = 0$. Kapasitas ruangan **bukan** hard constraint pada model ini; kekurangan kursi dihitung sebagai penalti lunak §6.2.

### 6.2 Soft penalty $P$

$$
P(x) = P_{kapasitas}(x) + P_{perubahan}(x) + P_{jeda}(x)
$$

Kekurangan kapasitas:

$$
P_{kapasitas}(x) = \sum_{s \in S} \max(0, |U_s| - cap_{ruangan_s}) \cdot k_s
$$

Perubahan hari/waktu dari jadwal awal (perubahan ruangan saja tidak dihitung):

$$
P_{perubahan}(x) = \sum_{s \in S} B_s \cdot \mathbf{1}[(hari_s, mulai_s) \ne (hari_s^0, mulai_s^0)]
$$

Jeda kosong mahasiswa: untuk setiap mahasiswa dan hari, urutkan pertemuan; untuk setiap dua pertemuan berurutan $(a,b)$ yang tidak overlap:

$$
P_{jeda}(x) = \sum_{u \in U} \sum_{(a,b) \in Adj_u} \frac{\max(0, mulai_b - selesai_a - 20)}{50}
$$

### 6.3 Objective scalar

$$
F(x) = W \cdot H(x) + P(x), \qquad W = P_{max} + 1
$$

$P_{max}$ adalah batas atas konservatif soft penalty, dihitung dari tiga komponen:

- batas kapasitas: $\sum_s \max(0, |U_s| - \min_r cap_r) \cdot k_s$;
- batas perubahan: $\sum_s B_s$;
- batas jeda: $\sum_u \max(0, n_u - 1) \cdot (1080 - 420)/50$, dengan $n_u$ banyak kelas mahasiswa $u$.

Karena $W > P_{max}$, pengurangan satu unit pelanggaran hard selalu lebih berharga daripada seluruh soft penalty yang mungkin. Jadwal layak tetap menjadi target; objective scalar juga memberi arah perbaikan saat state awal masih infeasible.

## 7. Algoritma

Tiga solver memakai representasi state (§3), successor (§5), dan objective $F$ (§6) yang sama. Parameter default di bawah ini **final**: implementasi boleh mengeksposnya sebagai argumen, tetapi nilai defaultnya tidak boleh berbeda.

### 7.1 Steepest-Ascent Hill-Climbing

Steepest-ascent mengevaluasi **seluruh** anggota $N(x)$, memilih kandidat dengan $F$ terkecil, dan menerima kandidat itu hanya bila $F(x') < F(x)$. Pencarian berhenti saat tidak ada kandidat yang memperbaiki state sekarang (local optimum) atau saat `max_iterations` move diterima telah tercapai. Biaya satu iterasi adalah $|N(x)|$ evaluasi objective, sehingga HC jauh lebih mahal per iterasi daripada Simulated Annealing.

HC deterministik: **tidak** memakai `seed`. Limitasinya jelas: hasil akhirnya adalah local optimum, tanpa jaminan optimum global.

```text
STEEPEST-ASCENT-HILL-CLIMBING(instance, max_iterations):
    x = jadwal awal instance                     # §2, x_s^0
    iterations = 0
    riwayat = [F(x)]
    ulangi (maksimum max_iterations move diterima):
        x' = kandidat dengan F terkecil di N(x)   # tie-break di bawah
        jika F(x') < F(x):
            x = x'
            iterations = iterations + 1
            catat F(x) ke riwayat
        selain:
            berhenti                              # local optimum
    return x, riwayat F setiap move diterima
```

**Tie-break.** Kandidat dievaluasi pada urutan tetap:

- (a) relocate: kelas urut `kode` menaik; untuk tiap kelas hari `Senin` → `Jumat`, lalu `mulai` menaik, lalu ruangan urut seperti pada file instance;
- (b) swap: pasangan kelas urut indeks $i < j$.

Bila beberapa kandidat punya $F$ terkecil yang sama, yang diambil adalah kandidat **pertama** pada urutan ini.

**Parameter default.** `max_iterations = 1000`, dihitung sebagai jumlah move yang **diterima**.

**Counter.** `iterations` = jumlah move yang diterima; `evaluations` = total pemanggilan objective termasuk evaluasi state awal.

### 7.2 Simulated Annealing

Tiap iterasi membangkitkan **satu** successor acak dari $N(x)$ (§5.4), menghitung $\Delta = F(x') - F(x)$, lalu menerimanya dengan peluang $p = 1$ bila $\Delta \le 0$ dan $p = \exp(-\Delta / T)$ bila $\Delta > 0$. State terbaik-so-far dilacak terpisah dan itulah yang dikembalikan. Temperatur diturunkan $T \leftarrow \max(\rho T, 10^{-12})$ setelah setiap iterasi. Pencarian berhenti saat `max_iterations` iterasi tercapai. Pemilihan swap hanya dilakukan bila kedua durasi masih muat setelah pertukaran; jika tidak, relocate yang dipakai (§5.4).

```text
SIMULATED-ANNEALING(instance, T0, rho, max_iterations, seed):
    x = jadwal awal instance
    best = x; F_best = F(x)
    T = T0
    accepted_moves = 0
    rng = RNG(seed)
    untuk i = 1..max_iterations:
        x' = successor acak dari x               # §5.4, memakai rng
        delta = F(x') - F(x)
        jika delta <= 0 atau rng.rand() < exp(-delta / T):
            x = x'
            accepted_moves = accepted_moves + 1
        jika F(x) < F_best:
            best = x; F_best = F(x)
        catat F_best ke riwayat
        T = max(rho * T, 10^-12)
    return best, riwayat F terbaik-so-far setiap iterasi
```

**Parameter default.** `T0 = 5W` (dengan $W$ dari §6.3), `rho = 0.995`, `max_iterations = 20000`, `seed = 42`.

**Counter.** `iterations` = jumlah kandidat yang dievaluasi; `accepted_moves` dicatat terpisah.

### 7.3 Genetic Algorithm

Fitness memakai tanda terbalik: $f(x) = -F(x)$, sehingga memaksimalkan $f$ sama dengan meminimalkan $F$; seleksi memilih individu dengan $F$ terkecil.

```text
GENETIC-ALGORITHM(instance, N, G, p_c, p_m, elit, seed):
    evaluasi fitness f(x) = -F(x)            # F dari §6.3; minimisasi F == maksimisasi f
    populasi = [x0]                          # x0 = jadwal awal instance
    ulangi sampai |populasi| == N:
        tambahkan salinan x0 dengan SETIAP kelas di-relocate ke
        (hari, mulai, ruangan) acak valid (lihat §5.1) menggunakan RNG(seed)
    untuk g = 1..G:
        baru = elit individu terbaik dari populasi (berdasarkan F terkecil)
        sampai |baru| == N:
            p1 = tournament(populasi, k=3); p2 = tournament(populasi, k=3)
            anak = p1
            jika rand() < p_c: anak = crossover_uniform(p1, p2)
            anak = mutasi(anak, p_m)
            baru.append(anak)
        populasi = baru
        catat F terbaik generasi g ke riwayat
    return individu terbaik, riwayat F terbaik per generasi
```

Definisi operator:

- **Individu** = satu state lengkap, bentuknya sama dengan §3.1.
- **Fitness** = $f(x) = -F(x)$; seleksi memilih $F$ terkecil.
- **`tournament(k=3)`** = ambil 3 individu acak dari populasi, kembalikan yang $F$ terkecil.
- **`crossover_uniform(p1, p2)`** = untuk setiap kelas, ambil assignment dari `p1` atau `p2` masing-masing peluang 0,5. Hasilnya selalu state lengkap dan valid, karena tiap kelas tetap punya tepat satu assignment.
- **`mutasi(x, p_m)`** = untuk setiap kelas, dengan peluang $p_m$ ganti assignment-nya ke `(hari, mulai, ruangan)` acak valid lain (move relocate §5.1).
- **`elit`** = `elit` individu terbaik disalin utuh tanpa perubahan ke generasi berikutnya.
- Semua keacakan memakai satu RNG yang di-seed dari argumen `seed`.

**Parameter default.** `N = 50`, `G = 200`, `p_c = 0.8`, `p_m = 0.1`, `elit = 2`, `seed = 42`.

**Counter.** `iterations` = jumlah generasi yang dijalankan; `evaluations` = total evaluasi fitness; `accepted_moves` tidak berlaku untuk GA.

### 7.4 Kontrak keluaran

Kontrak ini berlaku untuk ketiga algoritma. Parameter sudah dipatok di §7.1–§7.3.

Stdout selalu memuat, dalam urutan ini:

1. satu baris ringkasan

   ```text
   algorithm=<nama> F=<float> H=<int> P=<float> feasible=<true|false> iterations=<int> evaluations=<int>
   ```

2. tabel jadwal akhir, satu baris per kelas, urut `kode` kelas menaik, dengan kolom `kode`, `hari`, `mulai` (`HH:MM`), dan `ruangan`.

Flag `--verbose` menambahkan `P_kapasitas`, `P_perubahan`, `P_jeda`, dan `accepted_moves` (hanya SA); untuk HC tambahan berupa nilai $F$ setiap move yang diterima.

Flag `--plot PATH` (opsional) menulis PNG ke `PATH` dengan sumbu-x `evaluations` dan sumbu-y $F$. Seri yang digambar: HC = $F$ setiap move diterima; SA = $F$ terbaik-so-far setiap iterasi; GA = $F$ terbaik setiap generasi. Judul gambar memuat nama algoritma.

Bila tidak ada solusi layak, solver tetap mencetak state terbaik yang ditemukan dengan `feasible=false` dan $H > 0$. Ini bukan error: exit code tetap 0.

## Referensi Algoritma

- Stuart Russell & Peter Norvig, *Artificial Intelligence: A Modern Approach*, bagian local search; [AIMA pseudocode — Hill-Climbing](https://github.com/aimacode/aima-pseudocode/blob/master/md/Hill-Climbing.md), [Simulated Annealing](https://github.com/aimacode/aima-pseudocode/blob/master/md/Simulated-Annealing.md), [Genetic Algorithm](https://github.com/aimacode/aima-pseudocode/blob/master/md/Genetic-Algorithm.md).
