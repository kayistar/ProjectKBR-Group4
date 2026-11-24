# Rencana Kerja — KB Interaksi Obat Batuk-Pilek (Group 4)

Disusun: 2026-11-24
Basis: audit isi `out/kb_v1.owl` (bukan klaim `logs/LOG.md`), `data/apotek/*`, `KB/ddinter_*.csv`, `data/atc/*`.

---

## 1. State saat ini

### 1.1 Angka yang terverifikasi di file

| Artefak | Isi nyata sekarang | Catatan |
| :--- | :--- | :--- |
| `out/kb_v1.owl` | 115 deklarasi kelas, 17 object property, 21 data property, 91 individu | `measure_kb_v1.tsv` masih menulis 95/11/10/86 → **basi** |
| ABox produk | 12 produk | komposisi, indikasi, efek samping, golongan, NIE, harga |
| ABox zat aktif | 31 zat (29 kurasi + triprolidine + doxylamine) | ATC/ChEBI sebagai literal, bukan hierarki |
| ABox gejala | 22 gejala × 3 kategori × 3 aksi triase | sinonim awam ditandai "draf" |
| ABox interaksi | 11 pasangan (5 Major, 6 Moderate, 0 Minor) | CSV kurasi berisi 20 |
| ABox bukti | 2 record untuk INT-009 + tingkatBukti di 11 interaksi | satu-satunya rantai bukti lengkap |
| ABox kasus pasien | 1 kasus sintetis (Actifed + Digoxin) | `q4` belum pernah dieksekusi, hasil tidak ada |
| Modul referensi | `referensi_modul.owl` (765 kelas), `enzim_modul.owl` (9), `dinto_modul.owl` (72+18), `symptom_modul.owl` (22) | semua lolos OWL 2 DL + HermiT |
| `kb_v1_lengkap.owl` | 937 kelas, 12.264 aksioma | gabungan modul + kb_v1 |
| Katalog apotek | 1.716 baris listing → 933 produk detail; 467 produk batuk/pilek unik | `perlu_dilengkapi.csv` 399 baris |
| DDInter (7 CSV) | 210.359 pasangan, 3.484 obat; 164 pasangan di antara 31 zat kita, 55 di antaranya domain batuk-pilek × kronis | baru 20 dipakai |
| ATC | 1.320 baris level 1–4; 17 kode level-4 bisa diturunkan dari 31 zat | belum dipakai untuk aturan |

### 1.2 Kelemahan struktural (bukan sekadar kosmetik)

1. **ABox di-hardcode.** `scrape/build_kb_v1.py` menulis 12 produk sebagai literal Python, termasuk `classes=[...]`, `kandungan=[...]`, `efeksamping=[...]`; `sheet2_interaksi.csv` (20 baris) tidak dibaca, hanya 11 interaksi literal.
2. **Kesimpulan aturan sudah di-assert manual.** `_AH1Product` ↔ Mengantuk cocok 7/7, `_DekongestanProduct` ↔ Palpitasi 6/6 → HermiT hanya mengecek konsistensi, tidak menambah inferensi. `robot reason` dipanggil tanpa `--output` sehingga inferensi tidak pernah materialisasi.
3. **Farmakokinetik tidak terhubung.** `dimetabolismeOleh` cuma deklarasi properti (baris 134); nol triple zat→enzim. `diproduksiOleh` juga properti mati.
4. **Regulasi tanpa konsekuensi.** `memilikiGolongan` + `nomorBPOM` terisi, tapi tidak ada satu pun aturan yang memakainya.
5. **Aturan tidak saling eksklusif.** R-01 dan R-02 tidak `disjointWith`, sehingga satu produk bisa masuk dua kelas; tabel manual pun tidak sepakat dengan aturan (Sanmol = paracetamol tapi diberi `ObatPilekMurni`; Komix/Alpara/OB Combi/Promedex berisi antitusif tanpa dekongestan tapi tidak diberi `ObatBatukMurni`).
6. **Output query basi/duplikat.** `q1_result.csv` 36 baris untuk 12 produk, dengan 6 varian label golongan (label `id` + `en` tanpa `FILTER lang`), dan nilainya dari versi ontology lama.
7. **Tidak reproducible.** Path absolut Windows di 4 skrip (`d:\UNS\...`), tidak ada `requirements.txt`, README 1 baris, dan `KB/chebi.owl`/`KB/dron.owl` di-gitignore (tidak bisa build dari nol).
8. **Batas domain.** 0 dari 467 produk katalog adalah obat keras → mesin interaksi tidak punya bahan di sisi pasar; herbal 1 produk; kondisi pasien hanya 1 yang aktif (hipertensi).

---

## 2. Keputusan: dipertahankan / dibuang / diimprove

### 2.1 Dipertahankan (sudah benar, jangan diutak-atik)

- 5 modul referensi + checksum-nya (`out/*_modul.owl`), termasuk `dinto_modul.owl` dengan 18 object property.
- 22 gejala SYMP + kategori + aksi triase + sinonim awam (`data/symptoms/symptoms_selected.csv`, `scrape/collect_symptoms.py`).
- 31 zat aktif + ATC/ChEBI/peran farmakologis (`data/curation/sheet1_zat_aktif.csv`).
- 20 pasangan interaksi terkurasi beserta mekanisme, efek klinis, rekomendasi, tingkat bukti (`data/interactions/curated_drug_interactions.csv`).
- Disiplin bukti: `evidence_interaksi.csv` (kutipan + klaim + batas bukti) dan `SumberBukti`.
- Pipeline validasi: `robot reason --reasoner HermiT` + `validate-profile --profile DL`, dan format `logs/LOG.md` (checksum, ukuran, hasil uji).
- Katalog 933 produk + pemisahan batuk/pilek (`produk_detail.csv`, `produk_batuk.csv`, `produk_pilek.csv`).
- 12 produk ABox — tetap dipakai, tapi sebagai **fixture uji**, bukan sebagai isi KB final.

### 2.2 Dibuang

| Yang dibuang | Alasan |
| :--- | :--- |
| Literal `classes=[...]`, `efeksamping=[...]`, `indikasi=[...]` per produk di `build_kb_v1.py` | diganti inferensi + turunan dari CSV |
| Properti `diproduksiOleh` | 0 assertion, digantikan literal `namaProdusen` |
| `out/test_term.owl` (737 KB) | sisa uji ekstraksi satu term |
| `scrape/generate_dataset_apotek.py`, `generate_katalog_apotek_lengkap.py`, `generate_master_apotek.py`, `scrape_obat_apotek.py` + `data/dataset_obat_apotek*.csv`, `data/dataset_master_obat_apotek_indonesia.csv` | data dummy/legacy, sudah digantikan hasil scrape asli |
| `data/dataset_obat_apotek_indonesia - Copy.csv` | duplikat identik |
| Angka 95/11/10/86 di log dan `measure_kb_v1.tsv` | tidak cocok dengan file sekarang; dihitung ulang, bukan dihapus |

### 2.3 Diimprove

- `q1_daftar_produk.rq` — tambah `FILTER (lang(?golongan)="id")`, jalankan ulang, ganti `q1_result.csv`.
- `build_kb_v1.py` — path relatif (`Path(__file__)`), baca produk dari CSV, hapus assertion turunan.
- Inferensi — `robot reason --output` ke `out/kb_v1_materialized.owl` agar hasil penalaran bisa di-query.
- `q4` — eksekusi dan simpan `out/q4_result.csv`; tambah kasus kedua (keranjang duplikasi).
- `logs/LOG.md` — tambah bagian "state terverifikasi" yang sinkron dengan file; angka dihitung oleh skrip, bukan diketik.
- README — cara jalan (unduh `chebi.owl`/`dron.owl`, ROBOT, urutan perintah) + `requirements.txt`.
- `data/atc/atc_all.csv` — dipakai untuk hierarki kelas terapi, bukan cuma arsip.

---

## 3. Todo

Kolom **Individu** = kelas/individu/properti yang sudah ada di `out/kb_v1.owl` (atau modul) dan akan dipakai. Kolom **Sumber aturan** = dari mana pengetahuannya diambil (file di repo + referensi eksternal).

### Fase 0 — Reproducibility & kebenaran artefak (prasyarat)

| ID | Todo | Individu | Sumber aturan | Output | Usaha |
| :--- | :--- | :--- | :--- | :--- | :--- |
| T0.1 | Path relatif + `requirements.txt` + README jalan | — | `scrape/*.py` | `requirements.txt`, `README.md`, skrip jalan dari Linux | S |
| T0.2 | Perbaiki `q1` + jalankan ulang semua query | `ProduktObat`, `memilikiGolongan`, `GolonganObat` | `queries/q1..q4.rq` | `q1..q4_result.csv` dengan 12/24 baris benar, tanpa duplikat label | S |
| T0.3 | Hitung ulang metrik dari file nyata | — | `out/kb_v1.owl` | `measure_kb_v1.tsv` sinkron; `logs/LOG.md` bagian baru | S |
| T0.4 | Arsipkan skrip & data legacy | — | — | folder `arsip/`, repo bersih | S |

**Kriteria selesai Fase 0:** satu perintah `python scrape/build_kb_v1.py && robot ...` bisa dijalankan ulang di mesin bersih dan menghasilkan `kb_v1.owl` yang identik (tanpa assertion manual).

### Fase 1 — Penalaran yang benar-benar bekerja (tanpa data baru)

| ID | Todo | Individu | Sumber aturan | Output | Usaha |
| :--- | :--- | :--- | :--- | :--- | :--- |
| T1.1 | Hapus kesimpulan manual; bangun ABox dari `produk_batuk.csv` (12 produk) + jalankan reasoner dengan `--output` | 12 produk, `_AH1Product`, `_DekongestanProduct`, `ProdukDenganPSE`, `ProdukKombinasiCTMDPH` | R-01…R-04, R-07, R-08 (TBox) | `out/kb_v1.owl` tanpa tipe turunan + `out/kb_v1_materialized.owl`; tabel konflik manual-vs-aturan (Sanmol, Komix) | M |
| T1.2 | `disjointWith` + perbaikan R-01/R-02 agar tidak tumpang tindih | `ObatBatukMurni`, `ObatPilekMurni`, `ObatKombinasiBatukPilek` | definisi kelas + observasi Sanmol/Komix | 12 produk terklasifikasi konsisten; 0 produk di 2 kelas saudara | S |
| T1.3 | Assert zat → enzim | 31 zat, `dimetabolismeOleh`, `CYP3A4/2D6/2C19/2C9`, `enzim_modul.owl` | `sheet1_zat_aktif.csv` kolom `enzim_terkait` + PRO | ±35 triple; query "zat yang dimetabolisme CYP3A4" mengembalikan daftar benar | S |
| T1.4 | Aktifkan R-08 di produk baru | `ProdukDenganPSE`, `kontraindikasiBagi`, `HipertensiTidakTerkontrol` | R-08 | 6 produk ber-PSE otomatis ber-kontraindikasi hipertensi setelah reasoning | S |

**Kriteria selesai Fase 1:** hasil inferensi berbeda dari tabel manual (bukti penalaran bekerja), dan 0 inconsistency di HermiT.

### Fase 2 — Pengetahuan apoteker yang belum ada (data sudah tersedia)

| ID | Todo | Individu | Sumber aturan | Output | Usaha |
| :--- | :--- | :--- | :--- | :--- | :--- |
| T2.1 | Aturan duplikasi antar produk (keranjang obat) | `KasusPasien`, `ObatPasien`, `menggunakanProdukObat`, `memilikiKandungan`, `DuplikasiTerapetik` | generalisasi R-07 + 124 produk ber-paracetamol di katalog | kelas `DuplikasiKandungan` + query keranjang; kasus uji 2 merek paracetamol | M |
| T2.2 | Aturan kelas terapi ATC-4 | `kodeATC` di 31 zat, `atc_all.csv` | 17 kode level-4 (M01A, R06A, R05C, R05D, R01B, N02B, …) | 17 kelas ATC4 + aturan "dua zat sekelas → peringatan" + query | S |
| T2.3 | Import pasangan DDInter domain proyek | `InteraksiObat`, `InteraksiMajor/Moderate/Minor`, `melibatkanZatAktif` | `KB/ddinter_code_*.csv`; 55 pasangan (1 Major, 19 Moderate, 35 Unknown), 6 sudah ada | +14 Moderate baru di ABox; 35 Unknown ditandai `Unknown` (tidak diarang); tabel per pasangan | M |
| T2.4 | Kontraindikasi kondisi per zat | `KondisiPasien` (+ subkelas baru: PJK, hipertiroid, DM, glaukoma, tukak, hamil, anak<2), `kontraindikasiBagi` | PIONAS/label (pola R-08) | ±120 triple; query "produk aman untuk hipertensi" atas 467 produk (125 berdekongestan) | M |
| T2.5 | Mekanisme DINTO sebagai relasi | `dinto_modul.owl` (`has precipitant`, `has object`, `alters`), 20 pasangan kurasi | `curated_drug_interactions.csv` kolom `dinto_mechanism` | 20 pasangan punya precipitant/object; query "semua inhibitor CYP3A4 yang jadi precipitant" | M |
| T2.6 | Batas dosis & durasi swamedikasi | data property baru `dosisMaksHari`, `durasiMaksHari`; `Gejala` | PIONAS/label (paracetamol ≤2 g/hari sudah ada di CSV interaksi) | aturan ">3 hari demam / >5 hari batuk → SegeraKeDokter"; 31 zat terdokumentasi | M |

**Kriteria selesai Fase 2:** pertanyaan "pasien hipertensi rutin digoxin mau beli obat batuk, mana yang aman?" terjawab dari 467 produk katalog, bukan 12 contoh.

### Fase 3 — Skala & evaluasi

| ID | Todo | Individu | Sumber aturan | Output | Usaha |
| :--- | :--- | :--- | :--- | :--- | :--- |
| T3.1 | Masukkan katalog ke ABox | `ProduktObat`, `memilikiKandungan`, `memilikiGolongan`, `memilikiBentukSediaan` | `produk_batuk.csv` + `produk_pilek.csv`; 336/467 bisa dipetakan (75%, estimasi substring) | `out/kb_produk_katalog.owl` + laporan coverage per zat | M-L |
| T3.2 | Normalisasi nama zat | 31 zat + sinonim | 109 produk yang tak terpetakan + `perlu_dilengkapi.csv` | tabel sinonim (`ctm`, `gg`, `ppa`, `pe`) → coverage naik | M |
| T3.3 | Evaluasi kandidat interaksi vs DDInter | `InteraksiObat`, `dimetabolismeOleh` | 164 pasangan DDInter in-domain sebagai ground truth | precision/recall kandidat hasil penalaran enzim; tabel false positive | M |
| T3.4 | Efek samping per zat (warisan) | `GejalaEfekSamping`, kelas zat | DrON (unduh ulang `dron.owl`, modul sekarang 8 term) | kelas "zat dengan efek X" → produk mewarisi tanpa diketik | L |
| T3.5 | Kasus uji pasien tambahan | `KasusPasien`, `ObatPasien`, `KondisiPasien` | sintetis, mengikuti pola `q4` | 3 kasus: hipertensi+digoxin, hamil, anak <2; `q5_result.csv` | S-M |

**Kriteria selesai Fase 3:** ≥300 produk di ABox, 0 inconsistency, laporan evaluasi interaksi punya angka, dan 4 query demo (produk, gejala, interaksi, keranjang) berjalan.

---

## 4. Yang sengaja TIDAK dikerjakan

- Standarisasi kadar herbal: 47 produk jamu/herbal, kadar alpha-mangostin tidak dicantumkan di sumber (`sheet5_produk_herbal.csv` sudah mencatat ini).
- Dosis pediatrik per BB, penyesuaian renal/hepatik, farmakogenomik CYP2D6, kategori kehamilan FDA: tidak ada di PIONAS/label yang kita pakai, butuh kurasi besar.
- Ekstraksi halaman detail 210 ribu pasangan DDInter: hanya kolom `Level` yang tersedia bulk.
- Menambah obat keras ke katalog: K24Klik menyembunyikannya (batas regulasi, bukan batas teknis).

---

## 5. Urutan eksekusi & risiko

1. Fase 0 (1–2 hari) → wajib dulu, kalau tidak semua angka di laporan tidak bisa dipertanggungjawabkan.
2. Fase 1 (2–3 hari) → inti "expert system"; risiko utama: R-01/R-02 perlu dirapikan dulu (T1.2) atau klasifikasi produk kombinasi jadi ambigu.
3. Fase 2 (3–5 hari) → nilai tambah paling besar; risiko: kualitas terjemahan label PIONAS ke kelas kondisi, perlu sampel uji manual per zat.
4. Fase 3 (3–5 hari) → skala + evaluasi; risiko: pencocokan nama zat (T3.2) menentukan semua angka coverage, jangan diklaim sebelum divalidasi sampel.

Verifikasi akhir tiap fase: `robot reason --reasoner HermiT --input ... validate-profile --profile DL` LULUS, dan semua angka di laporan dihasilkan skrip (`measure`), bukan diketik manual.
