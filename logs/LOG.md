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
