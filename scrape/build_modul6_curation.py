"""
Build Modul 6:
1. Pemetaan ATC <-> ChEBI (data/mappings/atc_chebi_mapping.csv)
2. Master Excel Kurasi 5 Sheet (data/curation/Knowledge_Base_Curation_Master.xlsx and CSVs)
   - Sheet 1: ZatAktif (Mapping ChEBI, ATC, Enzim, Brand Apotek)
   - Sheet 2: Interaksi (20 Pasangan Terkurasi + Mekanisme DINTO)
   - Sheet 3: Gejala (22 Gejala SYMP + Istilah Awam + Triase)
   - Sheet 4: Sumber (Daftar Pustaka, PIONAS, DDInter, PRO, DINTO)
   - Sheet 5: ProdukHerbal (produk herbal with product-level composition and provenance)
"""

from __future__ import annotations

import csv
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

# -----------------------------------------------------------------------------
# 1. DATA SHEET 1: ZAT AKTIF & MAPPING ATC <-> ChEBI
# -----------------------------------------------------------------------------
ZAT_AKTIF_DATA = [
    {
        "id_zat": "ZAT-001",
        "nama_zat": "Paracetamol",
        "chebi_id": "CHEBI:46195",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_46195",
        "kode_atc": "N02BE01",
        "nama_atc": "Anilides",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Analgesik-Antipiretik",
        "enzim_terkait": "CYP2E1, CYP1A2 (oksidasi minor ke NAPQI)",
        "brand_apotek": "Panadol, Sanmol, Biogesic, Bodrex Flu & Batuk, Termorex",
    },
    {
        "id_zat": "ZAT-002",
        "nama_zat": "Ibuprofen",
        "chebi_id": "CHEBI:5855",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_5855",
        "kode_atc": "M01AE01",
        "nama_atc": "Propionic acid derivatives",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "NSAID (Analgesik, Antipiretik, Antiinflamasi)",
        "enzim_terkait": "CYP2C9, CYP2C19 (substrat metabolisme)",
        "brand_apotek": "Proris, Bodrex Extra, Oskadon SP, Farsifen",
    },
    {
        "id_zat": "ZAT-003",
        "nama_zat": "Dextromethorphan",
        "chebi_id": "CHEBI:4480",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_4480",
        "kode_atc": "R05DA09",
        "nama_atc": "Opium alkaloids and derivatives",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antitusif (Penekan Batuk Kering Sentral)",
        "enzim_terkait": "CYP2D6 (O-demetilasi utama), CYP3A4",
        "brand_apotek": "Siladex Antitussive, Bisolvon Antitusif, Vicks Formula 44 Batuk Kering",
    },
    {
        "id_zat": "ZAT-004",
        "nama_zat": "Pseudoephedrine",
        "chebi_id": "CHEBI:50346",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_50346",
        "kode_atc": "R01BA02",
        "nama_atc": "Pseudoephedrine combinations",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Dekongestan Nasal Simpatomimetik",
        "enzim_terkait": "Ekskresi renal aktif (minor N-demetilasi)",
        "brand_apotek": "Actifed Kuning/Merah, Rhinos SR, Tremenza, Decolgen FX",
    },
    {
        "id_zat": "ZAT-005",
        "nama_zat": "Phenylephrine",
        "chebi_id": "CHEBI:8093",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_8093",
        "kode_atc": "R01BA03",
        "nama_atc": "Phenylephrine",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Dekongestan Nasal Agonis Alfa-1",
        "enzim_terkait": "Monoamine oxidase (MAO) metabolisme lintas pertama",
        "brand_apotek": "Bodrex Flu & Batuk Berdahak PE, Panadol Cold & Flu",
    },
    {
        "id_zat": "ZAT-006",
        "nama_zat": "Chlorpheniramine (CTM)",
        "chebi_id": "CHEBI:3587",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_3587",
        "kode_atc": "R06AB04",
        "nama_atc": "Substituted alkylamines",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antihistamin H1 Generasi 1 (Sedatif)",
        "enzim_terkait": "CYP2D6, CYP3A4",
        "brand_apotek": "CTM Generik, Mixagrip Flu, Neozep Forte, Alpara",
    },
    {
        "id_zat": "ZAT-007",
        "nama_zat": "Diphenhydramine",
        "chebi_id": "CHEBI:4634",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_4634",
        "kode_atc": "R06AA02",
        "nama_atc": "Aminoalkyl ethers",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antihistamin H1 Gen 1 & Antitusif Sedatif",
        "enzim_terkait": "CYP2D6 (inhibitor moderat & substrat)",
        "brand_apotek": "Benadryl, OBH Tropica Plus, Vicks Formula 44 Anak",
    },
    {
        "id_zat": "ZAT-008",
        "nama_zat": "Cetirizine",
        "chebi_id": "CHEBI:3561",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_3561",
        "kode_atc": "R06AE07",
        "nama_atc": "Piperazine derivatives",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antihistamin H1 Generasi 2 (Non-sedatif)",
        "enzim_terkait": "Ekskresi renal dominan (minimal hepatik)",
        "brand_apotek": "Ryvel, Incidal-OD, Ozen, Cetirizine Generik",
    },
    {
        "id_zat": "ZAT-009",
        "nama_zat": "Bromhexine",
        "chebi_id": "CHEBI:3180",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_3180",
        "kode_atc": "R05CB02",
        "nama_atc": "Mucolytics",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Mukolitik (Pengencer Dahak)",
        "enzim_terkait": "CYP3A4 (metabolisme menjadi metabolit aktif ambroxol)",
        "brand_apotek": "Bisolvon Extra, Bromika, Woods Peppermint Expectorant",
    },
    {
        "id_zat": "ZAT-010",
        "nama_zat": "Ambroxol",
        "chebi_id": "CHEBI:2688",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_2688",
        "kode_atc": "R05CB06",
        "nama_atc": "Mucolytics",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Mukolitik & Stimulator Surfaktan Paru",
        "enzim_terkait": "CYP3A4 metabolisme hepatik",
        "brand_apotek": "Mucos, Epexol, Roverton, Ambroxol Generik",
    },
    {
        "id_zat": "ZAT-011",
        "nama_zat": "Guaifenesin (Glyceryl Guaiacolate)",
        "chebi_id": "CHEBI:5536",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_5536",
        "kode_atc": "R05CA03",
        "nama_atc": "Expectorants",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Ekspektoran (Pelumas Saluran Napas)",
        "enzim_terkait": "Metabolisme oksidasi renal",
        "brand_apotek": "OBH Combi Batuk Berdahak, Komix Jahe, Anakonidin OBH",
    },
    {
        "id_zat": "ZAT-012",
        "nama_zat": "Simvastatin",
        "chebi_id": "CHEBI:9150",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_9150",
        "kode_atc": "C10AA01",
        "nama_atc": "HMG CoA reductase inhibitors",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Hipolipidemik (Statin)",
        "enzim_terkait": "CYP3A4 (substrat utama)",
        "brand_apotek": "Simvastatin Generik, Zocor, Selvim",
    },
    {
        "id_zat": "ZAT-013",
        "nama_zat": "Atorvastatin",
        "chebi_id": "CHEBI:39548",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_39548",
        "kode_atc": "C10AA05",
        "nama_atc": "HMG CoA reductase inhibitors",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Hipolipidemik (Statin Poten)",
        "enzim_terkait": "CYP3A4 (substrat utama)",
        "brand_apotek": "Lipitor, Atorvastatin Generik, Truvaz",
    },
    {
        "id_zat": "ZAT-014",
        "nama_zat": "Amlodipine",
        "chebi_id": "CHEBI:2668",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_2668",
        "kode_atc": "C08CA01",
        "nama_atc": "Dihydropyridine derivatives",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antihipertensi (Calcium Channel Blocker)",
        "enzim_terkait": "CYP3A4 (substrat)",
        "brand_apotek": "Norvask, Amlodipine Generik, Tensivask",
    },
    {
        "id_zat": "ZAT-015",
        "nama_zat": "Captopril",
        "chebi_id": "CHEBI:3380",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_3380",
        "kode_atc": "C09AA01",
        "nama_atc": "ACE inhibitors, plain",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antihipertensi (ACE Inhibitor)",
        "enzim_terkait": "Eliminasi renal 95% (efek batuk kering bradikinin)",
        "brand_apotek": "Capoten, Captopril Generik, Tensobon",
    },
    {
        "id_zat": "ZAT-016",
        "nama_zat": "Metformin",
        "chebi_id": "CHEBI:6801",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_6801",
        "kode_atc": "A10BA02",
        "nama_atc": "Biguanides",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antidiabetes Oral (Sensitizer Insulin)",
        "enzim_terkait": "Transporter OCT1, OCT2 renal (tanpa metabolisme sitokrom)",
        "brand_apotek": "Glucophage, Metformin Generik, Nevox",
    },
    {
        "id_zat": "ZAT-017",
        "nama_zat": "Glimepiride",
        "chebi_id": "CHEBI:5383",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_5383",
        "kode_atc": "A10BB12",
        "nama_atc": "Sulfonylureas",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antidiabetes Oral (Sekretagog Insulin)",
        "enzim_terkait": "CYP2C9 (substrat utama)",
        "brand_apotek": "Amaryl, Glimepiride Generik, Actaryl",
    },
    {
        "id_zat": "ZAT-018",
        "nama_zat": "Warfarin",
        "chebi_id": "CHEBI:10033",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_10033",
        "kode_atc": "B01AA03",
        "nama_atc": "Vitamin K antagonists",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antikoagulan Oral",
        "enzim_terkait": "CYP2C9 (S-enantiomer poten), CYP1A2, CYP3A4",
        "brand_apotek": "Coumadin, Simarc-2, Warfarin Generik",
    },
    {
        "id_zat": "ZAT-019",
        "nama_zat": "Clopidogrel",
        "chebi_id": "CHEBI:37941",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_37941",
        "kode_atc": "B01AC04",
        "nama_atc": "Platelet aggregation inhibitors",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antiplatelet Inhibitor Reseptor ADP P2Y12",
        "enzim_terkait": "CYP2C19 (bioaktivasi prodrug 2 langkah), CYP3A4",
        "brand_apotek": "Plavix, Clopidogrel Generik, Placta",
    },
    {
        "id_zat": "ZAT-020",
        "nama_zat": "Digoxin",
        "chebi_id": "CHEBI:4551",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_4551",
        "kode_atc": "C01AA05",
        "nama_atc": "Digitalis glycosides",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Glikosida Jantung Inotropik Positif",
        "enzim_terkait": "Substrat P-glikoprotein (P-gp), rentang terapeutik sempit",
        "brand_apotek": "Fargoxin, Digoxin Generik",
    },
    {
        "id_zat": "ZAT-021",
        "nama_zat": "Omeprazole",
        "chebi_id": "CHEBI:7772",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_7772",
        "kode_atc": "A02BC01",
        "nama_atc": "Proton pump inhibitors",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antiasam Lambung (PPI)",
        "enzim_terkait": "CYP2C19 (inhibitor kompetitif poten & substrat), CYP3A4",
        "brand_apotek": "Losec, Omeprazole Generik, Lokev",
    },
    {
        "id_zat": "ZAT-022",
        "nama_zat": "Ciprofloxacin",
        "chebi_id": "CHEBI:100241",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_100241",
        "kode_atc": "J01MA02",
        "nama_atc": "Fluoroquinolones",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antibakteri Spektrum Luas (Inhibitor DNA Girase)",
        "enzim_terkait": "CYP1A2 (inhibitor kuat), transporter renal",
        "brand_apotek": "Ciproxin, Baquinor, Ciprofloxacin Generik",
    },
    {
        "id_zat": "ZAT-023",
        "nama_zat": "Amoxicillin",
        "chebi_id": "CHEBI:2676",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_2676",
        "kode_atc": "J01CA04",
        "nama_atc": "Penicillins with extended spectrum",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antibakteri Beta-laktam",
        "enzim_terkait": "Eliminasi ginjal utuh (tanpa inhibisi sitokrom)",
        "brand_apotek": "Amoxil, Kalmoxillin, Amoxicillin Generik, Yusimox",
    },
    {
        "id_zat": "ZAT-024",
        "nama_zat": "Itraconazole",
        "chebi_id": "CHEBI:6076",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_6076",
        "kode_atc": "J02AC02",
        "nama_atc": "Triazole derivatives",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antijamur Triazol Sistemik",
        "enzim_terkait": "CYP3A4 (penghambat sangat kuat / strong inhibitor)",
        "brand_apotek": "Sporanox, Itraconazole Generik, Itrasal",
    },
    {
        "id_zat": "ZAT-025",
        "nama_zat": "Ketoconazole",
        "chebi_id": "CHEBI:47519",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_47519",
        "kode_atc": "J02AB02",
        "nama_atc": "Imidazole derivatives",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antijamur Imidazol",
        "enzim_terkait": "CYP3A4, CYP2C9 (penghambat kuat)",
        "brand_apotek": "Nizoral, Ketoconazole Generik, Mycoral",
    },
    {
        "id_zat": "ZAT-026",
        "nama_zat": "Fluconazole",
        "chebi_id": "CHEBI:46081",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_46081",
        "kode_atc": "J02AC01",
        "nama_atc": "Triazole derivatives",
        "level_atc": "ATC Level 5",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antijamur Triazol",
        "enzim_terkait": "CYP2C9, CYP2C19 (penghambat kuat), CYP3A4 (moderat)",
        "brand_apotek": "Diflucan, Fluconazole Generik, Kifluzol",
    },
    {
        "id_zat": "ZAT-027",
        "nama_zat": "Alpha-Mangostin",
        "chebi_id": "CHEBI:67547",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_67547",
        "kode_atc": "A16AX",
        "nama_atc": "Various alimentary tract and metabolism products (Herbal)",
        "level_atc": "ATC Level 4 (Proxy)",
        "kategori": "Herbal",
        "peran_farmakologis": "Antioksidan, Antiinflamasi (Kulit Manggis)",
        "enzim_terkait": "CYP3A4 (penghambat kuat in vitro / in vivo)",
        "brand_apotek": "Mastin, Garcia, Jus Manggis Xamthone",
    },
    {
        "id_zat": "ZAT-028",
        "nama_zat": "Curcumin",
        "chebi_id": "CHEBI:3962",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_3962",
        "kode_atc": "A16AX",
        "nama_atc": "Various alimentary tract and metabolism products (Herbal)",
        "level_atc": "ATC Level 4 (Proxy)",
        "kategori": "Herbal",
        "peran_farmakologis": "Hepatoprotektor & Antiinflamasi (Kunyit/Temulawak)",
        "enzim_terkait": "CYP3A4, CYP2C9 inhibisi lemah, efek antiplatelet ringan",
        "brand_apotek": "Curcuma FCT, Curvit, Jamu Kunyit Asam",
    },
    {
        "id_zat": "ZAT-029",
        "nama_zat": "Gingerol",
        "chebi_id": "CHEBI:10136",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_10136",
        "kode_atc": "A16AX",
        "nama_atc": "Various alimentary tract and metabolism products (Herbal)",
        "level_atc": "ATC Level 4 (Proxy)",
        "kategori": "Herbal",
        "peran_farmakologis": "Karminatif & Penghangat Pernapasan (Jahe Merah)",
        "enzim_terkait": "Inhibisi COX aditif, penghambatan agregasi tromboksan",
        "brand_apotek": "Tolak Angin, Antangin JRG, Komix Herbal Jahe Merah",
    },
    {
        "id_zat": "ZAT-030",
        "nama_zat": "Triprolidine",
        "chebi_id": "CHEBI:84116",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_84116",
        "kode_atc": "R06AX",
        "nama_atc": "Other antihistamines for systemic use",
        "level_atc": "ATC Level 1-4",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antihistamin H1 generasi 1 (sedatif)",
        "enzim_terkait": "",
        "brand_apotek": "Actifed Plus Cough Suppress, Lapifed DM",
    },
    {
        "id_zat": "ZAT-031",
        "nama_zat": "Doxylamine",
        "chebi_id": "CHEBI:51380",
        "chebi_iri": "http://purl.obolibrary.org/obo/CHEBI_51380",
        "kode_atc": "R06AA",
        "nama_atc": "Aminoalkyl ethers",
        "level_atc": "ATC Level 1-4",
        "kategori": "Sintetis",
        "peran_farmakologis": "Antihistamin H1 generasi 1 dengan efek sedatif",
        "enzim_terkait": "",
        "brand_apotek": "Siladex Cough N Cold, Siladex Antitussive",
    },
]

PILOT_V1_ACTIVE_INGREDIENTS = {
    "Paracetamol",
    "Dextromethorphan",
    "Pseudoephedrine",
    "Chlorpheniramine (CTM)",
    "Diphenhydramine",
    "Guaifenesin (Glyceryl Guaiacolate)",
    "Triprolidine",
    "Doxylamine",
    "Ibuprofen",
    "Warfarin",
    "Digoxin",
    "Simvastatin",
    "Amlodipine",
    "Omeprazole",
    "Clopidogrel",
}

for zat in ZAT_AKTIF_DATA:
    if zat["nama_zat"] in PILOT_V1_ACTIVE_INGREDIENTS:
        zat["cakupan_v1"] = "zat_aktif_v1"
    elif zat["kategori"] == "Herbal":
        zat["cakupan_v1"] = "senyawa_herbal_kandidat_v1"
    else:
        zat["cakupan_v1"] = "di_luar_pilot_v1"

# Product-level herbal data is kept separate from isolated plant compounds.
HERBAL_PRODUCT_DATA = [
    {
        "id_produk_herbal": "HERB-001",
        "nama_produk": "Garcia Ekstrak Kulit Manggis Kapsul",
        "nama_bahan": "Kulit buah manggis",
        "nama_botani": "Garcinia mangostana L. (belum dicantumkan pada informasi produk yang diperiksa)",
        "bagian_tanaman": "Kulit buah / perikarp",
        "bentuk_bahan": "Ekstrak kulit buah",
        "komposisi_per_kapsul": "Ekstrak kulit buah manggis 420 mg; gula sukrosa 450 mg",
        "bentuk_sediaan": "Kapsul",
        "kemasan": "Botol isi 60 kapsul",
        "dosis_tercantum": "1 kapsul, 3 kali sehari",
        "cara_penyajian": "Sesudah makan",
        "nomor_izin_edar": "TR113328811",
        "pendaftar_bpom": "PT Zena Nirmala Sentosa",
        "status_verifikasi_bpom": "Entri NIE ditemukan di Cek BPOM; status aktif/berlaku belum dikonfirmasi terpisah",
        "kadar_alpha_mangostin": "Tidak dicantumkan / tidak diketahui",
        "hubungan_dengan_alpha_mangostin": "Senyawa bioaktif dapat menjadi kandidat untuk ditelusuri; tidak ada klaim kadar atau standardisasi produk pada sumber yang diperiksa",
        "sumber_data_produk": "REF-11",
        "sumber_verifikasi_registrasi": "REF-12",
        "tanggal_akses": "2026-11-16",
        "catatan_kurasi": "Data komposisi dan dosis berasal dari halaman apotek K24Klik, bukan transkripsi label kemasan. Gunakan sebagai data produk awal dan verifikasi label bila tersedia.",
    },
]

# -----------------------------------------------------------------------------
# 2. DATA SHEET 4: DAFTAR SUMBER BUKTI & REGULASI
# -----------------------------------------------------------------------------
SUMBER_DATA = [
    {
        "id_sumber": "REF-01",
        "nama": "DDInter 2.0 Database",
        "tipe": "Database Interaksi Obat Terkurasi",
        "cakupan": "Interaksi berpasangan (code A, B, D, R) dengan tingkat keparahan Major, Moderate, Minor.",
        "url_purl": "http://ddinter.scbdd.com",
        "tingkat_bukti": "A (Klinis / Literatur Terverifikasi)",
        "tanggal_akses": "2026-11-08",
    },
    {
        "id_sumber": "REF-02",
        "nama": "PIONAS BPOM RI (Pusat Informasi Obat Nasional)",
        "tipe": "Pedoman Resmi Regulator Farmasi Indonesia",
        "cakupan": "Informasi keamanan obat, kontraindikasi, dosis batas statin, dan peringatan interaksi.",
        "url_purl": "https://pionas.pom.go.id",
        "tingkat_bukti": "A (Regulator Resmi)",
        "tanggal_akses": "2026-11-15",
    },
    {
        "id_sumber": "REF-03",
        "nama": "ChEBI (Chemical Entities of Biological Interest)",
        "tipe": "Ontologi Kimia & Farmakologi Biomedis (EMBL-EBI)",
        "cakupan": "Identifier resmi zat aktif (CHEBI_xxxxx), struktur molekul, dan hierarki klasifikasi kimia.",
        "url_purl": "http://purl.obolibrary.org/obo/chebi.owl",
        "tingkat_bukti": "A (Ontologi Baku OBO Foundry)",
        "tanggal_akses": "2026-11-16",
    },
    {
        "id_sumber": "REF-04",
        "nama": "DrON (The Drug Ontology)",
        "tipe": "Ontologi Produk & Disposisi Terkait Obat",
        "cakupan": "Disposisi metabolisme CYP2C19/CYP2D6 dan konsep produk bahan aktif farmasi.",
        "url_purl": "http://purl.obolibrary.org/obo/dron.owl",
        "tingkat_bukti": "A (Ontologi Baku)",
        "tanggal_akses": "2026-11-15",
    },
    {
        "id_sumber": "REF-05",
        "nama": "Protein Ontology (PRO) via OLS4 API",
        "tipe": "Ontologi Protein & Enzim Manusia",
        "cakupan": "Kelas enzim CYP450 manusia (PR:P08684 CYP3A4, PR:P10635 CYP2D6, PR:P33261 CYP2C19, PR:P11712 CYP2C9).",
        "url_purl": "https://www.ebi.ac.uk/ols4/ontologies/pr",
        "tingkat_bukti": "A (UniProt / OLS4 API)",
        "tanggal_akses": "2026-11-15",
    },
    {
        "id_sumber": "REF-06",
        "nama": "DINTO (Drug-Drug Interactions Ontology 1.2)",
        "tipe": "Ontologi Mekanisme Interaksi Farmakologis",
        "cakupan": "Kosakata formal mekanisme PK/PD, peran precipitant/object, dan relasi alters/is_preceded_by.",
        "url_purl": "https://github.com/labda/DINTO",
        "tingkat_bukti": "A (OBO Foundry / Universidad Carlos III)",
        "tanggal_akses": "2026-11-15",
    },
    {
        "id_sumber": "REF-07",
        "nama": "Symptom Ontology (SYMP)",
        "tipe": "Ontologi Gejala & Tanda Klinis Penyakit Manusia",
        "cakupan": "Gejala batuk-pilek, efek samping antihistamin/dekongestan, dan tanda bahaya (red flags).",
        "url_purl": "http://purl.obolibrary.org/obo/symp.owl",
        "tingkat_bukti": "A (OBO Foundry)",
        "tanggal_akses": "2026-11-15",
    },
    {
        "id_sumber": "REF-08",
        "nama": "NLM RxClass API (National Library of Medicine)",
        "tipe": "Klasifikasi Terapeutik ATC WHO",
        "cakupan": "Klasifikasi ATC Level 1-4 untuk sistem pernapasan (R), kardiovaskular (C), dan pencernaan (A).",
        "url_purl": "https://rxnav.nlm.nih.gov/REST/rxclass",
        "tingkat_bukti": "A (WHO Collaborating Centre / NLM)",
        "tanggal_akses": "2026-11-16",
    },
    {
        "id_sumber": "REF-09",
        "nama": "Jurnal Farmakologi Herbal (Phytomedicine & Drug Metab Dispos)",
        "tipe": "Publikasi Ilmiah Internasional Peer-Reviewed",
        "cakupan": "Bukti inhibisi CYP3A4 oleh ekstrak Kulit Manggis (Alpha-mangostin) dan sinergi antiplatelet Jahe/Kunyit.",
        "url_purl": "DOI: 10.1016/j.phymed.2011.01.010 & DOI: 10.1124/dmd.108.022988",
        "tingkat_bukti": "B (Uji Farmakokinetik & Mikrosom Manusia)",
        "tanggal_akses": "2026-11-15",
    },
    {
        "id_sumber": "REF-10",
        "nama": "FDA Drug Safety Communications & Boxed Warnings",
        "tipe": "Peringatan Keamanan Obat Klinis Regulator AS",
        "cakupan": "Batas dosis interaksi Simvastatin + Amlodipine (maks 20 mg/hari) dan kontraindikasi Clopidogrel + Omeprazole.",
        "url_purl": "https://www.fda.gov/drugs/drug-safety-and-availability",
        "tingkat_bukti": "A (Regulator Klinis)",
        "tanggal_akses": "2026-11-15",
    },
    {
        "id_sumber": "REF-11",
        "nama": "K24Klik - Garcia Ekstrak Kulit Manggis",
        "tipe": "Katalog apotek daring; informasi produk ditinjau apoteker K24Klik",
        "cakupan": "Komposisi, bentuk sediaan, kemasan, dosis tercantum, NIE, dan pendaftar produk Garcia.",
        "url_purl": "https://www.k24klik.com/p/GARCIA-EKSTRAK-KULIT-MANGGIS-CAP-60S-BTL-1180",
        "tingkat_bukti": "Sumber sekunder produk; bukan label kemasan",
        "tanggal_akses": "2026-11-16",
    },
    {
        "id_sumber": "REF-12",
        "nama": "BPOM - Cek Produk",
        "tipe": "Basis data registrasi produk resmi BPOM",
        "cakupan": "Entri registrasi TR113328811 untuk GARCIA, termasuk pendaftar dan kemasan terdaftar.",
        "url_purl": "https://cekbpom.pom.go.id/all-produk?query=TR113328811",
        "tingkat_bukti": "A (Regulator resmi; identitas/registrasi produk)",
        "tanggal_akses": "2026-11-16",
    },
    {
        "id_sumber": "REF-13",
        "nama": "DDInter 2.0 - Digoxin and Pseudoephedrine interaction record 7594",
        "tipe": "Basis data interaksi obat terkurasi",
        "cakupan": "Klasifikasi Moderate, uraian risiko aritmia, saran kehati-hatian dan pemantauan ECG untuk Digoxin + Pseudoephedrine.",
        "url_purl": "https://ddinter2.scbdd.com/server/interact/7594/",
        "tingkat_bukti": "Sumber sekunder terkurasi; bukan uji klinis primer",
        "tanggal_akses": "2026-11-19",
    },
    {
        "id_sumber": "REF-14",
        "nama": "DailyMed - Allegra-D (fexofenadine/pseudoephedrine) label",
        "tipe": "Label obat di basis data National Library of Medicine",
        "cakupan": "Peringatan aktivitas pacemaker ektopik saat pseudoephedrine digunakan bersama digitalis.",
        "url_purl": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=121362c5-3a59-42f8-b721-fa0342d99c4b",
        "tingkat_bukti": "Label regulator; versi arsip, tidak memberi kelas keparahan",
        "tanggal_akses": "2026-11-19",
    },
]


def write_csv_file(path: Path, data: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"Saved CSV: {path} ({len(data)} rows)")


def build_minimal_xlsx(dest_xlsx: Path, sheets_dict: dict[str, list[dict]]) -> None:
    """
    Build a clean, compliant multi-sheet .xlsx file without external dependencies
    using Python standard library zipfile.
    """
    dest_xlsx.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. Content Types
    content_types = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '    <Default Extension="xml" ContentType="application/xml"/>',
        '    <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
    ]
    for idx in range(1, len(sheets_dict) + 1):
        content_types.append(f'    <Override PartName="/xl/worksheets/sheet{idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
    content_types.append('</Types>')

    # 2. Package relationships (_rels/.rels)
    package_rels = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
        '    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>',
        '</Relationships>',
    ]

    # 3. Workbook relationships (xl/_rels/workbook.xml.rels)
    wb_rels = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
    ]
    for idx in range(1, len(sheets_dict) + 1):
        wb_rels.append(f'    <Relationship Id="rId{idx}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{idx}.xml"/>')
    wb_rels.append('</Relationships>')

    # 4. Workbook (xl/workbook.xml)
    wb_xml = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',
        '    <sheets>',
    ]
    for idx, name in enumerate(sheets_dict.keys(), start=1):
        wb_xml.append(f'        <sheet name="{escape(name)}" sheetId="{idx}" r:id="rId{idx}"/>')
    wb_xml.append('    </sheets>')
    wb_xml.append('</workbook>')

    # 5. Worksheets (xl/worksheets/sheetX.xml)
    def make_cell(col_idx: int, row_idx: int, val: str) -> str:
        # Col to letters
        col_letters = ""
        temp = col_idx
        while temp > 0:
            temp, remainder = divmod(temp - 1, 26)
            col_letters = chr(65 + remainder) + col_letters
        cell_ref = f"{col_letters}{row_idx}"
        return f'<c r="{cell_ref}" t="inlineStr"><is><t>{escape(str(val))}</t></is></c>'

    sheet_xmls = {}
    for idx, (s_name, rows) in enumerate(sheets_dict.items(), start=1):
        lines = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
            '    <sheetData>',
        ]
        if rows:
            # Header
            headers = list(rows[0].keys())
            header_cells = "".join(make_cell(c, 1, h) for c, h in enumerate(headers, start=1))
            lines.append(f'        <row r="1">{header_cells}</row>')
            # Rows
            for r_idx, row in enumerate(rows, start=2):
                row_cells = "".join(make_cell(c, r_idx, row.get(h, "")) for c, h in enumerate(headers, start=1))
                lines.append(f'        <row r="{r_idx}">{row_cells}</row>')
        lines.append('    </sheetData>')
        lines.append('</worksheet>')
        sheet_xmls[f"xl/worksheets/sheet{idx}.xml"] = "\n".join(lines)

    # Write zip file
    with zipfile.ZipFile(dest_xlsx, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", "\n".join(content_types))
        zf.writestr("_rels/.rels", "\n".join(package_rels))
        zf.writestr("xl/_rels/workbook.xml.rels", "\n".join(wb_rels))
        zf.writestr("xl/workbook.xml", "\n".join(wb_xml))
        for path_in_zip, xml_content in sheet_xmls.items():
            zf.writestr(path_in_zip, xml_content)

    print(f"Generated multi-sheet XLSX: {dest_xlsx} ({dest_xlsx.stat().st_size:,} bytes)")


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    curation_dir = project_root / "data" / "curation"
    mapping_dir = project_root / "data" / "mappings"
    curation_dir.mkdir(parents=True, exist_ok=True)
    mapping_dir.mkdir(parents=True, exist_ok=True)

    # 1. Read curated interactions from Modul 5
    inter_csv = project_root / "data" / "interactions" / "curated_drug_interactions.csv"
    with inter_csv.open("r", encoding="utf-8") as f:
        inter_rows = list(csv.DictReader(f))
    evidence_csv = project_root / "data" / "interactions" / "interaction_evidence.csv"
    with evidence_csv.open("r", encoding="utf-8-sig") as f:
        evidence_rows = list(csv.DictReader(f))
    known_source_ids = {row["id_sumber"] for row in SUMBER_DATA}
    known_interaction_ids = {row["id"] for row in inter_rows}
    for row in evidence_rows:
        if row["id_sumber"] not in known_source_ids:
            raise ValueError(f'Unknown evidence source ID: {row["id_sumber"]}')
        if row["id_interaksi"] not in known_interaction_ids:
            raise ValueError(f'Unknown interaction ID: {row["id_interaksi"]}')

    # 2. Read curated symptoms from Modul 4
    symp_csv = project_root / "data" / "symptoms" / "symptoms_selected.csv"
    with symp_csv.open("r", encoding="utf-8") as f:
        symp_rows = list(csv.DictReader(f))

    pilot_active = [row for row in ZAT_AKTIF_DATA if row["cakupan_v1"] == "zat_aktif_v1"]
    herbal_constituents = [
        row for row in ZAT_AKTIF_DATA
        if row["cakupan_v1"] == "senyawa_herbal_kandidat_v1"
    ]
    pilot_symptoms = [row for row in symp_rows if row["cakupan_v1"] == "pilot"]
    if len(pilot_active) != 15:
        raise ValueError(f"Pilot scope requires 15 active ingredients; found {len(pilot_active)}")
    if not 2 <= len(herbal_constituents) <= 3:
        raise ValueError(
            f"Pilot scope requires 2-3 herbal constituent candidates; found {len(herbal_constituents)}"
        )
    if not 10 <= len(pilot_symptoms) <= 15:
        raise ValueError(f"Pilot scope requires 10-15 symptoms; found {len(pilot_symptoms)}")

    # 3. Export standalone mapping ATC <-> ChEBI
    atc_mapping_fields = ["id_zat", "nama_zat", "chebi_id", "chebi_iri", "kode_atc", "nama_atc", "level_atc", "kategori", "peran_farmakologis", "enzim_terkait"]
    atc_mapping_data = [{k: row[k] for k in atc_mapping_fields} for row in ZAT_AKTIF_DATA]
    write_csv_file(mapping_dir / "atc_chebi_mapping.csv", atc_mapping_data, atc_mapping_fields)

    # 4. Export CSV per Sheet
    write_csv_file(curation_dir / "sheet1_zat_aktif.csv", ZAT_AKTIF_DATA, list(ZAT_AKTIF_DATA[0].keys()))
    write_csv_file(curation_dir / "sheet2_interaksi.csv", inter_rows, list(inter_rows[0].keys()))
    write_csv_file(curation_dir / "evidence_interaksi.csv", evidence_rows, list(evidence_rows[0].keys()))
    write_csv_file(curation_dir / "sheet3_gejala.csv", symp_rows, list(symp_rows[0].keys()))
    write_csv_file(curation_dir / "sheet4_sumber.csv", SUMBER_DATA, list(SUMBER_DATA[0].keys()))
    write_csv_file(curation_dir / "sheet5_produk_herbal.csv", HERBAL_PRODUCT_DATA, list(HERBAL_PRODUCT_DATA[0].keys()))

    # 5. Build Master Multi-Sheet XLSX
    sheets = {
        "ZatAktif": ZAT_AKTIF_DATA,
        "Interaksi": inter_rows,
        "BuktiInteraksi": evidence_rows,
        "Gejala": symp_rows,
        "Sumber": SUMBER_DATA,
        "ProdukHerbal": HERBAL_PRODUCT_DATA,
    }
    master_xlsx = curation_dir / "Knowledge_Base_Curation_Master.xlsx"
    build_minimal_xlsx(master_xlsx, sheets)

    # 6. Export Metadata Provenance
    metadata = {
        "title": "Master Knowledge Base Curation (Modul 6)",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "summary": "6-sheet curation workbook combining ATC-ChEBI mappings, curated DDIs, interaction evidence provenance, symptoms triage, sources, and herbal products.",
        "pilot_scope": {
            "active_ingredients_selected": len(pilot_active),
            "active_ingredient_ids": [row["id_zat"] for row in pilot_active],
            "herbal_constituent_candidates": [
                row["nama_zat"] for row in herbal_constituents
            ],
            "herbal_product_records": len(HERBAL_PRODUCT_DATA),
            "pilot_symptoms": len(pilot_symptoms),
            "total_symptoms_curated": len(symp_rows),
        },
        "sheets": {
            "Sheet1_ZatAktif": {"count": len(ZAT_AKTIF_DATA), "csv": "data/curation/sheet1_zat_aktif.csv"},
            "Sheet2_Interaksi": {"count": len(inter_rows), "csv": "data/curation/sheet2_interaksi.csv"},
            "Evidence_Interaksi": {"count": len(evidence_rows), "csv": "data/curation/evidence_interaksi.csv"},
            "Sheet3_Gejala": {"count": len(symp_rows), "csv": "data/curation/sheet3_gejala.csv"},
            "Sheet4_Sumber": {"count": len(SUMBER_DATA), "csv": "data/curation/sheet4_sumber.csv"},
            "Sheet5_ProdukHerbal": {"count": len(HERBAL_PRODUCT_DATA), "csv": "data/curation/sheet5_produk_herbal.csv"},
        },
        "mapping_file": "data/mappings/atc_chebi_mapping.csv",
        "master_xlsx": "data/curation/Knowledge_Base_Curation_Master.xlsx",
    }
    (curation_dir / "source_metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n[SUCCESS] Modul 6 curation build completed successfully!")


if __name__ == "__main__":
    main()
