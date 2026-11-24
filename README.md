# ProjectKBR-Group4 — Sistem Pendukung Keputusan Swamedikasi & Interaksi Obat Batuk-Pilek (KB v2.0)

Repositori proyek **Knowledge-Based Reasoning (KBR) — Kelompok 4 (UNS)** untuk membangun basis pengetahuan ontologi OWL 2 DL, katalog produk apotek Indonesia, aturan penalaran HermiT, kueri SPARQL, serta mesin pendukung keputusan klinis untuk **5 Task Final (T1–T5)** swamedikasi batuk & pilek.

> **Disclaimer Klinis:** Sistem ini adalah alat bantu edukasi dan pendukung keputusan berbasis pengetahuan (*Knowledge-Based Reasoning*), **bukan** resep medis maupun pengganti evaluasi apoteker/dokter. Pasangan interaksi yang tidak tercatat selalu berstatus `tidak_diketahui` (*TanyaApoteker*), **tidak pernah** diklaim aman secara otomatis.

---

## Ringkasan 5 Task Final (T1–T5)

| Task | Deskripsi | Implementasi Utama |
| :--- | :--- | :--- |
| **T1 — Rekomendasi Terapi Personal** | Input gejala, durasi, umur, berat badan, kondisi khusus, obat rutin, dan alergi $\rightarrow$ 1–3 produk aman + aturan pakai + peringatan + triase (`Pantau` / `TanyaApoteker` / `SegeraKeDokter`). | `scrape/kbr_engine.py` (`recommend_t1`), `queries/q5_rekomendasi.rq` |
| **T2 — Alternatif Lebih Murah** | Membandingkan produk dengan kandungan zat aktif identik & satuan sebanding (`mL`/`tablet`/`sachet`) dari `data/apotek/harga_per_unit.csv`, mengecualikan produk rusak/kosong (`dikecualikan.csv`). | `scrape/kbr_engine.py` (`cheaper_alternatives_t2`), `queries/q6_alternatif_murah.rq` |
| **T3 — Skrining Keranjang & Obat Rutin** | Mendeteksi `DuplikasiKandungan`, `DuplikasiKelasATC` (ATC Level-4), interaksi obat kurasi + DDInter (termasuk `InteraksiUnknown`), konflik jadwal makan, dan kontraindikasi kondisi. | `scrape/kbr_engine.py` (`screen_cart_t3`), `queries/q7_keranjang.rq`, `queries/q4_skenario_pasien_actifed_digoxin.rq` |
| **T4 — Substitusi Aman** | Mengganti produk yang mengandung zat kontraindikasi (mis. PSE pada hipertensi, CTM pada BPH, Ibuprofen pada tukak lambung) dengan alternatif aman yang tetap mencakup keluhan pasien. | `scrape/kbr_engine.py` (`safe_substitution_t4`), `queries/q8_substitusi_aman.rq` |
| **T5 — Kartu Edukasi & Explainability** | Menghasilkan kartu edukasi Markdown lengkap dengan bahasa awam, cara pakai, pantangan, alergi silang (OpenFDA/DailyMed), rantai bukti interaksi (`SumberBukti`), serta pemisahan antara inferensi aturan vs data kurasi. | `scrape/kbr_engine.py` (`generate_education_card_t5`), `out/kartu_edukasi/`, `queries/q9_kartu_edukasi.rq` |

---

## Struktur Direktori Utama

```text
ProjectKBR-Group4/
├── data/
│   ├── apotek/          # Katalog K24Klik (produk_detail, produk_batuk, produk_pilek, harga_per_unit, dikecualikan)
│   ├── atc/             # Klasifikasi WHO ATC Level 1-5 (atc_all.csv)
│   ├── curation/        # Kurasi 31 zat aktif, sinonim, aturan pakai (umur & BB), kontraindikasi, alergi OpenFDA, durasi, bukti, measure TSV
│   ├── dinto/           # Modul mekanisme DDI DINTO
│   ├── enzymes/         # 4 enzim CYP450 manusia (PRO / OLS4)
│   ├── interactions/    # 20 interaksi terkurasi + 158 pasangan DDInter + tabel evidence
│   ├── mappings/        # Pemetaan ATC <-> ChEBI
│   └── symptoms/        # 22 gejala terpilih (Symptom Ontology)
├── docs/                # Rencana kerja (RENCANA_KERJA.md), catatan metode, spesifikasi
├── logs/                # LOG.md, run_commands.txt, penjelasan_ontologi_lengkap.txt
├── out/
│   ├── kb_v2.owl                # Basis pengetahuan v2 non-hardcode (345 produk + 1 herbal, 31 zat, 22 gejala, 65 interaksi, 21 bukti)
│   ├── kb_v2_reasoned.owl       # Hasil materialisasi reasoner HermiT (OWL 2 DL)
│   ├── kb_v2_lengkap.owl        # Gabungan kb_v2_reasoned + modul referensi (ChEBI, DrON, PRO, DINTO, SYMP)
│   ├── kartu_edukasi/           # 5 kartu edukasi Markdown hasil T5
│   └── q1_result.csv .. q9_result.csv
├── queries/             # Query SPARQL q1..q9
├── scrape/              # Skrip akuisisi data, perakitan KB (build_kb_v2.py), dan engine (kbr_engine.py)
├── tests/               # Uji regresi formal T1-T5 (test_kbr_regression.py)
├── archive_legacy/      # Arsip skrip & CSV dummy lama (tidak dipakai oleh pipeline v2)
└── requirements.txt
```

---

## Metrik Ontologi Terverifikasi (`robot measure` & HermiT OWL 2 DL)

| Berkas Ontologi | Kelas | Object Prop | Data Prop | Individu | Logical Axioms | Total Axioms | DL / SWRL |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| `out/kb_v2_reasoned.owl` (`measure_kb_v2.tsv`) | 115 | 21 | 47 | 546 | 8,741 | 10,169 | **SROIQ(D) + 11 SWRL (OWL 2 DL)** |
| `out/kb_v2_lengkap.owl` (`measure_kb_v2_lengkap.tsv`) | 953 | 55 | 47 | 546 | 10,760 | 21,228 | **SROIQ(D) + 11 SWRL (OWL 2 DL)** |

**Hasil Inferensi Murni Reasoner HermiT (0 asserted $\rightarrow$ dimaterialisasi oleh HermiT dengan `owl:AllDisjointClasses` & *closure axiom*):**
- `ObatBatukMurni` (R-01): **118** produk
- `ObatPilekMurni` (R-02): **158** produk
- `ObatKombinasiBatukPilek`: **96** produk
- `_AH1Product` (R-03, pemicu peringatan kantuk): **190** produk
- `_DekongestanProduct` (R-04, Phenylephrine): **18** produk
- `ProdukDenganPSE` (R-04 & R-08, kontraindikasi hipertensi): **83** produk

---

## Cara Menjalankan Pipeline & Uji Regresi

### 1. Prasyarat
- Python 3.10+ (pipeline `build_kb_v2.py`, `kbr_engine.py`, dan `test_kbr_regression.py` hanya memakai *Python standard library*; untuk skrip utilitas opsional lihat `requirements.txt`).
- Java (JRE/JDK 11+) dan `robot.jar` (ROBOT 1.9+) untuk validasi HermiT, profil OWL 2 DL, `measure`, dan `query`.

### 2. Bangun Ulang `kb_v2.owl`, Validasi HermiT, & Jalankan SPARQL
Jalankan dari direktori root repositori (`ProjectKBR-Group4/`):

```powershell
# 1. Rakit out/kb_v2.owl secara dinamis dari CSV terkurasi
python scrape/build_kb_v2.py

# 2. Materialisasi inferensi HermiT & validasi profil OWL 2 DL
java -jar path\to\robot.jar reason --reasoner HermiT --input out/kb_v2.owl --axiom-generators "SubClass EquivalentClass DisjointClasses ClassAssertion" --annotate-inferred-axioms true --output out/kb_v2_reasoned.owl validate-profile --profile DL

# 3. Ukur metrik ontologi
java -jar path\to\robot.jar measure --input out/kb_v2_reasoned.owl --format tsv --output data/curation/measure_kb_v2.tsv

# 4. Gabungkan dengan modul referensi (ChEBI, DrON, PRO, DINTO, SYMP)
java -jar path\to\robot.jar merge --input out/kb_v2_reasoned.owl --input out/kb_referensi_lengkap.owl annotate --ontology-iri "http://purl.obolibrary.org/obo/kbr-group4/kb_v2_lengkap.owl" --version-iri "http://purl.obolibrary.org/obo/kbr-group4/kb_v2_lengkap.owl/2.0" --output out/kb_v2_lengkap.owl validate-profile --profile DL

# 5. Jalankan kueri SPARQL T1-T5 (q1, q4-q9)
java -jar path\to\robot.jar query --input out/kb_v2_reasoned.owl --query queries/q5_rekomendasi.rq out/q5_result.csv --query queries/q6_alternatif_murah.rq out/q6_result.csv --query queries/q7_keranjang.rq out/q7_result.csv --query queries/q8_substitusi_aman.rq out/q8_result.csv --query queries/q9_kartu_edukasi.rq out/q9_result.csv
```

### 3. Hasilkan 5 Kartu Edukasi (T5) & Jalankan Uji Regresi (T1–T5)
```powershell
python scrape/kbr_engine.py
python tests/test_kbr_regression.py
```

Seluruh 5 rangkaian uji regresi (5 skenario T1, 10 kelompok harga T2, 3 keranjang T3 + uji negatif `Unknown != aman`, 3 substitusi T4, 5 kartu edukasi T5) terverifikasi **LULUS 100%**.
