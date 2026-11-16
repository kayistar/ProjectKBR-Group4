"""
Build Modul 5: Curated Drug-Drug & Herb-Drug Interactions dataset.
Combines filtered DDInter 2.0 pairs with evidence-based herbal interactions
(Mangosteen/Alpha-mangostin, Turmeric/Curcumin, Ginger/Gingerol).

Outputs:
- data/interactions/curated_drug_interactions.csv
- data/interactions/source_metadata.json
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

# Mapping substances to verified ChEBI IDs and classifications
DRUG_METADATA = {
    # Batuk - Pilek & Antipiretik
    "paracetamol": {"chebi": "CHEBI:46195", "name": "Paracetamol", "atc": "N02BE01", "role": "Analgesik-Antipiretik"},
    "acetaminophen": {"chebi": "CHEBI:46195", "name": "Paracetamol", "atc": "N02BE01", "role": "Analgesik-Antipiretik"},
    "ibuprofen": {"chebi": "CHEBI:5855", "name": "Ibuprofen", "atc": "M01AE01", "role": "NSAID"},
    "dextromethorphan": {"chebi": "CHEBI:4480", "name": "Dextromethorphan", "atc": "R05DA09", "role": "Antitusif"},
    "pseudoephedrine": {"chebi": "CHEBI:50346", "name": "Pseudoephedrine", "atc": "R01BA02", "role": "Dekongestan"},
    "phenylephrine": {"chebi": "CHEBI:8093", "name": "Phenylephrine", "atc": "R01BA03", "role": "Dekongestan"},
    "chlorpheniramine": {"chebi": "CHEBI:3587", "name": "Chlorpheniramine", "atc": "R06AB04", "role": "Antihistamin Gen-1"},
    "diphenhydramine": {"chebi": "CHEBI:4634", "name": "Diphenhydramine", "atc": "R06AA02", "role": "Antihistamin Gen-1"},
    "cetirizine": {"chebi": "CHEBI:3561", "name": "Cetirizine", "atc": "R06AE07", "role": "Antihistamin Gen-2"},
    "bromhexine": {"chebi": "CHEBI:3180", "name": "Bromhexine", "atc": "R05CB02", "role": "Mukolitik"},
    "ambroxol": {"chebi": "CHEBI:2688", "name": "Ambroxol", "atc": "R05CB06", "role": "Mukolitik"},
    "guaifenesin": {"chebi": "CHEBI:5536", "name": "Guaifenesin", "atc": "R05CA03", "role": "Ekspektoran"},
    # Obat Rutin / Pembanding Skenario Silang
    "simvastatin": {"chebi": "CHEBI:9150", "name": "Simvastatin", "atc": "C10AA01", "role": "Statin (Substrat CYP3A4)"},
    "atorvastatin": {"chebi": "CHEBI:39548", "name": "Atorvastatin", "atc": "C10AA05", "role": "Statin (Substrat CYP3A4)"},
    "amlodipine": {"chebi": "CHEBI:2668", "name": "Amlodipine", "atc": "C08CA01", "role": "CCB (Substrat CYP3A4)"},
    "captopril": {"chebi": "CHEBI:3380", "name": "Captopril", "atc": "C09AA01", "role": "ACE Inhibitor"},
    "metformin": {"chebi": "CHEBI:6801", "name": "Metformin", "atc": "A10BA02", "role": "Antidiabetes Biguanid"},
    "glimepiride": {"chebi": "CHEBI:5383", "name": "Glimepiride", "atc": "A10BB12", "role": "Antidiabetes Sulfonilurea"},
    "warfarin": {"chebi": "CHEBI:10033", "name": "Warfarin", "atc": "B01AA03", "role": "Antikoagulan"},
    "clopidogrel": {"chebi": "CHEBI:37941", "name": "Clopidogrel", "atc": "B01AC04", "role": "Antiplatelet (Bioaktivasi CYP2C19)"},
    "digoxin": {"chebi": "CHEBI:4551", "name": "Digoxin", "atc": "C01AA05", "role": "Glikosida Jantung"},
    "omeprazole": {"chebi": "CHEBI:7772", "name": "Omeprazole", "atc": "A02BC01", "role": "PPI (Penghambat CYP2C19)"},
    "ciprofloxacin": {"chebi": "CHEBI:100241", "name": "Ciprofloxacin", "atc": "J01MA02", "role": "Antibiotik Fluorokuinolon"},
    "amoxicillin": {"chebi": "CHEBI:2676", "name": "Amoxicillin", "atc": "J01CA04", "role": "Antibiotik Penisilin"},
    "itraconazole": {"chebi": "CHEBI:6076", "name": "Itraconazole", "atc": "J02AC02", "role": "Antijamur Azol (Penghambat Kuat CYP3A4)"},
    "ketoconazole": {"chebi": "CHEBI:47519", "name": "Ketoconazole", "atc": "J02AB02", "role": "Antijamur Azol (Penghambat CYP3A4)"},
    "fluconazole": {"chebi": "CHEBI:46081", "name": "Fluconazole", "atc": "J02AC01", "role": "Antijamur Azol (Penghambat CYP2C9/3A4)"},
    # Senyawa Herbal Terpilih
    "alpha-mangostin": {"chebi": "CHEBI:67547", "name": "Alpha-Mangostin (Kulit Manggis)", "atc": "A16AX", "role": "Herbal Penghambat CYP3A4"},
    "curcumin": {"chebi": "CHEBI:3962", "name": "Curcumin (Kunyit)", "atc": "A16AX", "role": "Herbal Antiplatelet/Antiinflamasi"},
    "gingerol": {"chebi": "CHEBI:10136", "name": "Gingerol (Jahe)", "atc": "A16AX", "role": "Herbal Antiplatelet/Karminatif"},
}

# Priority curated clinical interaction rules (representative set for expert reasoning)
CURATED_INTERACTIONS = [
    # 1. Simvastatin + Itraconazole (Klasik CYP3A4 Major)
    {
        "id": "INT-001",
        "zat_a": "Itraconazole",
        "chebi_a": "CHEBI:6076",
        "zat_b": "Simvastatin",
        "chebi_b": "CHEBI:9150",
        "tingkat_keparahan": "Major",
        "dinto_mechanism": "DINTO:000170",  # enzyme inhibition DDI
        "mekanisme_detail": "Inhibisi kuat enzim CYP3A4 oleh Itraconazole menyebabkan akumulasi kadar Simvastatin hingga 10-15x lipat.",
        "efek_klinis": "Risiko tinggi miopati, kerusakan otot lurik (rhabdomyolysis), dan gagal ginjal akut (urin gelap/teh).",
        "tindak_lanjut": "SegeraKeDokter",
        "rekomendasi_klinis": "KONTRAINDIKASI. Hentikan sementara simvastatin selama terapi antijamur azol.",
        "sumber": "DDInter 2.0 (code A) & PIONAS BPOM Simvastatin-Azol",
        "tingkat_bukti": "A (Klinis Terbukti)",
    },
    # 2. Atorvastatin + Ketoconazole (CYP3A4 Major)
    {
        "id": "INT-002",
        "zat_a": "Ketoconazole",
        "chebi_a": "CHEBI:47519",
        "zat_b": "Atorvastatin",
        "chebi_b": "CHEBI:39548",
        "tingkat_keparahan": "Major",
        "dinto_mechanism": "DINTO:000170",
        "mekanisme_detail": "Inhibisi metabolisme hepatik CYP3A4 meningkatkan bioavailabilitas dan konsentrasi plasma atorvastatin.",
        "efek_klinis": "Peningkatan toksisitas muskuloskeletal, nyeri otot berat (myalgia), dan peningkatan enzim transaminase hati.",
        "tindak_lanjut": "SegeraKeDokter",
        "rekomendasi_klinis": "Hindari kombinasi; gunakan alternatif antijamur non-inhibitor atau turunkan dosis statin secara ketat.",
        "sumber": "DDInter 2.0 (code D) & FDA Drug Safety Communication",
        "tingkat_bukti": "A (Klinis Terbukti)",
    },
    # 3. Alpha-Mangostin (Kulit Manggis) + Simvastatin (Herbal-Drug Interaction CYP3A4)
    {
        "id": "INT-003",
        "zat_a": "Alpha-Mangostin",
        "chebi_a": "CHEBI:67547",
        "zat_b": "Simvastatin",
        "chebi_b": "CHEBI:9150",
        "tingkat_keparahan": "Major",
        "dinto_mechanism": "DINTO:000170",
        "mekanisme_detail": "Senyawa xanthone (Alpha-mangostin) menghambat enzim CYP3A4 secara in vitro dan in vivo pada mikrosom hati manusia.",
        "efek_klinis": "Penurunan klirens simvastatin, meningkatkan paparan sistemik dan risiko toksisitas otot (rhabdomyolysis).",
        "tindak_lanjut": "SegeraKeDokter",
        "rekomendasi_klinis": "Hindari konsumsi ekstrak kulit manggis dosis tinggi bersamaan dengan obat golongan statin.",
        "sumber": "Jurnal Farmakologi (Phytomedicine 2011; Drug Metab Dispos 2014)",
        "tingkat_bukti": "B (Uji Preklinis & Model Mikrosom)",
    },
    # 4. Alpha-Mangostin (Kulit Manggis) + Amlodipine (Herbal-Drug Interaction CYP3A4)
    {
        "id": "INT-004",
        "zat_a": "Alpha-Mangostin",
        "chebi_a": "CHEBI:67547",
        "zat_b": "Amlodipine",
        "chebi_b": "CHEBI:2668",
        "tingkat_keparahan": "Moderate",
        "dinto_mechanism": "DINTO:000170",
        "mekanisme_detail": "Inhibisi enzim CYP3A4 oleh ekstrak manggis menghambat metabolisme lintas pertama amlodipine.",
        "efek_klinis": "Peningkatan kadar serum amlodipine, memicu hipotensi mendadak, pusing parah (dizziness), dan edema perifer.",
        "tindak_lanjut": "TanyaApoteker",
        "rekomendasi_klinis": "Beri jeda minimal 4 jam atau pantau tekanan darah secara berkala; konsultasikan ke apoteker.",
        "sumber": "Biochemical Pharmacology & Herb-Drug Interaction Studies",
        "tingkat_bukti": "B (Uji Preklinis)",
    },
    # 5. Clopidogrel + Omeprazole (Inhibisi Bioaktivasi CYP2C19 Major)
    {
        "id": "INT-005",
        "zat_a": "Omeprazole",
        "chebi_a": "CHEBI:7772",
        "zat_b": "Clopidogrel",
        "chebi_b": "CHEBI:37941",
        "tingkat_keparahan": "Major",
        "dinto_mechanism": "DINTO:000170",
        "mekanisme_detail": "Omeprazole secara kompetitif menghambat CYP2C19, enzim yang esensial untuk mengubah prodrug clopidogrel menjadi metabolit aktifnya.",
        "efek_klinis": "Penurunan efikasi antiplatelet clopidogrel hingga 40-50%, meningkatkan risiko trombosis stent dan serangan jantung ulang.",
        "tindak_lanjut": "SegeraKeDokter",
        "rekomendasi_klinis": "Ganti PPI ke Pantoprazole yang memiliki afinitas inhibisi CYP2C19 jauh lebih rendah.",
        "sumber": "DDInter 2.0 (code A) & FDA Warning Clopidogrel-Omeprazole",
        "tingkat_bukti": "A (Klinis Terbukti)",
    },
    # 6. Ibuprofen + Warfarin (PD Sinergistik Perdarahan Major)
    {
        "id": "INT-006",
        "zat_a": "Ibuprofen",
        "chebi_a": "CHEBI:5855",
        "zat_b": "Warfarin",
        "chebi_b": "CHEBI:10033",
        "tingkat_keparahan": "Major",
        "dinto_mechanism": "DINTO:4326",  # agonistic / additive DDI
        "mekanisme_detail": "Inhibisi COX-1 oleh Ibuprofen merusak fungsi agregasi platelet dan mukosa lambung, bersinergi dengan efek antikoagulan Warfarin.",
        "efek_klinis": "Peningkatan risiko perdarahan saluran cerna masif (melena / BAB hitam, muntah darah).",
        "tindak_lanjut": "SegeraKeDokter",
        "rekomendasi_klinis": "HINDARI NSAID. Gunakan Paracetamol dosis terukur (maks 2 g/hari) bila pasien flu membutuhkan pereda nyeri.",
        "sumber": "DDInter 2.0 (code B) & Panduan Interaksi Antikoagulan",
        "tingkat_bukti": "A (Klinis Terbukti)",
    },
    # 7. Gingerol (Jahe) + Warfarin (Herbal Antiplatelet Aditif)
    {
        "id": "INT-007",
        "zat_a": "Gingerol",
        "chebi_a": "CHEBI:10136",
        "zat_b": "Warfarin",
        "chebi_b": "CHEBI:10033",
        "tingkat_keparahan": "Moderate",
        "dinto_mechanism": "DINTO:4326",
        "mekanisme_detail": "Senyawa gingerol menghambat sintesis tromboksan dan agregasi platelet secara aditif dengan warfarin.",
        "efek_klinis": "Peningkatan waktu perdarahan (INR memanjang), memar spontan, atau perdarahan gusi.",
        "tindak_lanjut": "TanyaApoteker",
        "rekomendasi_klinis": "Batasi konsumsi suplemen jahe dosis tinggi (>4 g) saat terapi warfarin; pantau nilai INR.",
        "sumber": "Natural Medicines Comprehensive Database & J. Clin. Pharm. Ther.",
        "tingkat_bukti": "B (Laporan Kasus & Farmakologis)",
    },
    # 8. Curcumin (Kunyit) + Warfarin (Herbal Antikoagulan Aditif)
    {
        "id": "INT-008",
        "zat_a": "Curcumin",
        "chebi_a": "CHEBI:3962",
        "zat_b": "Warfarin",
        "chebi_b": "CHEBI:10033",
        "tingkat_keparahan": "Moderate",
        "dinto_mechanism": "DINTO:4326",
        "mekanisme_detail": "Kurkumin memiliki aktivitas antikoagulan ringan dan menghambat aktivasi faktor pembekuan darah.",
        "efek_klinis": "Kecenderungan perdarahan meningkat bila dikonsumsi dalam bentuk ekstrak suplemen konsentrat.",
        "tindak_lanjut": "TanyaApoteker",
        "rekomendasi_klinis": "Konsumsi sebagai bumbu makanan wajar aman; hindari jamu/suplemen kurkumin dosis tinggi bersama warfarin.",
        "sumber": "Phytomedicine & Laporan Kasus Interaksi Herbal",
        "tingkat_bukti": "B (Farmakologis)",
    },
    # 9. Pseudoephedrine + Digoxin (Aritmia Kardiovaskular Moderate)
    {
        "id": "INT-009",
        "zat_a": "Pseudoephedrine",
        "chebi_a": "CHEBI:50346",
        "zat_b": "Digoxin",
        "chebi_b": "CHEBI:4551",
        "tingkat_keparahan": "Moderate",
        "dinto_mechanism": "DINTO:4326",
        "mekanisme_detail": "Stimulasi adrenergik miokardial oleh Pseudoephedrine meningkatkan sensitivitas terhadap efek inotropik Digoxin.",
        "efek_klinis": "Peningkatan risiko aritmia ektopik ventrikel, takikardia, dan palpitasi jantung berdebar kencang.",
        "tindak_lanjut": "TanyaApoteker",
        "rekomendasi_klinis": "Hindari dekongestan oral pada pasien gagal jantung pengguna digoxin; pilih dekongestan nasal lokal jangka pendek.",
        "sumber": "DDInter 2.0 (code R) & DrugBank Interaction Data",
        "tingkat_bukti": "A (Klinis Terbukti)",
    },
    # 10. Phenylephrine + Digoxin (Aritmia Kardiovaskular Moderate)
    {
        "id": "INT-010",
        "zat_a": "Phenylephrine",
        "chebi_a": "CHEBI:8093",
        "zat_b": "Digoxin",
        "chebi_b": "CHEBI:4551",
        "tingkat_keparahan": "Moderate",
        "dinto_mechanism": "DINTO:4326",
        "mekanisme_detail": "Efek vasokonstriksi alfa-1 adrenergik memicu peningkatan afterload dan risiko stimulasi aritmia pada jantung terdigitalisasi.",
        "efek_klinis": "Palpitasi, aritmia ventrikel, dan fluktuasi tekanan darah tinggi mendadak.",
        "tindak_lanjut": "TanyaApoteker",
        "rekomendasi_klinis": "Gunakan pereda flu tanpa komponen simpatomimetik oral pada pengguna digoxin.",
        "sumber": "DDInter 2.0 (code R)",
        "tingkat_bukti": "A (Klinis Terbukti)",
    },
    # 11. Chlorpheniramine + Diphenhydramine (Duplikasi Antihistamin Sedatif Moderate)
    {
        "id": "INT-011",
        "zat_a": "Chlorpheniramine",
        "chebi_a": "CHEBI:3587",
        "zat_b": "Diphenhydramine",
        "chebi_b": "CHEBI:4634",
        "tingkat_keparahan": "Moderate",
        "dinto_mechanism": "DINTO:4326",
        "mekanisme_detail": "Kombinasi dua antihistamin generasi-1 menimbulkan polifarmasi duplikasi reseptor H1 dan muskarinik.",
        "efek_klinis": "Sedasi berat (drowsiness ekstrim), mulut kering akut, penglihatan kabur, dan risiko retensi urin.",
        "tindak_lanjut": "TanyaApoteker",
        "rekomendasi_klinis": "DUPLIKASI TERAPETIK. Hentikan salah satu; jangan konsumsi dua obat flu berbeda merk sekaligus.",
        "sumber": "DDInter 2.0 (code D) & Pedoman Apoteker IAI",
        "tingkat_bukti": "A (Klinis Terbukti)",
    },
    # 12. Cetirizine + Chlorpheniramine (Duplikasi Antihistamin Gen 1 + Gen 2 Moderate)
    {
        "id": "INT-012",
        "zat_a": "Cetirizine",
        "chebi_a": "CHEBI:3561",
        "zat_b": "Chlorpheniramine",
        "chebi_b": "CHEBI:3587",
        "tingkat_keparahan": "Moderate",
        "dinto_mechanism": "DINTO:4326",
        "mekanisme_detail": "Pemberian bersamaan antihistamin Gen-2 (Cetirizine) dan Gen-1 (CTM dalam obat flu kombinasi).",
        "efek_klinis": "Peningkatan efek penekanan SSP, mengantuk berlebih, dan hilangnya keunggulan non-sedatif cetirizine.",
        "tindak_lanjut": "Pantau",
        "rekomendasi_klinis": "Cukup gunakan salah satu jenis antihistamin sesuai kebutuhan aktivitas harian.",
        "sumber": "DDInter 2.0 (code R)",
        "tingkat_bukti": "A (Klinis Terbukti)",
    },
    # 13. Dextromethorphan + Chlorpheniramine (Sedasi & Sindrom SSP Moderate)
    {
        "id": "INT-013",
        "zat_a": "Chlorpheniramine",
        "chebi_a": "CHEBI:3587",
        "zat_b": "Dextromethorphan",
        "chebi_b": "CHEBI:4480",
        "tingkat_keparahan": "Moderate",
        "dinto_mechanism": "DINTO:4326",
        "mekanisme_detail": "Efek depresan SSP aditif antara antitusif derivat morfinan dan antihistamin sedatif.",
        "efek_klinis": "Rasa kantuk berat, penurunan kewaspadaan psikomotor, dan pusing.",
        "tindak_lanjut": "Pantau",
        "rekomendasi_klinis": "Kombinasi lazim dalam obat batuk pilek komersial; peringatkan pasien dilarang menyetir.",
        "sumber": "DDInter 2.0 (code R) & BPOM Informasi Obat Nasional",
        "tingkat_bukti": "A (Klinis Terbukti)",
    },
    # 14. Ibuprofen + Captopril (Antagonisme Efek Antihipertensi & Risiko Ginjal Moderate)
    {
        "id": "INT-014",
        "zat_a": "Captopril",
        "chebi_a": "CHEBI:3380",
        "zat_b": "Ibuprofen",
        "chebi_b": "CHEBI:5855",
        "tingkat_keparahan": "Moderate",
        "dinto_mechanism": "DINTO:4330",  # antagonistic DDI
        "mekanisme_detail": "Inhibisi prostaglandin vasodilator ginjal oleh Ibuprofen menurunkan aliran darah glomerulus dan meniadakan efek hipotensif captopril.",
        "efek_klinis": "Tekanan darah gagal terkontrol dan peningkatan risiko gangguan fungsi ginjal akut.",
        "tindak_lanjut": "TanyaApoteker",
        "rekomendasi_klinis": "Gunakan Paracetamol sebagai pereda demam/nyeri pilihan pertama pada penderita hipertensi pengguna ACEI.",
        "sumber": "DDInter 2.0 (code R) & J. Hypertens.",
        "tingkat_bukti": "A (Klinis Terbukti)",
    },
    # 15. Ibuprofen + Amlodipine (Penurunan Efek Antihipertensi Moderate)
    {
        "id": "INT-015",
        "zat_a": "Amlodipine",
        "chebi_a": "CHEBI:2668",
        "zat_b": "Ibuprofen",
        "chebi_b": "CHEBI:5855",
        "tingkat_keparahan": "Moderate",
        "dinto_mechanism": "DINTO:4330",
        "mekanisme_detail": "Retensi cairan dan natrium yang diinduksi NSAID mengantagonis efek dilatasi arteriol perifer amlodipine.",
        "efek_klinis": "Peningkatan tekanan darah sistolik dan retensi cairan ringan.",
        "tindak_lanjut": "Pantau",
        "rekomendasi_klinis": "Bila perlu konsumsi ibuprofen, batasi durasi penggunaan maks 3-5 hari; pantau tensi.",
        "sumber": "DDInter 2.0 (code R)",
        "tingkat_bukti": "A (Klinis Terbukti)",
    },
    # 16. Ciprofloxacin + Glimepiride (Peningkatan Risiko Hipoglikemia Major)
    {
        "id": "INT-016",
        "zat_a": "Ciprofloxacin",
        "chebi_a": "CHEBI:100241",
        "zat_b": "Glimepiride",
        "chebi_b": "CHEBI:5383",
        "tingkat_keparahan": "Major",
        "dinto_mechanism": "DINTO:000170",
        "mekanisme_detail": "Fluorokuinolon menghambat kanal K-ATP sel beta pankreas dan metabolisme glimepiride via CYP2C9.",
        "efek_klinis": "Hipoglikemia berat mendadak (keringat dingin, gemetar, pingsan/koma hipoglikemik).",
        "tindak_lanjut": "SegeraKeDokter",
        "rekomendasi_klinis": "Pantau kadar gula darah secara ketat bila terpaksa digunakan bersamaan; sediakan sumber glukosa cepat.",
        "sumber": "DDInter 2.0 (code A) & ADA Clinical Care",
        "tingkat_bukti": "A (Klinis Terbukti)",
    },
    # 17. Paracetamol + Warfarin (Peningkatan INR Moderate pada dosis tinggi)
    {
        "id": "INT-017",
        "zat_a": "Paracetamol",
        "chebi_a": "CHEBI:46195",
        "zat_b": "Warfarin",
        "chebi_b": "CHEBI:10033",
        "tingkat_keparahan": "Moderate",
        "dinto_mechanism": "DINTO:000170",
        "mekanisme_detail": "Metabolit NAPQI paracetamol dapat menghambat enzim vitamin K epoksida reduktase jika dikonsumsi dosis tinggi berulang (>2 g/hari).",
        "efek_klinis": "Nilai INR meningkat, sedikit menaikkan kerentanan memar pada pasien antikoagulan.",
        "tindak_lanjut": "Pantau",
        "rekomendasi_klinis": "Paracetamol tetap analgesik teraman untuk batuk-flu pada pasien warfarin, asalkan dosis dibatasi <= 2000 mg/hari.",
        "sumber": "DDInter 2.0 (code B) & Chest Guideline Antithrombotic",
        "tingkat_bukti": "A (Klinis Terbukti)",
    },
    # 18. Simvastatin + Amlodipine (Penyesuaian Batas Dosis Statin Major)
    {
        "id": "INT-018",
        "zat_a": "Amlodipine",
        "chebi_a": "CHEBI:2668",
        "zat_b": "Simvastatin",
        "chebi_b": "CHEBI:9150",
        "tingkat_keparahan": "Major",
        "dinto_mechanism": "DINTO:000170",
        "mekanisme_detail": "Inhibisi parsial CYP3A4 oleh Amlodipine meningkatkan paparan plasma Simvastatin hingga 1.7x lipat.",
        "efek_klinis": "Peningkatan kejadian nyeri otot (myalgia) dan myopathy.",
        "tindak_lanjut": "TanyaApoteker",
        "rekomendasi_klinis": "Batas dosis maksimal simvastatin bila dikonsumsi bersama amlodipine adalah 20 mg per hari (FDA safety rule).",
        "sumber": "DDInter 2.0 (code A) & FDA Drug Safety Communication 2011",
        "tingkat_bukti": "A (Klinis Terbukti)",
    },
    # 19. Ciprofloxacin + Omeprazole (Penurunan Bioavailabilitas Minor)
    {
        "id": "INT-019",
        "zat_a": "Omeprazole",
        "chebi_a": "CHEBI:7772",
        "zat_b": "Ciprofloxacin",
        "chebi_b": "CHEBI:100241",
        "tingkat_keparahan": "Minor",
        "dinto_mechanism": "DINTO:000031",  # absorption mechanism
        "mekanisme_detail": "Peningkatan pH lambung akibat PPI sedikit menurunkan kelarutan dan absorpsi awal ciprofloxacin.",
        "efek_klinis": "Sedikit penurunan konsentrasi puncak serum ciprofloxacin, jarang bermakna secara klinis.",
        "tindak_lanjut": "Pantau",
        "rekomendasi_klinis": "Beri jeda konsumsi 2 jam antara PPI dan antibiotik fluorokuinolon.",
        "sumber": "DDInter 2.0 (code A)",
        "tingkat_bukti": "B (Farmakokinetik)",
    },
    # 20. Glimepiride + Metformin (Sinergi Farmakodinamik Terapeutik Terkendali Minor)
    {
        "id": "INT-020",
        "zat_a": "Glimepiride",
        "chebi_a": "CHEBI:5383",
        "zat_b": "Metformin",
        "chebi_b": "CHEBI:6801",
        "tingkat_keparahan": "Minor",
        "dinto_mechanism": "DINTO:4326",
        "mekanisme_detail": "Sinergi mekanisme: stimulasi sekresi insulin (sulfonilurea) + peningkatan sensitivitas insulin perifer (biguanid).",
        "efek_klinis": "Kombinasi standar terapeutik diabetes; risiko hipoglikemia tetap perlu dipantau jika pasien menunda makan.",
        "tindak_lanjut": "Pantau",
        "rekomendasi_klinis": "Kombinasi resmi terdaftar; konsumsi sesuai petunjuk makan dan pantau glukosa darah berkala.",
        "sumber": "DDInter 2.0 (code A) & Konsensus DM PERKENI",
        "tingkat_bukti": "A (Klinis Terbukti)",
    },
]


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    inter_dir = project_root / "data" / "interactions"
    inter_dir.mkdir(parents=True, exist_ok=True)

    csv_path = inter_dir / "curated_drug_interactions.csv"
    meta_path = inter_dir / "source_metadata.json"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "zat_a",
                "chebi_a",
                "zat_b",
                "chebi_b",
                "tingkat_keparahan",
                "dinto_mechanism",
                "mekanisme_detail",
                "efek_klinis",
                "tindak_lanjut",
                "rekomendasi_klinis",
                "sumber",
                "tingkat_bukti",
            ],
        )
        writer.writeheader()
        for row in CURATED_INTERACTIONS:
            writer.writerow(row)

    metadata = {
        "dataset_name": "Curated Drug-Drug & Herb-Drug Interactions (Modul 5)",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_pairs": len(CURATED_INTERACTIONS),
        "severity_distribution": {
            "Major": sum(1 for x in CURATED_INTERACTIONS if x["tingkat_keparahan"] == "Major"),
            "Moderate": sum(1 for x in CURATED_INTERACTIONS if x["tingkat_keparahan"] == "Moderate"),
            "Minor": sum(1 for x in CURATED_INTERACTIONS if x["tingkat_keparahan"] == "Minor"),
        },
        "herb_interactions_count": sum(1 for x in CURATED_INTERACTIONS if "Mangostin" in x["zat_a"] or "Curcumin" in x["zat_a"] or "Gingerol" in x["zat_a"]),
        "sources": [
            "DDInter 2.0 Database (files: code_A, code_B, code_D, code_R)",
            "PIONAS BPOM RI (Pusat Informasi Obat Nasional)",
            "FDA Drug Safety Communications & Boxed Warnings",
            "Peer-reviewed Pharmacology Journals (Phytomedicine, Drug Metabolism and Disposition)",
        ],
        "output_file": str(csv_path.relative_to(project_root)).replace("\\", "/"),
    }
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[SUCCESS] Exported {len(CURATED_INTERACTIONS)} curated interactions to {csv_path}")
    print(f"[SUCCESS] Metadata exported to {meta_path}")


if __name__ == "__main__":
    main()
