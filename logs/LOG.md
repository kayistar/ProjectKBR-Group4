# ROBOT & Ontology Module Extraction Full Log
Tanggal-Waktu: 2026-11-08 14:35:00 WIB
OS: Windows (PowerShell)
Folder Kerja: D:\UNS\SMT_5\KBR\PROJECT

## 1. Alat & Lingkungan
- Java Version: OpenJDK 21.0.12.1 LTS (Eclipse Temurin)
- ROBOT Version: 1.9.11
- Heap Memory JVM: `-Xmx8G`

## 2. Checksum dan Ukuran File Sumber & Seed
| File | Ukuran (Bytes) | SHA-256 Checksum |
| :--- | :--- | :--- |
| `KB/chebi.owl` | 866,211,680 | `1D3392298F71ED8F099C69107416D41B7B85FB61228EB1649B86210A55AE4EA9` |
| `KB/dron.owl` | 526,190,848 | `CED2308A12363EB4A4A6771534A69FB6EDE4E93691C24F14BF94D3858125B79B` |
| `chebi_terms.txt` | 184 | `2B8079BC9725A9C481FC3E5C7DD7C8B84EA6CF6E22A92183AE5087B1DA6465B9` |
| `dron_terms.txt` | 117 | `05C7EBD126A42469B58E7668806ACEB6F548E696F1DA92372AE04F7D33511194` |

## 3. Ekstraksi Modul & Pembersihan
- Langkah 2: Uji term `CHEBI:2668` -> LULUS (file `out/test_term.owl`, 737 KB).
- Langkah 3: Ekstraksi ChEBI BOT (16 terms) -> LULUS tanpa `--force` (file `out/chebi_modul.owl`, 3,054,135 bytes).
- Langkah 4: Ekstraksi DrON BOT (8 terms) -> LULUS (file `out/dron_modul.owl`, 54,816 bytes). *Catatan*: File sumber `dron.owl` terpotong pada line 11120110 saat diunduh sebelumnya; disalin dan ditutup tag penutup valid di `out/dron_fixed.owl` sebelum diekstrak, tanpa mengubah file asli di `KB/`.
- Langkah 5: Pembersihan sinonim brand ChEBI -> LULUS (file `out/chebi_modul_clean.owl`, 1,411,818 bytes; 0 properti sinonim tersisa).
- Langkah 7: Penggabungan Modul (Merge) -> LULUS (file `out/referensi_modul.owl`, 1,459,109 bytes; 696 classes total).

## 4. Hasil Validasi (Langkah 6)
- 6a (Kelengkapan Seed): LULUS (16/16 ChEBI ADA, 8/8 DrON ADA).
- 6b (Tanpa Brand/Produk): LULUS (0 sinonim di ChEBI clean; 0 individual di DrON modul; 0 label produk/dosis di DrON modul).
- 6c (Ukuran Modul): LULUS (ChEBI Clean: 677 classes; DrON Modul: 19 classes; Target: < 1000).
- 6d (Spot-Check): LULUS (semua term terverifikasi pada ontologi lokal & link web resmi).
- 6e (Konsistensi Reasoner HermiT): LULUS (ChEBI Clean: 2.94s lolos; DrON Modul: 1.89s lolos; Merged Modul: 3.20s lolos).
- 6f (Pemetaan DrON ke ChEBI): LULUS (0 mismatch).


## 5. Pembaruan Ekstraksi Modul ChEBI (2026-11-15)
- Penambahan 5 seed 3-star terverifikasi dari `KB/chebi.owl` ke `chebi_terms.txt` & `out/seed_chebi_work.txt`:
  - `CHEBI:6076` (*itraconazole*)
  - `CHEBI:47519` (*ketoconazole*)
  - `CHEBI:46081` (*fluconazole*)
  - `CHEBI:37941` (*clopidogrel*)
  - `CHEBI:39548` (*atorvastatin*)
- Ukuran & SHA-256 terbaru:
  - `chebi_terms.txt` (21 IDs): `C589D73F9EE13549EA4BA7E6B13D7C0064477B545081B96ED3D9D6AAB37BECED`
  - `out/chebi_modul.owl`: 3,349,107 bytes
  - `out/chebi_modul_clean.owl`: 1,577,544 bytes (746 classes, 0 sinonim tersisa) | SHA-256: `500083D5C9CA782AABEB5A6851189C7B0AF55E9C9FD18C3A3432BDF106AA8150`
  - `out/referensi_modul.owl`: 1,624,835 bytes (765 classes total) | SHA-256: `8249E9FB8DD95EFAD41161C2B1FC68B622708B3305DDC77D4C95F5334AE0435A`
- Validasi pasca-ekstraksi ulang:
  - Kelengkapan seed: LULUS (21/21 ChEBI ADA, 8/8 DrON ADA, 0 missing).
  - Pembersihan sinonim: LULUS (0 properti sinonim di `out/chebi_modul_clean.owl`).
  - Konsistensi Reasoner HermiT (`robot reason --reasoner HermiT`): LULUS.
  - Validasi Profil OWL 2 DL (`robot validate-profile --profile DL`): LULUS (`Ontology and imports closure in profile`).


## 6. Pengambilan Enzim CYP450 Manusia via API PRO / OLS4 (2026-11-15)
- Skrip otomatisasi: `scrape/collect_enzymes.py` (stdlib Python `urllib`, tanpa download manual `pr.owl` multi-GB).
- Sumber API: EMBL-EBI OLS4 REST API (`https://www.ebi.ac.uk/ols4/api/ontologies/pr/terms`) & Ontobee RDF (`https://ontobee.org/ontology/rdf/PR`).
- 4 enzim manusia terverifikasi yang diambil:
  - `PR:P08684` — *cytochrome P450 3A4 (human)* (CYP3A4)
  - `PR:P10635` — *cytochrome P450 2D6 (human)* (CYP2D6)
  - `PR:P33261` — *cytochrome P450 2C19 (human)* (CYP2C19)
  - `PR:P11712` — *cytochrome P450 2C9 (human)* (CYP2C9)
- Output yang dihasilkan:
  - `out/enzim_modul.owl` (6,403 bytes; 9 `owl:Class`: 4 enzim target + 5 parent PRO `PR:000006118`, `PR:000006120`, `PR:000006121`, `PR:000006130`, `PR:000029067`) | SHA-256: `DC55EF4F3F00CF65F6FF60F642EBC26C8B79837472FA906CBD8C9B4E6FFF42AC`
  - `data/enzymes/enzymes_selected.csv` (1,088 bytes) | SHA-256: `51A6BE8B0E3EA34200712031A5624478C8C15FEF283DD15CA0A3354A8057EF08`
  - `data/enzymes/enzymes_ols4.json` | SHA-256: `DA0225D338F09FC7E168B7755254E094CB212B1D97244BB72ED0332A9D552F8E`
  - `data/enzymes/source_metadata.json` & `data/enzymes/ontobee/*.owl`
- Validasi ROBOT:
  - `robot reason --reasoner HermiT --input "out/enzim_modul.owl" validate-profile --profile DL`: LULUS (`Ontology and imports closure in profile`).
  - Uji komposisi `robot merge --input "out/referensi_modul.owl" --input "out/enzim_modul.owl" reason --reasoner HermiT validate-profile --profile DL`: LULUS (`Ontology and imports closure in profile`).


## 7. Pengambilan & Ekstraksi Modul Mekanisme DINTO via Otomatisasi (2026-11-15)
- Skrip otomatisasi: `scrape/collect_dinto.py`
- Sumber repositori: GitHub `labda/DINTO` (`https://raw.githubusercontent.com/labda/DINTO/master/DINTO1.2/DINTO_1.2.owl.zip`, arsip 5,798,610 bytes, uncompressed 113,519,214 bytes).
- Penanganan import eksternal: Pembersihan tag `<Import>http://purl.obolibrary.org/obo/MF/external/ontology-metadata-slim.owl</Import>` menghasilkan `DINTO_1.2_noimport.owl` agar ROBOT dapat memproses secara mandiri dan offline tanpa `UnloadableImportException`.
- Ekstraksi modul via ROBOT MIREOT:
  - Seed terms: 85 entitas formal DINTO (`data/dinto/seed_dinto_terms.txt`), mencakup:
    - Kelas interaksi & mekanisme DDI: `DINTO:000001` (*DDI*), `DINTO:000003` (*DDI mechanism*), `DINTO:000004` (*pharmacokinetic DDI mechanism*), `DINTO:000005` (*pharmacodynamic DDI mechanism*), `DINTO:0001` (*enzyme related DDI*), `DINTO:000169` (*enzyme induction DDI*), `DINTO:000170` (*enzyme inhibition DDI*), `DINTO:4326` (*agonistic DDI*), `DINTO:4330` (*antagonistic DDI*), `DINTO:000124` (*enzyme activity alteration*), dsb.
    - Kelas peran interaksi: `DINTO:000023` (*participant*), `DINTO:000024` (*precipitant*), `DINTO:000025` (*object*).
    - Properti relasi DDI & inverse: `DINTO:000136` (*has participant*), `DINTO:000137` (*has precipitant*), `DINTO:000138` (*has object*), `DINTO:000142` (*precedes*), `DINTO:000143` (*is preceded by*), `DINTO:000146` (*alters*), `DINTO:000147` (*is altered by*), `DINTO:000165` (*has DDI effect*), `DINTO:000166` (*is DDI effect of*).
- Output yang dihasilkan:
  - `out/dinto_modul.owl` (60,413 bytes; 72 `owl:Class`, 18 `owl:ObjectProperty`) | SHA-256: `0B252B36239683406947BF49248857925336CE0764DF626418B64FBDF3F88919`
  - `data/dinto/dinto_mechanisms_selected.csv` (7,283 bytes) | SHA-256: `30AFF7E8AE220BA6E20076E207A3FF1FA5E110C22CBFDAFE9708F13F72E12EB9`
  - `data/dinto/seed_dinto_terms.txt` | SHA-256: `9E50962A23919F4A84C6821FA0EA9C78FF43B9E84861DD8DB2607356B3D2E12F`
  - `data/dinto/source_metadata.json`
- Validasi ROBOT:
  - `robot reason --reasoner HermiT --input "out/dinto_modul.owl" validate-profile --profile DL`: LULUS (`OWL 2 DL Profile Report: [Ontology and imports closure in profile]`).
  - Uji komposisi 3 modul (`robot merge --input "out/referensi_modul.owl" --input "out/enzim_modul.owl" --input "out/dinto_modul.owl" reason --reasoner HermiT validate-profile --profile DL`): LULUS (`[Ontology and imports closure in profile]`).


## 8. Ekstraksi & Anotasi Modul Gejala dari Symptom Ontology (Modul 4) (2026-11-15)
- Skrip otomatisasi: `scrape/collect_symptoms.py`
- Sumber data: `KB/symp.owl` (832,936 bytes; Symptom Ontology releases/2026-07-30).
- Metode: ROBOT MIREOT dengan upper term `http://purl.obolibrary.org/obo/SYMP_0000462` (*symptom*).
- 22 Gejala Terkurasi untuk Domain Batuk-Pilek & Triase Apoteker (`data/symptoms/seed_symptom_terms.txt`):
  - **9 Gejala Indikasi (Tindak lanjut: `Pantau`):**
    - `SYMP:0000614` (*cough* / Batuk)
    - `SYMP:0000025` (*dry cough* / Batuk kering)
    - `SYMP:0020027` (*wet cough* / Batuk berdahak)
    - `SYMP:0000869` (*nasal congestion* / Hidung tersumbat)
    - `SYMP:0000372` (*rhinorrhea* / Pilek)
    - `SYMP:0000139` (*sneezing* / Bersin-bersin)
    - `SYMP:0000505` (*throat pain* / Sakit tenggorokan)
    - `SYMP:0000613` (*fever* / Demam)
    - `SYMP:0000504` (*headache* / Sakit kepala)
  - **8 Gejala Efek Samping (Tindak lanjut: `TanyaApoteker` / `Pantau`):**
    - `SYMP:0000024` (*drowsiness* / Mengantuk — antihistamin CTM/DPH)
    - `SYMP:0000610` (*dizziness* / Pusing)
    - `SYMP:0000260` (*dry mouth* / Mulut kering)
    - `SYMP:0000557` (*urinary retention* / Retensi urin)
    - `SYMP:0000530` (*palpitation* / Jantung berdebar — dekongestan PSE)
    - `SYMP:0000529` (*tachycardia* / Nadi cepat)
    - `SYMP:0000458` (*nausea* / Mual)
    - `SYMP:0019145` (*vomiting* / Muntah)
  - **5 Gejala Tanda Bahaya / Red Flags (Tindak lanjut: `SegeraKeDokter`):**
    - `SYMP:0019153` (*dyspnea* / Sesak napas)
    - `SYMP:0000604` (*wheezing* / Mengi)
    - `SYMP:0000576` (*chest pain* / Nyeri dada)
    - `SYMP:0000242` (*cough with bloody sputum* / Batuk berdarah)
    - `SYMP:0020043` (*dark urine* / Urin gelap teh — rhabdomyolysis / hepatotoksisitas)
- Anotasi semantik yang ditambahkan:
  - `skos:altLabel` (label bahasa Indonesia awam)
  - `rdfs:comment` (format terstruktur `[Kategori] Rekomendasi: TindakLanjut. Deskripsi`)
  - Ontology IRI: `http://purl.obolibrary.org/obo/kbr-group4/symptom_modul.owl`
- Output:
  - `out/symptom_modul.owl` (51,416 bytes) | SHA-256: `A30AE5E87AF3099641519B215585D91E549C21043E02558C3636022866346691`
  - `data/symptoms/symptoms_selected.csv` (4,698 bytes) | SHA-256: `5645DBE27B8725DB50B92176C539F24A106389593B079D47FAE99434F611405A`
  - `data/symptoms/seed_symptom_terms.txt` | SHA-256: `2CE67F1A1B26A03A771E500A082F3BBB710C627BC749B4B864DC6ADA0C3FBDAF`
  - `data/symptoms/source_metadata.json`
- Validasi ROBOT:
  - `robot reason --reasoner HermiT --input "out/symptom_modul.owl" validate-profile --profile DL`: LULUS (`OWL 2 DL Profile Report: [Ontology and imports closure in profile]`).
  - Uji komposisi 4 modul (`robot merge --input "out/referensi_modul.owl" --input "out/enzim_modul.owl" --input "out/dinto_modul.owl" --input "out/symptom_modul.owl" reason --reasoner HermiT validate-profile --profile DL`): LULUS (`[Ontology and imports closure in profile]`).


## 9. Kurasi Data Interaksi Obat & Herbal (Modul 5) (2026-11-15)
- Skrip otomatisasi: `scrape/build_modul5_interactions.py`
- Sumber data:
  - DDInter 2.0 (`KB/ddinter_downloads_code_A.csv`, `code_B.csv`, `code_D.csv`, `code_R.csv`)
  - PIONAS BPOM RI & DrugBank Interaction Data
  - Literatur Farmakologi Herbal (Phytomedicine, Drug Metabolism & Disposition untuk ekstrak Kulit Manggis, Kunyit, Jahe)
- Cakupan: 20 pasangan interaksi klinis terkurasi lengkap dengan mapping ChEBI, kode mekanisme DINTO, efek klinis, tindak lanjut triase, dan rekomendasi apoteker:
  - **Major (7 pasang):** *Simvastatin + Itraconazole* (CYP3A4), *Atorvastatin + Ketoconazole* (CYP3A4), *Alpha-Mangostin + Simvastatin* (Herbal-CYP3A4), *Clopidogrel + Omeprazole* (CYP2C19 prodrug bioactivation failure), *Ibuprofen + Warfarin* (Bleeding risk), *Ciprofloxacin + Glimepiride* (Hypoglycemia), *Simvastatin + Amlodipine* (CYP3A4 myopathy/dose cap).
  - **Moderate (10 pasang):** *Alpha-Mangostin + Amlodipine*, *Gingerol + Warfarin*, *Curcumin + Warfarin*, *Pseudoephedrine + Digoxin* (Arrhythmia), *Phenylephrine + Digoxin*, *Chlorpheniramine + Diphenhydramine* (Duplikasi antihistamin sedatif), *Cetirizine + Chlorpheniramine*, *Dextromethorphan + Chlorpheniramine* (Sedasi SSP), *Captopril + Ibuprofen* (Renal/antihypertensive failure), *Amlodipine + Ibuprofen*, *Paracetamol + Warfarin* (High dose INR).
  - **Minor (3 pasang):** *Ciprofloxacin + Omeprazole*, *Glimepiride + Metformin* (Controlled synergy), *Ibuprofen + Cetirizine*.
- Output:
  - `data/interactions/curated_drug_interactions.csv` (9,130 bytes) | SHA-256: `162456FD0E3E67117536A8A483B4736A05F07C52FDFAD4FCCF9C5851B373A1DC`
  - `data/interactions/source_metadata.json` | SHA-256: `3CF637D1407F50A6A7733F9BCA24A69E8525EEA2803A8B1E04E3DF98BBB5EC61`


## 10. Pemetaan ATC ↔ ChEBI & Master Workbook Kurasi 4 Sheet (Modul 6) (2026-11-15)
- Skrip otomatisasi: `scrape/build_modul6_curation.py`
- Komponen Master Kurasi:
  1. **Sheet 1 (`ZatAktif` / Pemetaan ATC ↔ ChEBI):** 29 zat aktif terverifikasi (11 zat inti batuk-pilek, 15 obat kronis pembanding, 3 senyawa herbal) menghubungkan Kode ATC Level 4/5, nama kelas ATC, identifier ChEBI, peran farmakologis, enzim metabolisme terkait, dan contoh produk paten/generik di apotek Indonesia.
  2. **Sheet 2 (`Interaksi`):** 20 pasangan interaksi klinis terkurasi dengan klasifikasi DINTO, tingkat keparahan (Major, Moderate, Minor), efek klinis, tindak lanjut triase, dan rekomendasi apoteker.
  3. **Sheet 3 (`Gejala`):** 22 gejala terkurasi dari Symptom Ontology (`SYMP_xxxxx`) lengkap dengan istilah bahasa Indonesia awam, kategori gejala (Indikasi, Efek Samping, Red Flag), dan rekomendasi tindak lanjut triase apoteker.
  4. **Sheet 4 (`Sumber`):** 10 referensi otoritatif dan regulator (DDInter 2.0, PIONAS BPOM, ChEBI, DrON, PRO, DINTO, SYMP, RxClass ATC, Jurnal Farmakologi, FDA Communications) beserta URL/PURL dan tingkat bukti ilmiah.
- Output yang dihasilkan:
  - `data/mappings/atc_chebi_mapping.csv` (6,118 bytes) | SHA-256: `8F3C2D9A53A2399DD40A70204BA9ABD34EA70F81AB38E7E6FCA67A9F99519065`
  - `data/curation/Knowledge_Base_Curation_Master.xlsx` (15,783 bytes) | SHA-256: `9DFD7B59D224F3A2E3EFC4EEDE413AB41F52D0FB1C4EF7D1D3434048F4401A46`
  - `data/curation/sheet1_zat_aktif.csv` (7,363 bytes)
  - `data/curation/sheet2_interaksi.csv` (9,130 bytes)
  - `data/curation/sheet3_gejala.csv` (4,698 bytes)
  - `data/curation/sheet4_sumber.csv` (2,735 bytes)
  - `data/curation/source_metadata.json`


## 11. Penggabungan Seluruh Modul ke Satu File Utuh (2026-11-15)
- Perintah: ROBOT `merge` menggabungkan 4 modul referensi:
  - `out/referensi_modul.owl` (ChEBI + DrON)
  - `out/enzim_modul.owl` (PRO human CYP450)
  - `out/dinto_modul.owl` (DINTO DDI mechanisms)
  - `out/symptom_modul.owl` (SYMP symptoms)
- Output gabungan:
  - `out/kb_referensi_lengkap.owl` (1,738,615 bytes) | SHA-256: `9239365759D9C19AD4DF82EF8F4EB8FDA1EE5C0811C9D80D10DB3E5C8866BFD5`
- Metrik ontologi gabungan (`data/curation/measure_kb_lengkap.tsv`):
  - Total Classes: **885 kelas**
  - Total Object Properties: **34 properti**
  - Logical Axioms: **2,019 aksioma logis**
  - Total Axioms: **11,129 aksioma**
- Validasi ROBOT:
  - `robot reason --reasoner HermiT --input "out/kb_referensi_lengkap.owl" validate-profile --profile DL`: LULUS (`OWL 2 DL Profile Report: [Ontology and imports closure in profile]`).


## 12. Scraping Menyeluruh Katalog Apotek Indonesia (K24Klik) (2026-11-16)
- Skrip: `scrape/scrape_apotek_full.py` (tahap `--stage listing` lalu `--stage detail`; resumable via `data/apotek/cache/`).
- Sumber: K24Klik (`www.k24klik.com/cariObat/<kata kunci>?page=N`, halaman detail `/p/<slug>`).
- Temuan batas sumber:
  - Hasil pencarian dibatasi ±2 halaman (≈66 produk) per kata kunci; halaman 3 mengembalikan HTTP 404. Cakupan diperluas dengan banyak variasi kata kunci (zat aktif, merk, bentuk sediaan, gejala, herbal).
  - Obat keras/resep (mis. amlodipine, metformin, simvastatin, warfarin, amoxicillin, ambroxol) disembunyikan oleh K24Klik sesuai Permenkes -> 0 produk. Tidak ada upaya melewati pembatasan ini.
- Hasil: `data/apotek/listing.csv` (1.716 baris, 933 produk unik) dan `data/apotek/produk_detail.csv` (933 produk, status ok 933/933).
- Kelengkapan kolom (dari `produk_detail.csv`): komposisi 853/933, golongan 772/933, pabrik 683/933, NIE BPOM 670/933 (586 NIE unik), kemasan 933/933, harga 828/933.
- Golongan: obat bebas terbatas 413, obat bebas 177, obat jamu 113, obat herbal 66, fitofarmaka 3, kosong 161.


## 13. Pemisahan Produk Batuk & Pilek Apotek Indonesia (2026-11-16)
- Skrip: `scrape/split_batuk_pilek.py`
- Sumber data: `data/apotek/produk_detail.csv` (933 produk katalog apotek).
- Aturan Filter & Klasifikasi:
  - **Batuk**: Indikasi eksplisit batuk pada nama/keyword/komposisi (batuk, cough, tussin, siladex, komix, obh, vicks, dsb.) atau memiliki zat aktif antitusif/ekspektoran (dextromethorphan, guaifenesin, bromhexine, ambroxol, glyceryl guaiacolate).
  - **Pilek / Flu**: Indikasi eksplisit pilek/flu/demam (flu, cold, rhinitis, bersin, hidung tersumbat, decongestant, dsb.) atau memiliki zat aktif dekongestan/antihistamin/analgesik-antipiretik flu (pseudoephedrine, phenylephrine, phenylpropanolamine, chlorpheniramine/CTM, triprolidine, doxylamine, cetirizine, paracetamol flu).
  - **Kombinasi / Irisan**: Produk multi-komponen flu & batuk (misalnya Paracetamol + Pseudoephedrine + Dextromethorphan + CTM) dimasukkan ke dalam kedua file dengan label `tipe_kategori` yang informatif.
- Hasil Eksekusi:
  - Total produk masukan: 933 produk
  - `data/apotek/produk_batuk.csv`: **323 produk** (106,291 bytes) | SHA-256: `586f64a6ddc33293b3583fb084490c4a90a8b512618ad896d4359924a6539913`
  - `data/apotek/produk_pilek.csv`: **292 produk** (95,354 bytes) | SHA-256: `8fd0f23bf6890cc8d77aec140ac03da13286391feafaf2ec08d763af358785cc`
  - Irisan Kombinasi Batuk + Pilek: **148 produk**
  - Metadata: `data/apotek/metadata_split_batuk_pilek.json` (308 bytes) | SHA-256: `59995854309e802c5dfcb54c77ff9dca8f21b9eff2eede008a5f17da62a43b9c`


## 14. Penyusunan Basis Pengetahuan kb_v1.owl & Validasi HermiT (2026-11-16)
- Skrip perakit: `scrape/build_kb_v1.py`
- Komponen Arsitektur:
  1. **TBox (Hierarki Kelas & Properti):**
     - Kelas: `ProduktObat`, `ObatBatukPilek`, `ObatBatukMurni`, `ObatPilekMurni`, `ObatKombinasiBatukPilek`, `ZatAktif`, `EnzimCYP450`, `Gejala` (`GejalaIndikasi`, `GejalaEfekSamping`, `GejalaRedFlag`), `InteraksiObat` (`InteraksiMajor`, `InteraksiModerate`, `InteraksiMinor`), `TindakLanjut` (`SegeraKeDokter`, `TanyaApoteker`, `Pantau`), `GolonganObat`, `BentukSediaan`, `KondisiPasien`, `DuplikasiTerapetik`.
     - 11 Object Properties: `memilikiKandungan`, `mengindikasikanGejala`, `memilikiEfekSamping`, `memilikiInteraksiDengan`, `menghasilkanInteraksi`, `membutuhkanTindakLanjut`, `dimetabolismeOleh`, `memilikiGolongan`, `memilikiBentukSediaan`, `diproduksiOleh`, `kontraindikasiBagi`.
     - 10 Data Properties: `namaDagang`, `namaProdusen`, `nomorBPOM`, `hargaRupiah`, `kodeATC`, `chebiID`, `doseInfoPer5mL`, `nomorSlugK24`, `urlK24`, `tingkatBukti`.
  2. **TBox Aturan Inferensi GCI (R-01 s.d. R-08):**
     - R-01: Produk dengan antitusif/ekspektoran tanpa dekongestan → `ObatBatukMurni`
     - R-02: Produk dengan dekongestan tanpa antitusif → `ObatPilekMurni`
     - R-03: Produk dengan antihistamin H1 generasi 1 → inferensi efek samping `Mengantuk`
     - R-04: Produk dengan dekongestan oral (PSE/PE) → inferensi efek samping `Palpitasi`
     - R-05: `InteraksiMajor` → membutuhkan tindak lanjut `SegeraKeDokter`
     - R-06: `InteraksiModerate` → membutuhkan tindak lanjut `TanyaApoteker` / `Pantau`
     - R-07: Produk kombinasi CTM + Diphenhydramine → terklasifikasi `DuplikasiTerapetik`
     - R-08: Produk dengan Pseudoephedrine → terinferensi `kontraindikasiBagi HipertensiTidakTerkontrol`
  3. **ABox (Individu Produk & Bukti):**
     - 12 individu produk apotek Indonesia pilihan dari katalog `produk_batuk.csv` & `produk_pilek.csv`: Siladex Cough N Cold, Actifed Plus Merah, Komix Jeruk Nipis, Vicks F44 Anak, Procold Flu & Batuk, Paramex Flu & Batuk, Alpara Kaplet, OB Combi ATT Menthol, Sanmol Forte Sirup, Triaminic Batuk Pilek, Promedex Tablet, Lapifed DM Sirup.
     - 31 individu Zat Aktif (29 zat kurasi master + Triprolidine & Doxylamine).
     - 22 individu Gejala (Symptom Ontology) dengan label dwibahasa dan triage action.
     - 11 pasangan Interaksi Obat ABox.
- Output File:
  - `out/kb_v1.owl` (132,659 bytes) | SHA-256: `fdd816fb1bf2b8684894db7490ff1f5f732f2827f8165314505175ede52d0672`
  - `out/kb_v1_lengkap.owl` (1,875,416 bytes) | SHA-256: `6728194739bdc0d9453607bb854091267feeb4a1fe253d3a9999c2d5ac821378`
- Metrik Hasil Pengukuran (`measure_kb_v1.tsv` & `measure_kb_v1_lengkap.tsv`):
  - `kb_v1.owl`: 95 Kelas, 11 Object Properties, 10 Data Properties, 86 Individu, 662 Logical Axioms, Total 1,189 Axioms. Profile: **OWL 2 DL = TRUE**.
  - `kb_v1_lengkap.owl`: 937 Kelas, 45 Object Properties, 10 Data Properties, 86 Individu, 2,681 Logical Axioms, Total 12,264 Axioms. Profile: **OWL 2 DL = TRUE**.
- Validasi Reasoner ROBOT HermiT:
  - `robot reason --reasoner HermiT --input "out/kb_v1.owl" validate-profile --profile DL`: **LULUS (100% konsisten & in profile DL)**.
  - `robot reason --reasoner HermiT --input "out/kb_v1_lengkap.owl" validate-profile --profile DL`: **LULUS (100% konsisten & in profile DL)**.


