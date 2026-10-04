# Ketimpangan Pembangunan Antarprovinsi di Indonesia, 2022

Proyek UAS mata kuliah **Visualisasi Data dan Informasi**

**Penyusun:** [Alifia Deanita], NIM [222312960], Kelas [3SD1]

## Tautan

- **Aplikasi (publik, tanpa login):** https://ketimpangan-2022.streamlit.app/
- **Repositori:** repositori GitHub ini

> Aplikasi dihosting di Streamlit Community Cloud (gratis). Aplikasi yang lama tidak dikunjungi dapat "tertidur". Jika muncul layar bertuliskan aplikasi tertidur, klik tombol untuk membangunkannya dan tunggu beberapa saat.

## Pertanyaan dan alur cerita

Aplikasi menjawab satu pertanyaan besar, *seberapa timpang pembangunan antarprovinsi di Indonesia?*, melalui tiga bagian:

1. **Di mana ekonomi terkumpul?** PDRB menurut lapangan usaha: Indonesia, pulau, provinsi, lapangan usaha.
2. **Apakah ekonomi besar berarti lebih sejahtera?** Profil sepuluh indikator pembangunan 34 provinsi.
3. **Ke mana orang berpindah?** Migrasi risen antarprovinsi (Juni 2017 sampai Juni 2022).

## Topik dan teknik visualisasi (3 dari 6 topik)

| Topik | Teknik | Interaksi |
|---|---|---|
| Data berhierarki | Treemap dan sunburst (4 tingkat, 619 simpul). Ukuran = PDRB, warna = PDRB per kapita (skala log) | Drill-down dengan breadcrumb (treemap), tooltip |
| Data berdimensi tinggi | PCA, parallel coordinates, heatmap terklaster (10 variabel, 34 provinsi) | Brushing dan linking: seleksi kotak/lasso pada scatter PCA menyorot provinsi di parallel coordinates, heatmap, dan matriks OD; slider jumlah klaster; tooltip |
| Data aliran/pergerakan | Sankey (antarpulau dan antarprovinsi) dan matriks asal-tujuan (OD) | Filter provinsi asal/tujuan, filter N aliran terbesar, pilihan skala warna matriks, tooltip |

Palet warna: Viridis (hierarki), Okabe-Ito (kelompok klaster), CARTO Safe (kelompok pulau), Cividis (matriks OD), dan skala merah-biru untuk z-score. Semuanya dipilih agar ramah buta warna.

## Data

Seluruh data utama bersumber dari **BPS**. Catatan lengkap ada di [`data/processed/sumber_data.csv`](data/processed/sumber_data.csv) (pemisah titik koma).

| Variabel | Judul tabel/publikasi | Tahun data | Satuan | URL | Diakses |
|---|---|---|---|---|---|
| Indeks Pembangunan Manusia (IPM) | Indeks Pembangunan Manusia Menurut Provinsi | 2022 | indeks | [tautan](https://www.bps.go.id/id/statistics-table/3/V25GaFNHaExaMnhITm1sWmRrUlJZelJzYUc1SGR6MDkjMyMwMDAw/indeks-pembangunan-manusia-menurut-provinsi.html?year=2022) | 03/10/2026 |
| Persentase penduduk miskin | Jumlah dan Persentase Penduduk Miskin Menurut Provinsi | 2022 (Maret) | % | [tautan](https://www.bps.go.id/id/statistics-table/3/UkVkWGJVZFNWakl6VWxKVFQwWjVWeTlSZDNabVFUMDkjMw==/jumlah-dan-persentase-penduduk-miskin-menurut-provinsi-2022.html?year=2022) | 03/10/2026 |
| Tingkat Pengangguran Terbuka (TPT) | Tingkat Pengangguran Terbuka (TPT) dan Tingkat Partisipasi Angkatan Kerja (TPAK) Menurut Provinsi | 2022 (Agustus) | % | [tautan](https://www.bps.go.id/id/statistics-table/3/V2pOVWJWcHJURGg0U2pONFJYaExhVXB0TUhacVFUMDkjMw==/tingkat-pengangguran-terbuka--tpt--dan-tingkat-partisipasi-angkatan-kerja--tpak--menurut-provinsi--2022.html?year=2022) | 03/10/2026 |
| PDRB per kapita | Produk Domestik Regional Bruto per Kapita Atas Dasar Harga Berlaku Menurut Provinsi (ribu rupiah) | 2022 | ribu rupiah | [tautan](https://www.bps.go.id/id/statistics-table/3/YWtoQlRVZzNiMU5qU1VOSlRFeFZiRTR4VDJOTVVUMDkjMw==/produk-domestik-regional-bruto-per-kapita-atas-dasar-harga-berlaku-menurut-provinsi--ribu-rupiah---2022.html?year=2022) | 03/10/2026 |
| Pengeluaran per kapita disesuaikan | [Metode Baru] Pengeluaran per Kapita Disesuaikan | 2022 | ribu rupiah/orang/tahun | [tautan](https://www.bps.go.id/id/statistics-table/2/NDE2IzI=/-metode-baru--pengeluaran-per-kapita-disesuaikan.html) | 03/10/2026 |
| Migrasi risen antarprovinsi | Statistik Migrasi Indonesia Hasil Long Form Sensus Penduduk 2020 (Tabel 5.3 dan Tabel 7) | 2023 (terbit) | jiwa | [tautan](https://www.bps.go.id/id/publication/2023/07/20/97c956dd7ff3ece924911115/statistik-migrasi-indonesia-hasil-long-form-sensus-penduduk-2020.html) | 03/10/2026 |
| Rata-rata lama sekolah | Rata-Rata Lama Sekolah Penduduk Umur 15 Tahun ke Atas Menurut Provinsi | 2022 | tahun | [tautan](https://www.bps.go.id/id/statistics-table/2/MTQyOSMy/rata-rata-lama-sekolah-penduduk-umur-15-tahun-ke-atas-menurut-provinsi.html) | 03/10/2026 |
| Gini ratio | Gini Ratio Menurut Provinsi dan Daerah | 2022 (Semester 1/Maret, kota+desa) | indeks | [tautan](https://www.bps.go.id/id/statistics-table/2/OTgjMg==/gini-ratio-menurut-provinsi-dan-daerah.html) | 03/10/2026 |
| Akses sanitasi layak | Persentase Rumah Tangga menurut Provinsi dan Memiliki Akses terhadap Sanitasi Layak | 2022 | % | [tautan](https://www.bps.go.id/id/statistics-table/2/ODQ3IzI=/persentase-rumah-tangga-menurut-provinsi-dan-memiliki-akses-terhadap-sanitasi-layak.html) | 03/10/2026 |
| Akses air minum layak | Persentase Rumah Tangga yang Memiliki Akses terhadap Sumber Air Minum Layak Menurut Provinsi dan Klasifikasi Desa | 2022 (kota+desa) | % | [tautan](https://www.bps.go.id/id/statistics-table/2/ODU0IzI=/persentase-rumah-tangga-yang-memiliki-akses-terhadap-sumber-air-minum-layak-menurut-provinsi-dan-klasifikasi-desa--persen-.html) | 03/10/2026 |
| Penduduk 5+ menurut status migrasi risen | Jumlah Penduduk Berumur 5 Tahun ke Atas menurut provinsi, jenis kelamin, dan migrasi risen **[Jumlah Penduduk Berumur 5 Tahun ke Atas menurut Wilayah, Status Migrasi Risen, dan Jenis Kelamin, INDONESIA, 2022]** | 2022 | jiwa | [tautan](https://sensus.bps.go.id/topik/tabular/sp2022/171/0/0) | 03/10/2026 |
| PDRB menurut lapangan usaha | Produk Domestik Regional Bruto Provinsi-Provinsi di Indonesia Menurut Lapangan Usaha 2020-2024, Tabel 87 | 2022 | persen dan miliar Rp | [tautan](https://www.bps.go.id/id/publication/2025/04/11/95c729ee8c6fb5e2cb86b00f/produk-domestik-regional-bruto-provinsi-provinsi-di-indonesia-menurut-lapangan-usaha-2020-2024.html) | 03/10/2026 |
| Umur harapan hidup saat lahir (UHH), laki-laki dan perempuan | Umur Harapan Hidup saat lahir menurut Provinsi dan Jenis Kelamin (menggunakan UHH hasil SP2020 LF) | 2022 | tahun | [tautan](https://www.bps.go.id/id/statistics-table/2/MjI3MyMy/umur-harapan-hidup-saat-lahir-menurut-provinsi-dan-jenis-kelamin--menggunakan-uhh-hasil-sp2020-lf-.html) | 04/10/2026 |

## Pengolahan data

Skrip pengolahan ada di akar repositori:

- `prep_migrasi.py`: mengekstrak Tabel 5.3 (matriks asal-tujuan migrasi risen) dan Tabel 7 (migrasi masuk, keluar, neto) dari PDF publikasi BPS.
- `prep_indikator.py`: menggabungkan file mentah indikator provinsi, menghitung rasio migrasi per 1.000 penduduk berumur 5+ tahun, dan menulis laporan pengecekan.

Hasilnya ada di `data/processed/`. Berkas PDF publikasi tidak disertakan di repositori; unduh dari tautan BPS pada tabel di atas dan letakkan di `data/raw/` bila ingin menjalankan ulang `prep_migrasi.py`.

### Keputusan dan catatan metodologi

- **Tahun acuan 2022** dengan **34 provinsi** (sebelum pemekaran Papua), agar seragam dengan data migrasi.
- **Migrasi risen**: perpindahan antarprovinsi selama Juni 2017 sampai Juni 2022, dari Long Form Sensus Penduduk 2020 yang dicacah Juni 2022. Data berasal dari sampel rumah tangga, sehingga merupakan estimasi.
- **Migrasi per 1.000 penduduk** memakai penduduk berumur 5+ tahun sebagai penyebut. Migrasi neto dihitung dari aliran antarprovinsi saja (tanpa migran dari luar negeri).
- Kemiskinan memakai kondisi **Maret 2022**, TPT memakai **Agustus 2022**, dan Gini ratio memakai **Maret 2022** (kota+desa).
- Rata-rata lama sekolah adalah untuk penduduk **15 tahun ke atas** (bukan 25+ seperti komponen IPM).
- **UHH** pada unduhan hanya tersedia per jenis kelamin; variabel analisis adalah **rata-rata sederhana** laki-laki dan perempuan (aproksimasi UHH gabungan).
- Nilai PDRB per lapangan usaha adalah **turunan**: persen distribusi dikali total PDRB provinsi (persen disalin dari publikasi BPS).
- Pada PCA dan heatmap, semua variabel distandarkan (z-score) dan PDRB per kapita ditransformasi log10.

## Menjalankan di komputer sendiri

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

## Struktur repositori

```
app.py               # aplikasi Streamlit (3 bagian)
prep_migrasi.py      # ekstraksi tabel migrasi dari PDF BPS
prep_indikator.py    # penggabungan indikator dan rasio migrasi
requirements.txt
data/
  processed/         # data terolah yang dibaca aplikasi
  raw/               # data mentah (tidak semua disertakan)
```

## Keterbatasan

- Data satu titik waktu (2022); tidak menampilkan tren.
- Warna pada tingkat lapangan usaha di bagian 1 sama dengan warna provinsinya (PDRB per kapita provinsi), sehingga di dalam satu provinsi warnanya seragam.
- Busur kecil pada sunburst dan kotak kecil pada treemap sulit dibaca; nilai lengkap tersedia di tooltip.
- UHH gabungan berupa aproksimasi, dan klaster bergantung pada jumlah kelompok yang dipilih.
- Korelasi pada analisis multivariat bukan hubungan sebab-akibat.

## Deklarasi penggunaan AI

Pengerjaan proyek ini dibantu alat berbasis AI (Claude, Anthropic) untuk diskusi perancangan, penulisan dan perbaikan kode (aplikasi Streamlit), serta pengecekan data. Penulis menyiapkan dan memeriksa data, menjalankan dan menguji aplikasi, dan bertanggung jawab penuh atas seluruh isi proyek.

## Lisensi dan sumber

Data bersumber dari Badan Pusat Statistik (BPS) dan digunakan untuk keperluan akademik. Hak atas data tetap pada BPS.
