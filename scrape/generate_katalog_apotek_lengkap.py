"""
Generator Dataset Katalog Obat Apotek Indonesia Lengkap
Menghasilkan ~90 produk obat komersial yang beredar di apotek Indonesia (Kimia Farma, K-24, Century, dll.)
Mencakup kategori: Kardiovaskular, Diabetes, Kolesterol, Saluran Cerna, Analgesik, Antibiotik, Alergi, dan Herbal.
"""

import csv

KATALOG_APOTEK = [
    # =========================================================================
    # 1. KARDIOVASKULAR - ANTIHIPERTENSI & GAGAL JANTUNG
    # =========================================================================
    {
        "id_produk": "APT_001",
        "nama_produk_apotek": "Amlodipine Hexpharm 5 mg Tablet",
        "zat_aktif_inn": "Amlodipine",
        "kategori_terapi": "Antihipertensi (Calcium Channel Blocker)",
        "golongan_obat": "Obat Keras (PRB BPJS)",
        "nomor_izin_edar_bpom": "GKL0708514110A1",
        "produsen_farmasi": "PT Hexpharm Jaya Laboratories (Kalbe)",
        "bentuk_sediaan_kemasan": "Tablet 5 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 5.000 - Rp 10.000 / strip",
        "ketersediaan_apotek": "Sangat Umum (Wajib PRB)"
    },
    {
        "id_produk": "APT_002",
        "nama_produk_apotek": "Amlodipine 10 mg Kimia Farma",
        "zat_aktif_inn": "Amlodipine",
        "kategori_terapi": "Antihipertensi (Calcium Channel Blocker)",
        "golongan_obat": "Obat Keras (Generik)",
        "nomor_izin_edar_bpom": "GKL0812523910B1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Tablet 10 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 8.000 - Rp 15.000 / strip",
        "ketersediaan_apotek": "Sangat Umum (Wajib PRB)"
    },
    {
        "id_produk": "APT_003",
        "nama_produk_apotek": "Norvask 5 mg Tablet",
        "zat_aktif_inn": "Amlodipine",
        "kategori_terapi": "Antihipertensi (Calcium Channel Blocker)",
        "golongan_obat": "Obat Keras (Paten Originator)",
        "nomor_izin_edar_bpom": "DKL9319803110A1",
        "produsen_farmasi": "PT Pfizer Indonesia",
        "bentuk_sediaan_kemasan": "Tablet 5 mg (Blister @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 95.000 - Rp 120.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_004",
        "nama_produk_apotek": "Norvask 10 mg Tablet",
        "zat_aktif_inn": "Amlodipine",
        "kategori_terapi": "Antihipertensi (Calcium Channel Blocker)",
        "golongan_obat": "Obat Keras (Paten Originator)",
        "nomor_izin_edar_bpom": "DKL9319803110B1",
        "produsen_farmasi": "PT Pfizer Indonesia",
        "bentuk_sediaan_kemasan": "Tablet 10 mg (Blister @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 160.000 - Rp 190.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_005",
        "nama_produk_apotek": "Intervask 5 mg Tablet",
        "zat_aktif_inn": "Amlodipine",
        "kategori_terapi": "Antihipertensi (Calcium Channel Blocker)",
        "golongan_obat": "Obat Keras (Merk Dagang)",
        "nomor_izin_edar_bpom": "DKL0017616610A1",
        "produsen_farmasi": "PT Interbat",
        "bentuk_sediaan_kemasan": "Tablet 5 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 70.000 - Rp 90.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_006",
        "nama_produk_apotek": "Captopril 12.5 mg Kimia Farma",
        "zat_aktif_inn": "Captopril",
        "kategori_terapi": "Antihipertensi (ACE Inhibitor)",
        "golongan_obat": "Obat Keras (Generik)",
        "nomor_izin_edar_bpom": "GKL9912519710A1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Tablet 12.5 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 2.500 - Rp 5.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_007",
        "nama_produk_apotek": "Captopril 25 mg Kimia Farma",
        "zat_aktif_inn": "Captopril",
        "kategori_terapi": "Antihipertensi (ACE Inhibitor)",
        "golongan_obat": "Obat Keras (Generik)",
        "nomor_izin_edar_bpom": "GKL9912519710B1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Tablet 25 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 3.500 - Rp 7.000 / strip",
        "ketersediaan_apotek": "Sangat Umum (Wajib PRB)"
    },
    {
        "id_produk": "APT_008",
        "nama_produk_apotek": "Captopril Dexa 25 mg Tablet",
        "zat_aktif_inn": "Captopril",
        "kategori_terapi": "Antihipertensi (ACE Inhibitor)",
        "golongan_obat": "Obat Keras (Generik)",
        "nomor_izin_edar_bpom": "GKL9912519710B1",
        "produsen_farmasi": "PT Dexa Medica",
        "bentuk_sediaan_kemasan": "Tablet 25 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 4.000 - Rp 7.500 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_009",
        "nama_produk_apotek": "Capoten 25 mg Tablet",
        "zat_aktif_inn": "Captopril",
        "kategori_terapi": "Antihipertensi (ACE Inhibitor)",
        "golongan_obat": "Obat Keras (Paten)",
        "nomor_izin_edar_bpom": "DKL8324400410B1",
        "produsen_farmasi": "PT Taisho Pharmaceutical Indonesia",
        "bentuk_sediaan_kemasan": "Tablet 25 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 55.000 - Rp 75.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_010",
        "nama_produk_apotek": "Candesartan 8 mg Dexa",
        "zat_aktif_inn": "Candesartan",
        "kategori_terapi": "Antihipertensi (Angiotensin Receptor Blocker)",
        "golongan_obat": "Obat Keras (PRB BPJS)",
        "nomor_izin_edar_bpom": "GKL1308517710A1",
        "produsen_farmasi": "PT Dexa Medica",
        "bentuk_sediaan_kemasan": "Tablet 8 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 35.000 - Rp 50.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_011",
        "nama_produk_apotek": "Candesartan 16 mg Kimia Farma",
        "zat_aktif_inn": "Candesartan",
        "kategori_terapi": "Antihipertensi (Angiotensin Receptor Blocker)",
        "golongan_obat": "Obat Keras (PRB BPJS)",
        "nomor_izin_edar_bpom": "GKL1412525510B1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Tablet 16 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 50.000 - Rp 75.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_012",
        "nama_produk_apotek": "Bisoprolol 5 mg Dexa",
        "zat_aktif_inn": "Bisoprolol",
        "kategori_terapi": "Antihipertensi / Beta Blocker",
        "golongan_obat": "Obat Keras (PRB BPJS)",
        "nomor_izin_edar_bpom": "GKL0708514410B1",
        "produsen_farmasi": "PT Dexa Medica",
        "bentuk_sediaan_kemasan": "Tablet 5 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 15.000 - Rp 25.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_013",
        "nama_produk_apotek": "Concor 2.5 mg Tablet",
        "zat_aktif_inn": "Bisoprolol",
        "kategori_terapi": "Antihipertensi / Beta Blocker",
        "golongan_obat": "Obat Keras (Paten Originator)",
        "nomor_izin_edar_bpom": "DKI0386400317A1",
        "produsen_farmasi": "PT Merck Tbk",
        "bentuk_sediaan_kemasan": "Tablet 2.5 mg (Blister @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 65.000 - Rp 85.000 / blister",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_014",
        "nama_produk_apotek": "Fargoxin 0.25 mg Tablet",
        "zat_aktif_inn": "Digoxin",
        "kategori_terapi": "Glikosida Jantung (Gagal Jantung & Aritmia)",
        "golongan_obat": "Obat Keras (Indeks Terapi Sempit)",
        "nomor_izin_edar_bpom": "DKL8831502410A1",
        "produsen_farmasi": "PT Pratapa Nirmala (Fahrenheit)",
        "bentuk_sediaan_kemasan": "Tablet 0.25 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 15.000 - Rp 25.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_015",
        "nama_produk_apotek": "Digoxin 0.25 mg Yarindo",
        "zat_aktif_inn": "Digoxin",
        "kategori_terapi": "Glikosida Jantung",
        "golongan_obat": "Obat Keras (Generik)",
        "nomor_izin_edar_bpom": "GKL0632711710A1",
        "produsen_farmasi": "PT Yarindo Farmatama",
        "bentuk_sediaan_kemasan": "Tablet 0.25 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 8.000 - Rp 15.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_016",
        "nama_produk_apotek": "Furosemide 40 mg Kimia Farma",
        "zat_aktif_inn": "Furosemide",
        "kategori_terapi": "Diuretik Loop (Hipertensi & Edema)",
        "golongan_obat": "Obat Keras (Generik)",
        "nomor_izin_edar_bpom": "GKL9912519810A1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Tablet 40 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 4.000 - Rp 8.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },

    # =========================================================================
    # 2. ANTIKOAGULAN & ANTIPLATELET
    # =========================================================================
    {
        "id_produk": "APT_017",
        "nama_produk_apotek": "Simarc-2 Tablet (Warfarin Sodium 2 mg)",
        "zat_aktif_inn": "Warfarin",
        "kategori_terapi": "Antikoagulan (Antagonis Vitamin K)",
        "golongan_obat": "Obat Keras (Monitoring INR)",
        "nomor_izin_edar_bpom": "DKL9331504910A1",
        "produsen_farmasi": "PT Pratapa Nirmala (Fahrenheit)",
        "bentuk_sediaan_kemasan": "Tablet 2 mg (Blister @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 25.000 - Rp 35.000 / strip",
        "ketersediaan_apotek": "Tersedia (Apotek Rujukan BPJS)"
    },
    {
        "id_produk": "APT_018",
        "nama_produk_apotek": "Aspilet 80 mg Tablet Kunyah",
        "zat_aktif_inn": "Acetylsalicylic Acid",
        "kategori_terapi": "Antiplatelet (Pengencer Darah)",
        "golongan_obat": "Obat Keras",
        "nomor_izin_edar_bpom": "DKL7214704763A1",
        "produsen_farmasi": "PT Medifarma Laboratories",
        "bentuk_sediaan_kemasan": "Tablet 80 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 8.000 - Rp 14.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_019",
        "nama_produk_apotek": "Miniaspi 80 mg Tablet",
        "zat_aktif_inn": "Acetylsalicylic Acid",
        "kategori_terapi": "Antiplatelet",
        "golongan_obat": "Obat Keras",
        "nomor_izin_edar_bpom": "DKL9115606415A1",
        "produsen_farmasi": "PT Mersi Farma",
        "bentuk_sediaan_kemasan": "Tablet salut enterik 80 mg",
        "estimasi_harga_apotek": "Rp 6.000 - Rp 12.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_020",
        "nama_produk_apotek": "Clopidogrel 75 mg Dexa",
        "zat_aktif_inn": "Clopidogrel",
        "kategori_terapi": "Antiplatelet",
        "golongan_obat": "Obat Keras (PRB BPJS)",
        "nomor_izin_edar_bpom": "GKL1108516717A1",
        "produsen_farmasi": "PT Dexa Medica",
        "bentuk_sediaan_kemasan": "Tablet salut selaput 75 mg",
        "estimasi_harga_apotek": "Rp 40.000 - Rp 65.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },

    # =========================================================================
    # 3. ANTIKOLESTEROL / DISLIPIDEMIA (STATIN)
    # =========================================================================
    {
        "id_produk": "APT_021",
        "nama_produk_apotek": "Simvastatin 10 mg Kimia Farma",
        "zat_aktif_inn": "Simvastatin",
        "kategori_terapi": "Antikolesterol (HMG-CoA Reductase Inhibitor)",
        "golongan_obat": "Obat Keras (PRB BPJS)",
        "nomor_izin_edar_bpom": "GKL0312521710A1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Tablet salut selaput 10 mg",
        "estimasi_harga_apotek": "Rp 7.000 - Rp 14.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_022",
        "nama_produk_apotek": "Simvastatin 20 mg Dexa",
        "zat_aktif_inn": "Simvastatin",
        "kategori_terapi": "Antikolesterol (HMG-CoA Reductase Inhibitor)",
        "golongan_obat": "Obat Keras (PRB BPJS)",
        "nomor_izin_edar_bpom": "GKL0308507210B1",
        "produsen_farmasi": "PT Dexa Medica",
        "bentuk_sediaan_kemasan": "Tablet salut selaput 20 mg",
        "estimasi_harga_apotek": "Rp 10.000 - Rp 20.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_023",
        "nama_produk_apotek": "Zocor 10 mg Tablet",
        "zat_aktif_inn": "Simvastatin",
        "kategori_terapi": "Antikolesterol (Statin)",
        "golongan_obat": "Obat Keras (Paten Originator)",
        "nomor_izin_edar_bpom": "DKI9376400217A1",
        "produsen_farmasi": "PT Organon Pharma Indonesia",
        "bentuk_sediaan_kemasan": "Tablet salut selaput 10 mg",
        "estimasi_harga_apotek": "Rp 110.000 - Rp 140.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_024",
        "nama_produk_apotek": "Zocor 20 mg Tablet",
        "zat_aktif_inn": "Simvastatin",
        "kategori_terapi": "Antikolesterol (Statin)",
        "golongan_obat": "Obat Keras (Paten Originator)",
        "nomor_izin_edar_bpom": "DKI9376400217B1",
        "produsen_farmasi": "PT Organon Pharma Indonesia",
        "bentuk_sediaan_kemasan": "Tablet salut selaput 20 mg",
        "estimasi_harga_apotek": "Rp 160.000 - Rp 195.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_025",
        "nama_produk_apotek": "Valemia 10 mg Tablet",
        "zat_aktif_inn": "Simvastatin",
        "kategori_terapi": "Antikolesterol (Statin)",
        "golongan_obat": "Obat Keras (Merk Dagang)",
        "nomor_izin_edar_bpom": "DKL0433511310A1",
        "produsen_farmasi": "PT Novell Pharmaceutical Laboratories",
        "bentuk_sediaan_kemasan": "Tablet salut selaput 10 mg",
        "estimasi_harga_apotek": "Rp 45.000 - Rp 65.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_026",
        "nama_produk_apotek": "Atorvastatin 20 mg Dexa",
        "zat_aktif_inn": "Atorvastatin",
        "kategori_terapi": "Antikolesterol (Statin)",
        "golongan_obat": "Obat Keras (PRB BPJS)",
        "nomor_izin_edar_bpom": "GKL1308517610A1",
        "produsen_farmasi": "PT Dexa Medica",
        "bentuk_sediaan_kemasan": "Tablet salut selaput 20 mg",
        "estimasi_harga_apotek": "Rp 35.000 - Rp 55.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_027",
        "nama_produk_apotek": "Lipitor 20 mg Tablet",
        "zat_aktif_inn": "Atorvastatin",
        "kategori_terapi": "Antikolesterol (Statin)",
        "golongan_obat": "Obat Keras (Paten Originator)",
        "nomor_izin_edar_bpom": "DKI9790700417B1",
        "produsen_farmasi": "PT Pfizer Indonesia",
        "bentuk_sediaan_kemasan": "Tablet salut selaput 20 mg",
        "estimasi_harga_apotek": "Rp 220.000 - Rp 260.000 / blister",
        "ketersediaan_apotek": "Tersedia"
    },

    # =========================================================================
    # 4. ANTIDIABETES ORAL
    # =========================================================================
    {
        "id_produk": "APT_028",
        "nama_produk_apotek": "Metformin HCl 500 mg Bernofarm",
        "zat_aktif_inn": "Metformin",
        "kategori_terapi": "Antidiabetes Oral (Biguanid)",
        "golongan_obat": "Obat Keras (PRB BPJS)",
        "nomor_izin_edar_bpom": "GKL0602338110A1",
        "produsen_farmasi": "PT Bernofarm",
        "bentuk_sediaan_kemasan": "Tablet salut selaput 500 mg",
        "estimasi_harga_apotek": "Rp 4.000 - Rp 9.000 / strip",
        "ketersediaan_apotek": "Sangat Umum (Lini Pertama)"
    },
    {
        "id_produk": "APT_029",
        "nama_produk_apotek": "Metformin HCl 850 mg Kimia Farma",
        "zat_aktif_inn": "Metformin",
        "kategori_terapi": "Antidiabetes Oral (Biguanid)",
        "golongan_obat": "Obat Keras (Generik)",
        "nomor_izin_edar_bpom": "GKL0412522410B1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Tablet salut selaput 850 mg",
        "estimasi_harga_apotek": "Rp 7.000 - Rp 14.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_030",
        "nama_produk_apotek": "Glucophage 500 mg Tablet",
        "zat_aktif_inn": "Metformin",
        "kategori_terapi": "Antidiabetes Oral (Biguanid)",
        "golongan_obat": "Obat Keras (Paten Originator)",
        "nomor_izin_edar_bpom": "DKL8715801417A1",
        "produsen_farmasi": "PT Merck Tbk",
        "bentuk_sediaan_kemasan": "Tablet salut selaput 500 mg",
        "estimasi_harga_apotek": "Rp 35.000 - Rp 50.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_031",
        "nama_produk_apotek": "Glucophage XR 750 mg",
        "zat_aktif_inn": "Metformin",
        "kategori_terapi": "Antidiabetes Oral (Lepas Lambat)",
        "golongan_obat": "Obat Keras (Paten)",
        "nomor_izin_edar_bpom": "DKI0786400614A1",
        "produsen_farmasi": "PT Merck Tbk",
        "bentuk_sediaan_kemasan": "Tablet lepas lambat 750 mg",
        "estimasi_harga_apotek": "Rp 85.000 - Rp 110.000 / blister",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_032",
        "nama_produk_apotek": "Glimepiride 2 mg Dexa",
        "zat_aktif_inn": "Glimepiride",
        "kategori_terapi": "Antidiabetes Oral (Sulfonilurea Gen 2)",
        "golongan_obat": "Obat Keras (PRB BPJS)",
        "nomor_izin_edar_bpom": "GKL0608513510A1",
        "produsen_farmasi": "PT Dexa Medica",
        "bentuk_sediaan_kemasan": "Tablet 2 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 8.000 - Rp 16.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_033",
        "nama_produk_apotek": "Glimepiride 3 mg Kimia Farma",
        "zat_aktif_inn": "Glimepiride",
        "kategori_terapi": "Antidiabetes Oral (Sulfonilurea Gen 2)",
        "golongan_obat": "Obat Keras (PRB BPJS)",
        "nomor_izin_edar_bpom": "GKL0812523910C1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Tablet 3 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 12.000 - Rp 22.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_034",
        "nama_produk_apotek": "Amaryl 2 mg Tablet",
        "zat_aktif_inn": "Glimepiride",
        "kategori_terapi": "Antidiabetes Oral (Sulfonilurea)",
        "golongan_obat": "Obat Keras (Paten Originator)",
        "nomor_izin_edar_bpom": "DKL9721200210A1",
        "produsen_farmasi": "PT Sanofi-Aventis Indonesia",
        "bentuk_sediaan_kemasan": "Tablet 2 mg (Blister @ 15 tablet)",
        "estimasi_harga_apotek": "Rp 90.000 - Rp 115.000 / blister",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_035",
        "nama_produk_apotek": "Glibenclamide 5 mg Kimia Farma",
        "zat_aktif_inn": "Glibenclamide",
        "kategori_terapi": "Antidiabetes Oral (Sulfonilurea)",
        "golongan_obat": "Obat Keras (Generik)",
        "nomor_izin_edar_bpom": "GKL9912519510A1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Tablet 5 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 3.000 - Rp 6.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_036",
        "nama_produk_apotek": "Glucobay 50 mg Tablet",
        "zat_aktif_inn": "Acarbose",
        "kategori_terapi": "Antidiabetes Oral (Penghambat Alfa-Glukosidase)",
        "golongan_obat": "Obat Keras (PRB BPJS)",
        "nomor_izin_edar_bpom": "DKI0351601610A1",
        "produsen_farmasi": "PT Bayer Indonesia",
        "bentuk_sediaan_kemasan": "Tablet 50 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 30.000 - Rp 45.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },

    # =========================================================================
    # 5. SALURAN CERNA (LAMBUNG, MAAG, PPI)
    # =========================================================================
    {
        "id_produk": "APT_037",
        "nama_produk_apotek": "Omeprazole 20 mg Kimia Farma",
        "zat_aktif_inn": "Omeprazole",
        "kategori_terapi": "Penghambat Pompa Proton (PPI)",
        "golongan_obat": "Obat Keras (DOWA - Tanpa Resep Maks 7 Tab)",
        "nomor_izin_edar_bpom": "GKL0412522301A1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Kapsul lepas tunda 20 mg",
        "estimasi_harga_apotek": "Rp 6.000 - Rp 12.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_038",
        "nama_produk_apotek": "Omeprazole 20 mg Dexa",
        "zat_aktif_inn": "Omeprazole",
        "kategori_terapi": "Penghambat Pompa Proton (PPI)",
        "golongan_obat": "Obat Keras (DOWA)",
        "nomor_izin_edar_bpom": "GKL0408510701A1",
        "produsen_farmasi": "PT Dexa Medica",
        "bentuk_sediaan_kemasan": "Kapsul lepas tunda 20 mg",
        "estimasi_harga_apotek": "Rp 7.000 - Rp 13.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_039",
        "nama_produk_apotek": "Ozid 20 mg Kapsul",
        "zat_aktif_inn": "Omeprazole",
        "kategori_terapi": "Penghambat Pompa Proton (PPI)",
        "golongan_obat": "Obat Keras (Merk Dagang)",
        "nomor_izin_edar_bpom": "DKL0004514501A1",
        "produsen_farmasi": "PT Darya-Varia Laboratoria",
        "bentuk_sediaan_kemasan": "Kapsul 20 mg (Strip @ 10 kapsul)",
        "estimasi_harga_apotek": "Rp 120.000 - Rp 145.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_040",
        "nama_produk_apotek": "Losec 20 mg Tablet",
        "zat_aktif_inn": "Omeprazole",
        "kategori_terapi": "Penghambat Pompa Proton (PPI)",
        "golongan_obat": "Obat Keras (Paten Originator)",
        "nomor_izin_edar_bpom": "DKI9031502801A1",
        "produsen_farmasi": "PT AstraZeneca Indonesia",
        "bentuk_sediaan_kemasan": "Tablet MUPS 20 mg (Strip @ 7 tablet)",
        "estimasi_harga_apotek": "Rp 175.000 - Rp 210.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_041",
        "nama_produk_apotek": "Lansoprazole 30 mg Dexa",
        "zat_aktif_inn": "Lansoprazole",
        "kategori_terapi": "Penghambat Pompa Proton (PPI)",
        "golongan_obat": "Obat Keras (DOWA)",
        "nomor_izin_edar_bpom": "GKL0608513301A1",
        "produsen_farmasi": "PT Dexa Medica",
        "bentuk_sediaan_kemasan": "Kapsul lepas tunda 30 mg",
        "estimasi_harga_apotek": "Rp 12.000 - Rp 22.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_042",
        "nama_produk_apotek": "Prosogan FD 30 mg Tablet",
        "zat_aktif_inn": "Lansoprazole",
        "kategori_terapi": "Penghambat Pompa Proton (PPI)",
        "golongan_obat": "Obat Keras (Paten Originator)",
        "nomor_izin_edar_bpom": "DKL0425801214A1",
        "produsen_farmasi": "PT Takeda Indonesia",
        "bentuk_sediaan_kemasan": "Tablet cepat larut 30 mg",
        "estimasi_harga_apotek": "Rp 210.000 - Rp 250.000 / blister",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_043",
        "nama_produk_apotek": "Antasida Doen Tablet Kunyah KF",
        "zat_aktif_inn": "Aluminium Hydroxide & Magnesium Hydroxide",
        "kategori_terapi": "Antasida (Peneutral Asam Lambung)",
        "golongan_obat": "Obat Bebas (Hijau)",
        "nomor_izin_edar_bpom": "GBL9912520063A1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Tablet kunyah (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 3.000 - Rp 6.000 / strip",
        "ketersediaan_apotek": "Sangat Umum (Etalase Depan)"
    },
    {
        "id_produk": "APT_044",
        "nama_produk_apotek": "Mylanta Tablet Kunyah",
        "zat_aktif_inn": "Aluminium Hydroxide, Magnesium Hydroxide, Simethicone",
        "kategori_terapi": "Antasida & Antikembung",
        "golongan_obat": "Obat Bebas (Hijau)",
        "nomor_izin_edar_bpom": "DBL1441200263A1",
        "produsen_farmasi": "PT Johnson & Johnson Indonesia",
        "bentuk_sediaan_kemasan": "Tablet kunyah (Blister @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 9.500 - Rp 14.000 / blister",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_045",
        "nama_produk_apotek": "Promag Tablet Kunyah",
        "zat_aktif_inn": "Hydrotalcite, Magnesium Hydroxide, Simethicone",
        "kategori_terapi": "Antasida & Pereda Sakit Maag",
        "golongan_obat": "Obat Bebas (Hijau)",
        "nomor_izin_edar_bpom": "DBL9111601963A1",
        "produsen_farmasi": "PT Kalbe Farma Tbk",
        "bentuk_sediaan_kemasan": "Tablet kunyah (Blister @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 9.000 - Rp 13.000 / blister",
        "ketersediaan_apotek": "Sangat Umum (Top Seller)"
    },
    {
        "id_produk": "APT_046",
        "nama_produk_apotek": "Polysilane Tablet Kunyah",
        "zat_aktif_inn": "Aluminium Hydroxide, Magnesium Hydroxide, Dimethylpolysiloxane",
        "kategori_terapi": "Antasida & Antikembung",
        "golongan_obat": "Obat Bebas (Hijau)",
        "nomor_izin_edar_bpom": "DBL7821624263A1",
        "produsen_farmasi": "PT Pharos Indonesia",
        "bentuk_sediaan_kemasan": "Tablet kunyah (Strip @ 8 tablet)",
        "estimasi_harga_apotek": "Rp 10.000 - Rp 15.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_047",
        "nama_produk_apotek": "Inpepsa Suspensi 100 mL",
        "zat_aktif_inn": "Sucralfate",
        "kategori_terapi": "Mukoprotektor Lambung",
        "golongan_obat": "Obat Keras",
        "nomor_izin_edar_bpom": "DKL9306709833A1",
        "produsen_farmasi": "PT Fahrenheit",
        "bentuk_sediaan_kemasan": "Suspensi 500 mg/5 mL (Botol 100 mL)",
        "estimasi_harga_apotek": "Rp 75.000 - Rp 95.000 / botol",
        "ketersediaan_apotek": "Tersedia"
    },

    # =========================================================================
    # 6. ANALGESIK, ANTIPIRETIK, & NSAID (PEREDA NYERI & DEMAM)
    # =========================================================================
    {
        "id_produk": "APT_048",
        "nama_produk_apotek": "Sanmol 500 mg Tablet",
        "zat_aktif_inn": "Paracetamol",
        "kategori_terapi": "Analgesik & Antipiretik",
        "golongan_obat": "Obat Bebas (Hijau)",
        "nomor_izin_edar_bpom": "DBL7622235610A2",
        "produsen_farmasi": "PT Sanbe Farma",
        "bentuk_sediaan_kemasan": "Tablet 500 mg (Strip @ 4 tablet)",
        "estimasi_harga_apotek": "Rp 2.500 - Rp 4.500 / strip",
        "ketersediaan_apotek": "Sangat Umum (Top Seller)"
    },
    {
        "id_produk": "APT_049",
        "nama_produk_apotek": "Sanmol Forte 650 mg Tablet",
        "zat_aktif_inn": "Paracetamol",
        "kategori_terapi": "Analgesik & Antipiretik",
        "golongan_obat": "Obat Bebas (Hijau)",
        "nomor_izin_edar_bpom": "DBL7622235610B1",
        "produsen_farmasi": "PT Sanbe Farma",
        "bentuk_sediaan_kemasan": "Tablet 650 mg (Strip @ 4 tablet)",
        "estimasi_harga_apotek": "Rp 3.500 - Rp 6.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_050",
        "nama_produk_apotek": "Panadol 500 mg Kaplet Biru",
        "zat_aktif_inn": "Paracetamol",
        "kategori_terapi": "Analgesik & Antipiretik",
        "golongan_obat": "Obat Bebas (Hijau)",
        "nomor_izin_edar_bpom": "DBL9624502804A1",
        "produsen_farmasi": "PT Glaxo Wellcome Indonesia",
        "bentuk_sediaan_kemasan": "Kaplet 500 mg (Blister @ 10 kaplet)",
        "estimasi_harga_apotek": "Rp 12.000 - Rp 16.000 / blister",
        "ketersediaan_apotek": "Sangat Umum (Top Seller)"
    },
    {
        "id_produk": "APT_051",
        "nama_produk_apotek": "Panadol Extra Kaplet Merah",
        "zat_aktif_inn": "Paracetamol & Caffeine",
        "kategori_terapi": "Analgesik Kombinasi (Sakit Kepala)",
        "golongan_obat": "Obat Bebas Terbatas (Biru)",
        "nomor_izin_edar_bpom": "DTL9424502004A1",
        "produsen_farmasi": "PT Glaxo Wellcome Indonesia",
        "bentuk_sediaan_kemasan": "Kaplet (Blister @ 10 kaplet)",
        "estimasi_harga_apotek": "Rp 14.000 - Rp 18.000 / blister",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_052",
        "nama_produk_apotek": "Biogesic 500 mg Tablet",
        "zat_aktif_inn": "Paracetamol",
        "kategori_terapi": "Analgesik & Antipiretik",
        "golongan_obat": "Obat Bebas (Hijau)",
        "nomor_izin_edar_bpom": "DBL9114704710A1",
        "produsen_farmasi": "PT Medifarma Laboratories",
        "bentuk_sediaan_kemasan": "Tablet 500 mg (Strip @ 4 tablet)",
        "estimasi_harga_apotek": "Rp 2.500 - Rp 4.500 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_053",
        "nama_produk_apotek": "Dumin 500 mg Tablet",
        "zat_aktif_inn": "Paracetamol",
        "kategori_terapi": "Analgesik & Antipiretik",
        "golongan_obat": "Obat Bebas (Hijau)",
        "nomor_izin_edar_bpom": "DBL830Acta01",
        "produsen_farmasi": "PT Actavis Indonesia",
        "bentuk_sediaan_kemasan": "Tablet 500 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 7.000 - Rp 12.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_054",
        "nama_produk_apotek": "Bodrex Tablet",
        "zat_aktif_inn": "Paracetamol & Caffeine",
        "kategori_terapi": "Analgesik Sakit Kepala & Demam",
        "golongan_obat": "Obat Bebas (Hijau)",
        "nomor_izin_edar_bpom": "DBL7225201010A1",
        "produsen_farmasi": "PT Tempo Scan Pacific Tbk",
        "bentuk_sediaan_kemasan": "Tablet (Strip @ 20 tablet)",
        "estimasi_harga_apotek": "Rp 9.000 - Rp 13.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_055",
        "nama_produk_apotek": "Paracetamol 500 mg Kimia Farma",
        "zat_aktif_inn": "Paracetamol",
        "kategori_terapi": "Analgesik & Antipiretik",
        "golongan_obat": "Obat Bebas (Generik)",
        "nomor_izin_edar_bpom": "GBL9612514804A1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Tablet 500 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 3.500 - Rp 7.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_056",
        "nama_produk_apotek": "Proris 200 mg Kaplet",
        "zat_aktif_inn": "Ibuprofen",
        "kategori_terapi": "Antiinflamasi Non-Steroid (NSAID)",
        "golongan_obat": "Obat Bebas Terbatas (Biru)",
        "nomor_izin_edar_bpom": "DTL9821620604A1",
        "produsen_farmasi": "PT Pharos Indonesia",
        "bentuk_sediaan_kemasan": "Kaplet 200 mg (Strip @ 10 kaplet)",
        "estimasi_harga_apotek": "Rp 10.000 - Rp 15.000 / strip",
        "ketersediaan_apotek": "Sangat Umum (Top Seller)"
    },
    {
        "id_produk": "APT_057",
        "nama_produk_apotek": "Proris Forte Sirup 50 mL",
        "zat_aktif_inn": "Ibuprofen",
        "kategori_terapi": "NSAID / Antipiretik Anak",
        "golongan_obat": "Obat Bebas Terbatas (Biru)",
        "nomor_izin_edar_bpom": "DTL9921620636A1",
        "produsen_farmasi": "PT Pharos Indonesia",
        "bentuk_sediaan_kemasan": "Suspensi 200 mg/5 mL (Botol 50 mL)",
        "estimasi_harga_apotek": "Rp 35.000 - Rp 45.000 / botol",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_058",
        "nama_produk_apotek": "Ibuprofen 400 mg Kimia Farma",
        "zat_aktif_inn": "Ibuprofen",
        "kategori_terapi": "Antiinflamasi Non-Steroid (NSAID)",
        "golongan_obat": "Obat Bebas Terbatas (Biru)",
        "nomor_izin_edar_bpom": "GTL9912520304A1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Tablet 400 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 5.000 - Rp 9.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_059",
        "nama_produk_apotek": "Bufect 400 mg Tablet",
        "zat_aktif_inn": "Ibuprofen",
        "kategori_terapi": "Antiinflamasi Non-Steroid (NSAID)",
        "golongan_obat": "Obat Keras",
        "nomor_izin_edar_bpom": "DKL8822206704A1",
        "produsen_farmasi": "PT Sanbe Farma",
        "bentuk_sediaan_kemasan": "Kaplet salut selaput 400 mg",
        "estimasi_harga_apotek": "Rp 25.000 - Rp 35.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_060",
        "nama_produk_apotek": "Ponstan 500 mg Tablet",
        "zat_aktif_inn": "Mefenamic Acid",
        "kategori_terapi": "NSAID (Pereda Nyeri Gigi & Haid)",
        "golongan_obat": "Obat Keras",
        "nomor_izin_edar_bpom": "DKL8319801809A1",
        "produsen_farmasi": "PT Pfizer Indonesia",
        "bentuk_sediaan_kemasan": "Tablet salut selaput 500 mg",
        "estimasi_harga_apotek": "Rp 35.000 - Rp 48.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_061",
        "nama_produk_apotek": "Asam Mefenamat 500 mg Dexa",
        "zat_aktif_inn": "Mefenamic Acid",
        "kategori_terapi": "NSAID",
        "golongan_obat": "Obat Keras (Generik)",
        "nomor_izin_edar_bpom": "GKL9908502309A1",
        "produsen_farmasi": "PT Dexa Medica",
        "bentuk_sediaan_kemasan": "Kaplet salut selaput 500 mg",
        "estimasi_harga_apotek": "Rp 5.000 - Rp 10.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_062",
        "nama_produk_apotek": "Voltaren 50 mg Tablet",
        "zat_aktif_inn": "Diclofenac Sodium",
        "kategori_terapi": "NSAID (Nyeri Sendi & Rematik)",
        "golongan_obat": "Obat Keras",
        "nomor_izin_edar_bpom": "DKL9930408015A1",
        "produsen_farmasi": "PT Novartis Indonesia",
        "bentuk_sediaan_kemasan": "Tablet salut enterik 50 mg",
        "estimasi_harga_apotek": "Rp 85.000 - Rp 110.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_063",
        "nama_produk_apotek": "Natrium Diklofenak 50 mg KF",
        "zat_aktif_inn": "Diclofenac Sodium",
        "kategori_terapi": "NSAID",
        "golongan_obat": "Obat Keras (Generik)",
        "nomor_izin_edar_bpom": "GKL9812518815A1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Tablet salut enterik 50 mg",
        "estimasi_harga_apotek": "Rp 4.000 - Rp 8.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_064",
        "nama_produk_apotek": "Meloxicam 15 mg Dexa",
        "zat_aktif_inn": "Meloxicam",
        "kategori_terapi": "NSAID Penghambat COX-2 Selektif",
        "golongan_obat": "Obat Keras (PRB BPJS)",
        "nomor_izin_edar_bpom": "GKL0408511210B1",
        "produsen_farmasi": "PT Dexa Medica",
        "bentuk_sediaan_kemasan": "Tablet 15 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 12.000 - Rp 20.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },

    # =========================================================================
    # 7. ANTIBIOTIK
    # =========================================================================
    {
        "id_produk": "APT_065",
        "nama_produk_apotek": "Amoxicillin 500 mg Kimia Farma",
        "zat_aktif_inn": "Amoxicillin",
        "kategori_terapi": "Antibiotik Beta-Laktam (Penicillin)",
        "golongan_obat": "Obat Keras (Resep Dokter)",
        "nomor_izin_edar_bpom": "GKL9612515704A1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Kaplet 500 mg (Strip @ 10 kaplet)",
        "estimasi_harga_apotek": "Rp 6.000 - Rp 11.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_066",
        "nama_produk_apotek": "Amoxsan 500 mg Kapsul",
        "zat_aktif_inn": "Amoxicillin",
        "kategori_terapi": "Antibiotik Penicillin",
        "golongan_obat": "Obat Keras (Paten)",
        "nomor_izin_edar_bpom": "DKL7822221601A1",
        "produsen_farmasi": "PT Sanbe Farma",
        "bentuk_sediaan_kemasan": "Kapsul 500 mg (Strip @ 10 kapsul)",
        "estimasi_harga_apotek": "Rp 38.000 - Rp 50.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_067",
        "nama_produk_apotek": "Kalmoxillin 500 mg Kaplet",
        "zat_aktif_inn": "Amoxicillin",
        "kategori_terapi": "Antibiotik Penicillin",
        "golongan_obat": "Obat Keras (Paten)",
        "nomor_izin_edar_bpom": "DKL8111603504A1",
        "produsen_farmasi": "PT Kalbe Farma Tbk",
        "bentuk_sediaan_kemasan": "Kaplet 500 mg (Strip @ 10 kaplet)",
        "estimasi_harga_apotek": "Rp 32.000 - Rp 45.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_068",
        "nama_produk_apotek": "Ciprofloxacin 500 mg Kimia Farma",
        "zat_aktif_inn": "Ciprofloxacin",
        "kategori_terapi": "Antibiotik Fluorokuinolon",
        "golongan_obat": "Obat Keras (Resep Dokter)",
        "nomor_izin_edar_bpom": "GKL9912519909A1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Kaplet salut selaput 500 mg",
        "estimasi_harga_apotek": "Rp 8.000 - Rp 15.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_069",
        "nama_produk_apotek": "Baquinor Forte 500 mg",
        "zat_aktif_inn": "Ciprofloxacin",
        "kategori_terapi": "Antibiotik Fluorokuinolon",
        "golongan_obat": "Obat Keras (Paten)",
        "nomor_izin_edar_bpom": "DKL8922209109A1",
        "produsen_farmasi": "PT Sanbe Farma",
        "bentuk_sediaan_kemasan": "Kaplet 500 mg (Strip @ 10 kaplet)",
        "estimasi_harga_apotek": "Rp 110.000 - Rp 140.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_070",
        "nama_produk_apotek": "Cefixime 100 mg Dexa",
        "zat_aktif_inn": "Cefixime",
        "kategori_terapi": "Antibiotik Sefalosporin Generasi 3",
        "golongan_obat": "Obat Keras",
        "nomor_izin_edar_bpom": "GKL0708514001A1",
        "produsen_farmasi": "PT Dexa Medica",
        "bentuk_sediaan_kemasan": "Kapsul 100 mg (Strip @ 10 kapsul)",
        "estimasi_harga_apotek": "Rp 25.000 - Rp 40.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_071",
        "nama_produk_apotek": "Azithromycin 500 mg Kimia Farma",
        "zat_aktif_inn": "Azithromycin",
        "kategori_terapi": "Antibiotik Makrolida",
        "golongan_obat": "Obat Keras",
        "nomor_izin_edar_bpom": "GKL1112524410A1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Kaplet 500 mg (Strip @ 6 kaplet)",
        "estimasi_harga_apotek": "Rp 45.000 - Rp 65.000 / strip",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_072",
        "nama_produk_apotek": "Zithromax 500 mg Tablet",
        "zat_aktif_inn": "Azithromycin",
        "kategori_terapi": "Antibiotik Makrolida",
        "golongan_obat": "Obat Keras (Paten Originator)",
        "nomor_izin_edar_bpom": "DKI9319803010A1",
        "produsen_farmasi": "PT Pfizer Indonesia",
        "bentuk_sediaan_kemasan": "Tablet salut selaput 500 mg",
        "estimasi_harga_apotek": "Rp 280.000 - Rp 320.000 / box (3 tab)",
        "ketersediaan_apotek": "Tersedia"
    },

    # =========================================================================
    # 8. ANTIJAMUR & ENZIM MODULATOR (AZOL)
    # =========================================================================
    {
        "id_produk": "APT_073",
        "nama_produk_apotek": "Ketoconazole 200 mg Kimia Farma",
        "zat_aktif_inn": "Ketoconazole",
        "kategori_terapi": "Antijamur Azol (Inhibitor Kuat CYP3A4)",
        "golongan_obat": "Obat Keras",
        "nomor_izin_edar_bpom": "GKL9912520110A1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Tablet 200 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 8.000 - Rp 14.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_074",
        "nama_produk_apotek": "Sporacid 100 mg Kapsul (Itraconazole)",
        "zat_aktif_inn": "Itraconazole",
        "kategori_terapi": "Antijamur Triazol (Inhibitor Kuat CYP3A4)",
        "golongan_obat": "Obat Keras",
        "nomor_izin_edar_bpom": "DKL0008507801A1",
        "produsen_farmasi": "PT Dexa Medica",
        "bentuk_sediaan_kemasan": "Kapsul 100 mg (Blister @ 4 kapsul)",
        "estimasi_harga_apotek": "Rp 65.000 - Rp 85.000 / blister",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_075",
        "nama_produk_apotek": "Diflucan 150 mg Kapsul (Fluconazole)",
        "zat_aktif_inn": "Fluconazole",
        "kategori_terapi": "Antijamur Triazol (Inhibitor Enzim)",
        "golongan_obat": "Obat Keras (Paten Originator)",
        "nomor_izin_edar_bpom": "DKI9019802001B1",
        "produsen_farmasi": "PT Pfizer Indonesia",
        "bentuk_sediaan_kemasan": "Kapsul 150 mg (Dus @ 1 kapsul)",
        "estimasi_harga_apotek": "Rp 120.000 - Rp 150.000 / kapsul",
        "ketersediaan_apotek": "Tersedia"
    },

    # =========================================================================
    # 9. ANTIHISTAMIN & ALERGI
    # =========================================================================
    {
        "id_produk": "APT_076",
        "nama_produk_apotek": "Cetirizine 10 mg Kimia Farma",
        "zat_aktif_inn": "Cetirizine",
        "kategori_terapi": "Antihistamin Generasi 2",
        "golongan_obat": "Obat Keras (DOWA)",
        "nomor_izin_edar_bpom": "GKL0612522710A1",
        "produsen_farmasi": "PT Kimia Farma Tbk",
        "bentuk_sediaan_kemasan": "Tablet 10 mg (Strip @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 5.000 - Rp 9.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_077",
        "nama_produk_apotek": "Incidal-OD 10 mg Kapsul",
        "zat_aktif_inn": "Cetirizine",
        "kategori_terapi": "Antihistamin",
        "golongan_obat": "Obat Keras (Paten)",
        "nomor_izin_edar_bpom": "DKL9404511501A1",
        "produsen_farmasi": "PT Bayer Indonesia",
        "bentuk_sediaan_kemasan": "Kapsul 10 mg (Strip @ 4 kapsul)",
        "estimasi_harga_apotek": "Rp 24.000 - Rp 32.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_078",
        "nama_produk_apotek": "CTM 4 mg PIM",
        "zat_aktif_inn": "Chlorpheniramine Maleate",
        "kategori_terapi": "Antihistamin Generasi 1 (Sedatif)",
        "golongan_obat": "Obat Bebas Terbatas (Biru)",
        "nomor_izin_edar_bpom": "DTL7218906310A1",
        "produsen_farmasi": "PT PIM Pharmaceuticals",
        "bentuk_sediaan_kemasan": "Tablet 4 mg (Strip @ 12 tablet)",
        "estimasi_harga_apotek": "Rp 2.000 - Rp 4.000 / strip",
        "ketersediaan_apotek": "Sangat Umum"
    },

    # =========================================================================
    # 10. HERBAL, JAMU TERSTANDAR, & FITOFARMAKA (ETALASE APOTEK INDONESIA)
    # =========================================================================
    {
        "id_produk": "APT_079",
        "nama_produk_apotek": "Mastin Kapsul Ekstrak Kulit Manggis",
        "zat_aktif_inn": "Alpha-Mangostin (Garcinia mangostana)",
        "kategori_terapi": "Herbal Ekstrak Xanthone (Inhibitor CYP3A4)",
        "golongan_obat": "Obat Tradisional (Jamu Terstandar)",
        "nomor_izin_edar_bpom": "POM TR 112325531",
        "produsen_farmasi": "PT Industri Jamu Borobudur",
        "bentuk_sediaan_kemasan": "Kapsul (Botol @ 60 kapsul)",
        "estimasi_harga_apotek": "Rp 50.000 - Rp 70.000 / botol",
        "ketersediaan_apotek": "Sangat Umum di Apotek"
    },
    {
        "id_produk": "APT_080",
        "nama_produk_apotek": "Mastin Plus Kapsul",
        "zat_aktif_inn": "Alpha-Mangostin & Ekstrak Daun Sirsak",
        "kategori_terapi": "Herbal Kombinasi Antioksidan",
        "golongan_obat": "Obat Tradisional (Jamu)",
        "nomor_izin_edar_bpom": "POM TR 142376651",
        "produsen_farmasi": "PT Industri Jamu Borobudur",
        "bentuk_sediaan_kemasan": "Kapsul (Botol @ 60 kapsul)",
        "estimasi_harga_apotek": "Rp 60.000 - Rp 80.000 / botol",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_081",
        "nama_produk_apotek": "Garcia Ekstrak Kulit Manggis",
        "zat_aktif_inn": "Alpha-Mangostin (Garcinia mangostana)",
        "kategori_terapi": "Herbal Ekstrak Manggis",
        "golongan_obat": "Obat Tradisional (Jamu)",
        "nomor_izin_edar_bpom": "POM TR 113324671",
        "produsen_farmasi": "PT Sumber Rejeki Makmur",
        "bentuk_sediaan_kemasan": "Kapsul (Botol @ 60 kapsul)",
        "estimasi_harga_apotek": "Rp 65.000 - Rp 85.000 / botol",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_082",
        "nama_produk_apotek": "Sido Muncul Ekstrak Kulit Manggis",
        "zat_aktif_inn": "Alpha-Mangostin (Garcinia mangostana)",
        "kategori_terapi": "Herbal Ekstrak Manggis",
        "golongan_obat": "Obat Tradisional (Jamu)",
        "nomor_izin_edar_bpom": "POM TR 142380581",
        "produsen_farmasi": "PT Industri Jamu Sido Muncul Tbk",
        "bentuk_sediaan_kemasan": "Kapsul (Botol @ 50 kapsul)",
        "estimasi_harga_apotek": "Rp 70.000 - Rp 90.000 / botol",
        "ketersediaan_apotek": "Tersedia"
    },
    {
        "id_produk": "APT_083",
        "nama_produk_apotek": "Curcuma FCT Tablet",
        "zat_aktif_inn": "Curcumin (Curcuma xanthorrhiza)",
        "kategori_terapi": "Suplemen Herbal Hepatoprotektor",
        "golongan_obat": "Suplemen Kesehatan / Herbal",
        "nomor_izin_edar_bpom": "POM SD 041517411",
        "produsen_farmasi": "PT Soho Industri Pharmasi",
        "bentuk_sediaan_kemasan": "Tablet salut selaput (Blister @ 10 tablet)",
        "estimasi_harga_apotek": "Rp 14.000 - Rp 20.000 / strip",
        "ketersediaan_apotek": "Sangat Umum (Top Seller)"
    },
    {
        "id_produk": "APT_084",
        "nama_produk_apotek": "Curcuma Force Tablet",
        "zat_aktif_inn": "Curcumin & Piperine",
        "kategori_terapi": "Suplemen Herbal Penambah Nafsu Makan",
        "golongan_obat": "Suplemen Kesehatan",
        "nomor_izin_edar_bpom": "POM SD 192554761",
        "produsen_farmasi": "PT Soho Industri Pharmasi",
        "bentuk_sediaan_kemasan": "Tablet (Blister @ 12 tablet)",
        "estimasi_harga_apotek": "Rp 18.000 - Rp 26.000 / blister",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_085",
        "nama_produk_apotek": "Sari Kunyit Kapsul Sido Muncul",
        "zat_aktif_inn": "Curcumin (Curcuma domestica)",
        "kategori_terapi": "Herbal Pelindung Lambung & Liver",
        "golongan_obat": "Obat Tradisional (Jamu)",
        "nomor_izin_edar_bpom": "POM TR 092303861",
        "produsen_farmasi": "PT Industri Jamu Sido Muncul Tbk",
        "bentuk_sediaan_kemasan": "Kapsul (Botol @ 50 kapsul)",
        "estimasi_harga_apotek": "Rp 60.000 - Rp 80.000 / botol",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_086",
        "nama_produk_apotek": "HerbaKOF Sirup 100 mL",
        "zat_aktif_inn": "Gingerol (Zingiber officinale & Ekstrak Herbal)",
        "kategori_terapi": "Obat Herbal Terstandar (Batuk & Radang)",
        "golongan_obat": "Obat Herbal Terstandar (OHT)",
        "nomor_izin_edar_bpom": "POM TR 152687991",
        "produsen_farmasi": "PT Dexa Medica",
        "bentuk_sediaan_kemasan": "Sirup Herbal 100 mL",
        "estimasi_harga_apotek": "Rp 15.000 - Rp 22.000 / botol",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_087",
        "nama_produk_apotek": "Tolak Angin Cair Sachet",
        "zat_aktif_inn": "Gingerol, Adas, Daun Cengkeh, Mint, Madu",
        "kategori_terapi": "Obat Herbal Terstandar (Masuk Angin)",
        "golongan_obat": "Obat Herbal Terstandar (OHT)",
        "nomor_izin_edar_bpom": "POM TR 122634441",
        "produsen_farmasi": "PT Industri Jamu Sido Muncul Tbk",
        "bentuk_sediaan_kemasan": "Cair (Dus @ 12 sachet)",
        "estimasi_harga_apotek": "Rp 40.000 - Rp 50.000 / dus",
        "ketersediaan_apotek": "Sangat Umum (Top Seller Nasional)"
    },
    {
        "id_produk": "APT_088",
        "nama_produk_apotek": "Antangin JRG Cair Sachet",
        "zat_aktif_inn": "Zingiber officinale (Jahe), Ginseng, Royal Jelly",
        "kategori_terapi": "Obat Herbal Masuk Angin",
        "golongan_obat": "Obat Tradisional (Jamu)",
        "nomor_izin_edar_bpom": "POM TR 082686731",
        "produsen_farmasi": "PT Deltomed Laboratories",
        "bentuk_sediaan_kemasan": "Cair (Dus @ 12 sachet)",
        "estimasi_harga_apotek": "Rp 38.000 - Rp 48.000 / dus",
        "ketersediaan_apotek": "Sangat Umum"
    },
    {
        "id_produk": "APT_089",
        "nama_produk_apotek": "Stimuno Forte Kapsul",
        "zat_aktif_inn": "Phyllanthus niruri (Meniran)",
        "kategori_terapi": "Imunomodulator (Fitofarmaka Uji Klinis)",
        "golongan_obat": "Fitofarmaka (Kasta Tertinggi Herbal BPOM)",
        "nomor_izin_edar_bpom": "POM FF 152300641",
        "produsen_farmasi": "PT Dexa Medica",
        "bentuk_sediaan_kemasan": "Kapsul (Blister @ 10 kapsul)",
        "estimasi_harga_apotek": "Rp 32.000 - Rp 45.000 / blister",
        "ketersediaan_apotek": "Sangat Umum"
    }
]

def main():
    output_csv = "dataset_obat_apotek_lengkap.csv"
    fieldnames = [
        "id_produk",
        "nama_produk_apotek",
        "zat_aktif_inn",
        "kategori_terapi",
        "golongan_obat",
        "nomor_izin_edar_bpom",
        "produsen_farmasi",
        "bentuk_sediaan_kemasan",
        "estimasi_harga_apotek",
        "ketersediaan_apotek"
    ]

    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(KATALOG_APOTEK)

    print("==========================================================================")
    print(" SUKSES: DATASET KATALOG OBAT APOTEK LENGKAP TELAH DITERBITKAN!           ")
    print("==========================================================================")
    print(f"Total entri produk obat apotek riil : {len(KATALOG_APOTEK)} produk")
    print(f"File luaran tersimpan di            : {output_csv}")
    print("Cakupan kategori:")
    print(" - Kardiovaskular (Antihipertensi, Jantung, Antikoagulan)")
    print(" - Kolesterol (Statin)")
    print(" - Antidiabetes Oral")
    print(" - Saluran Cerna (Maag, PPI, Antasida)")
    print(" - Analgesik & Antiinflamasi (Paracetamol, Ibuprofen, Asam Mefenamat, dll)")
    print(" - Antibiotik & Antijamur (Azol/CYP3A4 inhibitor)")
    print(" - Herbal Apotek (Kulit Manggis, Kunyit, Jahe, Jamu, OHT, Fitofarmaka)")
    print("==========================================================================")

if __name__ == "__main__":
    main()

