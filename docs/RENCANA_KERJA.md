# Rencana Kerja v2 — KB Interaksi Obat Batuk-Pilek (Group 4)

Disusun: 2026-11-24 (revisi dari v1)
Basis: audit `out/kb_v1.owl`, `data/apotek/*`, `KB/ddinter_*.csv`, `data/atc/*`, `data/curation/*`.
Dokumen ini yang dalam diskusi disebut "todo.md".

---

## 0. Lima task final

| # | Task | Nilai bagi apoteker | Data baru | Kesiapan data |
| :--- | :--- | :--- | :--- | :--- |
| **T1** | Rekomendasi terapi personal: produk + cara pakai + peringatan kombinasi, dari kondisi pasien | inti swamedikasi | tabel aturan pakai 31 zat + tabel kontraindikasi 31 zat | sedang (aturan pakai belum ada) |
| **T2** | Alternatif lebih murah: kandungan sama / kandungan minimal | hemat biaya, hindari obat kombinasi tak perlu | turunan harga per unit | **siap** (828/933 sudah ada harga) |
| **T3** | Skrining keranjang & obat rutin: duplikasi + interaksi multi-produk | cegah dobel dosis & interaksi | 0 | **siap** (model KasusPasien + DDInter sudah ada) |
| **T4** | Substitusi aman: ganti produk karena kandungannya bermasalah untuk kondisi pasien | lindungi pasien hipertensi/BPH/glaukoma, dll | tabel kontraindikasi (sama dengan T1) | sedang |
| **T5** | Kartu edukasi & explainability: "kenapa" + sumber + bahasa awam | konseling pasien | 0 | **siap** (SumberBukti + skos:altLabel sudah ada) |

Cadangan bila butuh lebih dari 5: audit katalog (laporan kualitas data) dan evaluasi kandidat interaksi vs DDInter. Keduanya murah dan tidak butuh individu baru.

---

## 1. State saat ini (terverifikasi di file, bukan dari LOG)

| Artefak | Isi nyata | Catatan |
| :--- | :--- | :--- |
| `out/kb_v1.owl` | 115 deklarasi kelas, 17 object prop, 21 data prop, 91 individu | `measure_kb_v1.tsv` masih 95/11/10/86 → basi |
| ABox produk | 12 produk (komposisi, indikasi, efek samping, golongan, NIE, harga) | di-hardcode di `build_kb_v1.py` |
| ABox zat aktif | 31 zat; ATC/ChEBI literal | 0 relasi ke enzim |
| ABox gejala | 22 gejala × 3 kategori × 3 aksi | sinonim awam masih draf |
| ABox interaksi | 11 (5 Major, 6 Moderate); CSV kurasi 20 | R-05/R-06 sudah di-assert manual |
| ABox bukti | 2 record (INT-009) + tingkatBukti A/B | satu-satunya rantai bukti lengkap |
| Kasus pasien | 1 (Actifed + Digoxin) | `q4` belum pernah dieksekusi |
| Modul referensi | ChEBI/DrON (765 kelas), PRO (9), DINTO (72+18), SYMP (22) | semuanya OWL 2 DL + HermiT LULUS |
| Katalog | 933 detail; 467 batuk/pilek unik; **828 punya harga**, 853 punya komposisi | tanpa kolom dosis/aturan pakai |
| DDInter | 210.359 pasangan; 164 antar 31 zat kita; 55 domain batuk-pilek × kronis | baru 20 dipakai |
| ATC | 1.320 baris level 1–4; 17 kode level-4 dari 31 zat | belum dipakai aturan |

Kelemahan struktural yang relevan untuk 5 task: ABox di-hardcode, kesimpulan aturan sudah di-assert manual (HermiT tak menambah apa pun), `dimetabolismeOleh` 0 triple, R-01/R-02 tanpa `disjointWith` (Sanmol/Komix salah kelas), `q1_result.csv` basi + duplikat label, tidak ada `requirements.txt`, dan path absolut Windows di 4 skrip.

---

## 2. Batas data: yang mungkin vs yang tidak

### 2.1 Mungkin dengan data yang sudah ada

| Kebutuhan | Bahan yang ada | Catatan |
| :--- | :--- | :--- |
| Pilih produk berdasarkan keluhan | 467 produk + komposisi + 22 gejala + sinonim awam | kandidat bersih 377 (punya harga **dan** komposisi) |
| Peringatan "jangan bersama obat X" | DDInter 55 pasangan + 20 kurasi | hanya untuk 31 zat yang kita punya |
| Deteksi dobel kandungan antar produk | `memilikiKandungan` + model `KasusPasien`/`ObatPasien` | 124 produk mengandung paracetamol → risiko dobel dosis nyata |
| Deteksi dobel kelas terapi | ATC level-4 (17 kode) | "dua antihistamin / dua NSAID / dua dekongestan" |
| Kondisi pasien sebagai penentu | kelas `KondisiPasien` + pola R-08 | tinggal isi tabel kontraindikasi |
| Rekomendasi lebih murah | harga 828 produk + kemasan 933 | butuh normalisasi harga per unit |
| Penjelasan + sumber | `SumberBukti` + `tingkatBukti` + `skos:altLabel` | sudah jalan untuk 1 interaksi |
| Triase/red flag | 22 gejala × 3 aksi | biner (ya/tidak), bukan skor |

### 2.2 Tidak mungkin dengan data sekarang (jangan dijanjikan)

| Yang diminta | Kenapa tidak |
| :--- | :--- |
| Dosis per sekali pakai **per produk** ("1 sendok takar 3x sehari") | `produk_detail.csv` tidak punya kolom dosis/aturan pakai; komposisi hanya kadar per 5 mL. Yang bisa: aturan **per zat** (31 baris kurasi) |
| Dosis berbasis **berat badan** (mg/kg) | tidak ada dosis pediatrik per produk di katalog. BB hanya bisa jadi catatan, tidak mengubah angka. Jangan dipakai sebagai fitur |
| **Skor keparahan** berjenjang | tidak ada data severity; yang ada hanya red flag biner |
| Interaksi dengan obat di luar 31 zat | butuh mapping 3.484 nama DDInter; bisa, tapi bukan "manfaatkan yang ada" |
| Aturan pakai spesifik per merek (sebelum/sesudah makan) | tidak ada di sumber; hanya bisa per kelas sediaan atau per zat dari PIONAS |
| Standarisasi herbal (kadar alpha-mangostin) | tidak dicantumkan di sumber mana pun yang kita punya |
| Harga per unit untuk semua produk | `kemasan` bebas teks (`1 Dos isi 25 Strip x 4 Tablet`); 68 produk tanpa harga, 22 tanpa komposisi |

**Koreksi penting:** harga **bukan** data yang perlu ditambah — 828/933 sudah punya harga. Yang benar-benar kosong adalah **aturan pakai (dosis/frekuensi/waktu/maks hari)** dan **kontraindikasi kondisi**. Itu dua tabel kecil (31 baris masing-masing), bukan scrape baru.

---

## 3. Keputusan: dipertahankan / dibuang / diimprove

**Dipertahankan:** 5 modul referensi + checksum; 22 gejala + triase + sinonim; 31 zat + ATC/ChEBI/peran; 20 interaksi kurasi + disiplin bukti (`SumberBukti`); pipeline HermiT + `validate-profile`; katalog 933 + pemisahan batuk/pilek; 12 produk ABox (turun peran jadi fixture uji).

**Dibuang:** literal `classes`/`efeksamping`/`indikasi` per produk; properti mati `diproduksiOleh`; `out/test_term.owl`; 4 skrip generator legacy (`generate_dataset_apotek.py`, `generate_katalog_apotek_lengkap.py`, `generate_master_apotek.py`, `scrape_obat_apotek.py`) + CSV dummy-nya; `dataset_obat_apotek_indonesia - Copy.csv`; angka 95/11/10/86 di log (dihitung ulang).

**Diimprove:** `q1` (tambah `FILTER lang`); path relatif + `requirements.txt` + README; `robot reason --output` agar inferensi termaterialisasi; `q4` dieksekusi; `atc_all.csv` dipakai untuk kelas terapi; `measure`/`LOG` dihasilkan skrip.

---

## 4. Data baru yang perlu dibuat (semuanya kecil, tanpa scrape ulang)

| File | Isi | Sumber | Usaha |
| :--- | :--- | :--- | :--- |
| `data/curation/substansi_aturan_pakai.csv` | 31 baris: dosis dewasa, dosis anak, frekuensi, waktu minum (pagi/malam/sesudah makan), maks hari swamedikasi, maks dosis harian, peringatan | PIONAS BPOM + label (pola yang sudah dipakai di `sheet4`) | M |
| `data/curation/substansi_kontraindikasi.csv` | 31 zat × kondisi (hipertensi, PJK, hipertiroid, DM, glaukoma, BPH, gagal jantung, tukak, hamil, menyusui, anak <2) | PIONAS + label | M |
| `data/curation/aturan_durasi.csv` | 22 gejala → batas hari sebelum rujuk (demam >3 hari, batuk >5 hari, dll) | PIONAS/label | S |
| `data/curation/sinonim_zat.csv` | normalisasi `ctm`, `gg`, `ppa`, `pe`, `dmp`, dll → 31 zat | `sheet1` + 109 produk tak terpetakan | S |
| `data/apotek/harga_per_unit.csv` | harga, isi kemasan, satuan (tablet/mL/sachet), harga per unit | turunan `produk_detail.csv` | M |
| `data/apotek/dikecualikan.csv` | produk dengan komposisi tidak valid/kosong (mis. BODREX FLU tanpa komposisi) agar tidak masuk rekomendasi | hasil validasi | S |

---

## 5. Detail task

### T1 — Rekomendasi terapi personal (task utama)

**Tujuan:** dari keluhan + kondisi pasien → produk yang tepat, cara pakai, dan peringatan.

**Input:** gejala (pilih dari 22 + sinonim), durasi gejala, umur, jenis kelamin, hamil/menyusui, penyakit penyerta, obat rutin.
**Output:** 1–3 produk + aturan pakai (frekuensi, waktu, maks hari) + peringatan (interaksi, kontraindikasi, efek samping) + aksi triase (Pantau / TanyaApoteker / SegeraKeDokter).

| Unsur | Individu/kelas yang dipakai | Sumber aturan |
| :--- | :--- | :--- |
| Kandidat produk | 377 produk batuk/pilek, `memilikiKandungan`, `mengindikasikanGejala` | `produk_batuk.csv`, `produk_pilek.csv` |
| Aturan pakai | 31 zat + data property baru `dosisDewasa`, `frekuensi`, `waktuMinum`, `maksHari`, `maksDosisHarian` | PIONAS/label |
| Kondisi pasien | `KondisiPasien` (+ subkelas baru), `kontraindikasiBagi` | PIONAS/label |
| Peringatan kombinasi | `InteraksiObat` + kelas keparahan, `DuplikasiTerapetik` | DDInter + 20 kurasi |
| Efek samping | `GejalaEfekSamping`, `_AH1Product`, `_DekongestanProduct` | R-03, R-04 |
| Triase | `GejalaIndikasi/RedFlag`, `TindakLanjut` | 22 gejala + `aturan_durasi.csv` |
| Klasifikasi produk | R-01, R-02 (setelah diperbaiki + `disjointWith`) | TBox |

**Sub-todo:**
1.1 Perbaiki R-01/R-02 + `disjointWith`; hapus assertion manual; materialisasi inferensi.
1.2 Buat `substansi_aturan_pakai.csv` (31 baris) + data property di OWL.
1.3 Buat `substansi_kontraindikasi.csv` (31 × kondisi) + aktifkan R-08 untuk kondisi lain.
1.4 Buat `aturan_durasi.csv` (22 baris) + aturan "> X hari → SegeraKeDokter".
1.5 Endpoint/skrip rekomendasi (`scrape/rekomendasi.py`) + `queries/q5_rekomendasi.rq`.
1.6 5 skenario uji: batuk kering dewasa; batuk berdahak anak 4 th; hipertensi + PSE; hamil; demam 5 hari.

**Kriteria selesai:** 5 skenario menghasilkan produk + cara pakai + minimal 1 peringatan, dan kondisi yang tidak tercakup jatuh ke "TanyaApoteker" (bukan menebak).

**Risiko:** kualitas tabel aturan pakai (manual). Batasi ke 31 zat, jangan klaim per produk.

---

### T2 — Alternatif lebih murah / kandungan minimal

**Tujuan:** dari 1 produk → produk lain dengan kandungan identik tapi lebih murah, atau produk mono-kandungan yang lebih murah.

**Input:** produk A. **Output:** (a) ekuivalen lebih murah, (b) mono-kandungan yang menutupi keluhan, (c) selisih harga + catatan kemasan.

| Unsur | Individu | Sumber |
| :--- | :--- | :--- |
| Kandungan | `memilikiKandungan` (31 zat) | komposisi hasil scrape |
| Harga | `hargaRupiah` | `produk_detail.csv` (828 terisi) |
| Kesetaraan | `BentukSediaan` + set kandungan identik | ATC + komposisi |
| Golongan | `GolonganObat` | BPOM |

**Sub-todo:** 2.1 `sinonim_zat.csv` + parser komposisi (bukan substring); 2.2 `harga_per_unit.csv` (parse "isi N tablet/mL"); 2.3 `dikecualikan.csv`; 2.4 query/endpoint `q6_alternatif_murah.rq`; 2.5 demo 10 kelompok (paracetamol tunggal, CTM, cetirizine, guaifenesin, bromhexine, dll).

**Kriteria selesai:** 10 kelompok menampilkan alternatif lebih murah dengan kandungan identik dan satuan harga yang sebanding; produk dengan komposisi tidak valid tidak muncul.

**Risiko (terbukti dari uji cepat):** pencocokan substring membuat BODREX FLU masuk grup "paracetamol tunggal" dan WICOLD muncul Rp180.375 — hasilnya ngawur kalau komposisi tidak dibersihkan. Wajib kerjakan 2.1–2.3 sebelum query.

---

### T3 — Skrining keranjang & obat rutin

**Tujuan:** pasien membawa 2–5 produk (beli + obat rutin) → daftar masalah: dobel zat, dobel kelas terapi, interaksi, kontraindikasi, aksi triase.

**Input:** daftar produk/zat. **Output:** laporan masalah + aksi per masalah.

| Unsur | Individu | Sumber |
| :--- | :--- | :--- |
| Keranjang | `KasusPasien`, `ObatPasien`, `menggunakanProdukObat`, `menggunakanZatAktif` | model yang sudah ada |
| Dobel zat | `memilikiKandungan` + kelas `DuplikasiKandungan` (baru) | generalisasi R-07 |
| Dobel kelas | ATC level-4 (17 kode) | `atc_all.csv` + `kodeATC` |
| Interaksi | `InteraksiObat` + 55 pasangan DDInter domain | `KB/ddinter_*.csv` |
| Kontraindikasi | `kontraindikasiBagi` | tabel T1.3 |
| Output tindakan | `TindakLanjut` | R-05, R-06 |

**Sub-todo:** 3.1 kelas `DuplikasiKandungan` + `DuplikasiKelasATC`; 3.2 import 55 pasangan DDInter (1 Major, 19 Moderate siap; 35 Unknown ditandai `Unknown`, jangan dikarang); 3.3 `q7_keranjang.rq`; 3.4 3 keranjang uji (2 merek paracetamol; Komix + Actifed; Actifed + digoxin).

**Kriteria selesai:** keranjang 2 merek ber-paracetamol → "dobel paracetamol, risiko overdosis"; keranjang dengan PSE + hipertensi → "kontraindikasi"; 0 interaksi yang tidak ada di sumber.

---

### T4 — Substitusi aman

**Tujuan:** produk yang dipilih mengandung zat bermasalah untuk kondisi pasien → cari produk lain yang menutupi gejala sama tanpa zat itu.

**Input:** produk + kondisi pasien. **Output:** alternatif + alasan penolakan produk awal.

| Unsur | Individu | Sumber |
| :--- | :--- | :--- |
| Zat bermasalah | `kontraindikasiBagi` (perlu domain `ZatAktif`, bukan hanya produk) | R-08 + tabel T1.3 |
| Gejala yang harus tetap ditutup | `mengindikasikanGejala`, `GejalaIndikasi` | komposisi + gejala |
| Kandidat pengganti | 377 produk, `memilikiKandungan` | katalog |
| Prioritas | aman > murah (T2) > mono-kandungan | kombinasi T2+T4 |

**Sub-todo:** 4.1 pindahkan/duplikasi `kontraindikasiBagi` ke level zat; 4.2 `q8_substitusi_aman.rq`; 4.3 3 skenario (hipertensi + produk PSE; BPH + CTM; tukak + ibuprofen).

**Kriteria selesai:** setiap skenario menghasilkan minimal 1 alternatif yang tidak melanggar kontraindikasi dan tetap menutupi keluhan.

**Risiko:** tanpa tabel kontraindikasi lengkap, T4 tidak bisa jalan — T4 bergantung pada T1.3.

---

### T5 — Kartu edukasi & explainability

**Tujuan:** setiap rekomendasi/peringatan bisa dijelaskan ke pasien dalam bahasa awam, dengan sumber yang bisa diaudit.

**Input:** hasil T1/T3/T4. **Output:** kartu per produk: nama, isi, untuk apa, cara pakai, kapan berhenti/rujuk, "kenapa" (rantai produk→zat→interaksi→sumber + batas bukti).

| Unsur | Individu | Sumber |
| :--- | :--- | :--- |
| Rantai bukti | `SumberBukti`, `didukungOleh`, `tingkatBukti` | `evidence_interaksi.csv` |
| Bahasa awam | `skos:altLabel` di 22 gejala | `symptoms_selected.csv` |
| Aksi | `TindakLanjut` + `membutuhkanTindakLanjut` | R-05, R-06 |
| Aturan pakai | data property dari T1.2 | PIONAS/label |

**Sub-todo:** 5.1 template kartu (markdown); 5.2 query pengambil rantai penjelasan; 5.3 5 kartu contoh (Actifed, Komix, Sanmol, OB Combi, Siladex); 5.4 penanda "kesimpulan dari aturan" vs "data kurasi" agar tidak menyesatkan.

**Kriteria selesai:** 5 kartu memuat cara pakai + minimal 1 peringatan + sumber, dan setiap klaim punya rujukan atau label "belum ada sumber".

---

## 6. Urutan kerja & dependensi

1. **Fase 0 (wajib, 1–2 hari):** path relatif + `requirements.txt` + README; perbaiki `q1`; hitung ulang `measure`; arsipkan legacy; perbaiki R-01/R-02 + `disjointWith`; materialisasi inferensi.
2. **Fase 1 (T2, 1–2 hari):** paling siap — harga & komposisi sudah ada. Butuh `sinonim_zat` + parser + `harga_per_unit` + `dikecualikan`. Hasilnya bisa didemokan tanpa aturan klinis baru.
3. **Fase 2 (T3, 2 hari):** model keranjang + ATC-4 + import DDInter. Tidak butuh kurasi manual.
4. **Fase 3 (T1, 3–5 hari):** dua tabel kurasi (aturan pakai + kontraindikasi) + aturan durasi + endpoint. Ini task terberat.
5. **Fase 4 (T4, 1–2 hari):** setelah T1.3 selesai, mayoritas kerja tinggal query.
6. **Fase 5 (T5, 1 hari):** template + 5 kartu; hanya merangkai yang sudah ada.

**Dependensi:** T4 ← T1.3. T3 ← T1.3 (untuk bagian kontraindikasi; duplikasi & interaksi bisa jalan lebih dulu). T1 ← Fase 0. T2 dan T5 tidak bergantung pada task lain.

---

## 7. Non-goals

- Dosis berbasis berat badan / mg per kg (data tidak ada di katalog).
- Skor keparahan berjenjang selain red flag.
- Interaksi di luar 31 zat (butuh mapping 3.484 obat DDInter).
- Standarisasi kadar herbal (47 produk jamu, kadar tidak dicantumkan).
- Penyesuaian renal/hepatik, farmakogenomik, kategori kehamilan FDA.
- Menambah obat keras ke katalog (disembunyikan K24Klik sesuai regulasi).
- Ekstraksi 210 ribu halaman detail DDInter (hanya kolom `Level` yang tersedia bulk).

**Batas etis:** sistem ini alat bantu keputusan, bukan resep. Red flag selalu berakhir `SegeraKeDokter`; kasus di luar cakupan selalu `TanyaApoteker`.

---

## 8. Verifikasi

- Tiap fase: `robot reason --reasoner HermiT --input ... validate-profile --profile DL` LULUS.
- Semua angka di laporan dihasilkan `robot measure`/skrip, bukan diketik.
- Setiap rekomendasi menyertakan sumber atau penanda "belum ada sumber".
- Uji regresi: 5 skenario T1 + 3 keranjang T3 + 3 substitusi T4 + 10 kelompok T2, dijalankan ulang tiap build.
