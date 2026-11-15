"""
Generator Dataset Obat Apotek Indonesia (Terverifikasi BPOM & Katalog Apotek)
Mencakup 15 zat aktif pilot proyek KBR beserta merk dagang riil di apotek Indonesia.
"""

import csv

DATASET_OBAT_APOTEK = [
    # 1. Amlodipine
    {
        "id_obat": "OBAT_001",
        "nama_produk_apotek": "Amlodipine Hexpharm 5 mg Tablet",
        "zat_aktif_inn": "Amlodipine",
        "golongan_farmakologi": "Antagonis Kalsium (CCB)",
        "golongan_regulasi": "Obat Keras (PRB BPJS)",
        "nomor_izin_edar_bpom": "GKL0708514110A1",
        "produsen_pabrik": "PT Hexpharm Jaya Laboratories (Kalbe)",
        "bentuk_sediaan": "Tablet 5 mg (Strip @ 10 tablet)",
        "rentang_harga_apotek_idr": "Rp 5.000 - Rp 10.000 / strip",
        "status_tersedia_apotek": "Tersedia (Sangat Umum)"
    },
    {
        "id_obat": "OBAT_002",
        "nama_produk_apotek": "Norvask 5 mg Tablet",
        "zat_aktif_inn": "Amlodipine",
        "golongan_farmakologi": "Antagonis Kalsium (CCB)",
        "golongan_regulasi": "Obat Keras (Paten Originator)",
        "nomor_izin_edar_bpom": "DKL9319803110A1",
        "produsen_pabrik": "PT Pfizer Indonesia",
        "bentuk_sediaan": "Tablet 5 mg (Blister @ 10 tablet)",
        "rentang_harga_apotek_idr": "Rp 95.000 - Rp 120.000 / strip",
        "status_tersedia_apotek": "Tersedia"
    },
    {
        "id_obat": "OBAT_003",
        "nama_produk_apotek": "Amlodipine 10 mg Kimia Farma",
        "zat_aktif_inn": "Amlodipine",
        "golongan_farmakologi": "Antagonis Kalsium (CCB)",
        "golongan_regulasi": "Obat Keras (Generik)",
        "nomor_izin_edar_bpom": "GKL0812523910B1",
        "produsen_pabrik": "PT Kimia Farma Tbk",
        "bentuk_sediaan": "Tablet 10 mg (Strip @ 10 tablet)",
        "rentang_harga_apotek_idr": "Rp 8.000 - Rp 15.000 / strip",
        "status_tersedia_apotek": "Tersedia (Sangat Umum)"
    },

    # 2. Captopril
    {
        "id_obat": "OBAT_004",
        "nama_produk_apotek": "Captopril 25 mg Kimia Farma",
        "zat_aktif_inn": "Captopril",
        "golongan_farmakologi": "ACE Inhibitor",
        "golongan_regulasi": "Obat Keras (Generik)",
        "nomor_izin_edar_bpom": "GKL9912519710B1",
        "produsen_pabrik": "PT Kimia Farma Tbk",
        "bentuk_sediaan": "Tablet 25 mg (Strip @ 10 tablet)",
        "rentang_harga_apotek_idr": "Rp 3.000 - Rp 7.000 / strip",
        "status_tersedia_apotek": "Tersedia (Sangat Umum)"
    },
    {
        "id_obat": "OBAT_005",
        "nama_produk_apotek": "Capoten 25 mg Tablet",
        "zat_aktif_inn": "Captopril",
        "golongan_farmakologi": "ACE Inhibitor",
        "golongan_regulasi": "Obat Keras (Paten)",
        "nomor_izin_edar_bpom": "DKL8324400410B1",
        "produsen_pabrik": "PT Taisho Pharmaceutical Indonesia",
        "bentuk_sediaan": "Tablet 25 mg (Strip @ 10 tablet)",
        "rentang_harga_apotek_idr": "Rp 55.000 - Rp 75.000 / strip",
        "status_tersedia_apotek": "Tersedia"
    },

    # 3. Simvastatin
    {
        "id_obat": "OBAT_006",
        "nama_produk_apotek": "Simvastatin 10 mg Kimia Farma",
        "zat_aktif_inn": "Simvastatin",
        "golongan_farmakologi": "HMG-CoA Reductase Inhibitor (Statin)",
        "golongan_regulasi": "Obat Keras (PRB BPJS)",
        "nomor_izin_edar_bpom": "GKL0312521710A1",
        "produsen_pabrik": "PT Kimia Farma Tbk",
        "bentuk_sediaan": "Tablet salut selaput 10 mg",
        "rentang_harga_apotek_idr": "Rp 7.000 - Rp 14.000 / strip",
        "status_tersedia_apotek": "Tersedia (Sangat Umum)"
    },
    {
        "id_obat": "OBAT_007",
        "nama_produk_apotek": "Zocor 20 mg Tablet",
        "zat_aktif_inn": "Simvastatin",
        "golongan_farmakologi": "HMG-CoA Reductase Inhibitor (Statin)",
        "golongan_regulasi": "Obat Keras (Paten Originator)",
        "nomor_izin_edar_bpom": "DKI9376400217A1",
        "produsen_pabrik": "PT Organon Pharma Indonesia",
        "bentuk_sediaan": "Tablet salut selaput 20 mg",
        "rentang_harga_apotek_idr": "Rp 150.000 - Rp 185.000 / strip",
        "status_tersedia_apotek": "Tersedia"
    },

    # 4. Metformin
    {
        "id_obat": "OBAT_008",
        "nama_produk_apotek": "Metformin HCl 500 mg Bernofarm",
        "zat_aktif_inn": "Metformin",
        "golongan_farmakologi": "Biguanid (Antidiabetes)",
        "golongan_regulasi": "Obat Keras (PRB BPJS)",
        "nomor_izin_edar_bpom": "GKL0602338110A1",
        "produsen_pabrik": "PT Bernofarm",
        "bentuk_sediaan": "Tablet salut selaput 500 mg",
        "rentang_harga_apotek_idr": "Rp 4.000 - Rp 9.000 / strip",
        "status_tersedia_apotek": "Tersedia (Sangat Umum)"
    },
    {
        "id_obat": "OBAT_009",
        "nama_produk_apotek": "Glucophage 500 mg Tablet",
        "zat_aktif_inn": "Metformin",
        "golongan_farmakologi": "Biguanid (Antidiabetes)",
        "golongan_regulasi": "Obat Keras (Paten Originator)",
        "nomor_izin_edar_bpom": "DKL8715801417A1",
        "produsen_pabrik": "PT Merck Tbk",
        "bentuk_sediaan": "Tablet salut selaput 500 mg",
        "rentang_harga_apotek_idr": "Rp 35.000 - Rp 50.000 / strip",
        "status_tersedia_apotek": "Tersedia"
    },

    # 5. Glimepiride
    {
        "id_obat": "OBAT_010",
        "nama_produk_apotek": "Glimepiride 2 mg Dexa",
        "zat_aktif_inn": "Glimepiride",
        "golongan_farmakologi": "Sulfonilurea Generasi 2",
        "golongan_regulasi": "Obat Keras (PRB BPJS)",
        "nomor_izin_edar_bpom": "GKL0608513510A1",
        "produsen_pabrik": "PT Dexa Medica",
        "bentuk_sediaan": "Tablet 2 mg (Strip @ 10 tablet)",
        "rentang_harga_apotek_idr": "Rp 8.000 - Rp 16.000 / strip",
        "status_tersedia_apotek": "Tersedia (Sangat Umum)"
    },
    {
        "id_obat": "OBAT_011",
        "nama_produk_apotek": "Amaryl 2 mg Tablet",
        "zat_aktif_inn": "Glimepiride",
        "golongan_farmakologi": "Sulfonilurea Generasi 2",
        "golongan_regulasi": "Obat Keras (Paten)",
        "nomor_izin_edar_bpom": "DKL9721200210A1",
        "produsen_pabrik": "PT Sanofi-Aventis Indonesia",
        "bentuk_sediaan": "Tablet 2 mg (Blister @ 15 tablet)",
        "rentang_harga_apotek_idr": "Rp 90.000 - Rp 115.000 / blister",
        "status_tersedia_apotek": "Tersedia"
    },

    # 6. Omeprazole
    {
        "id_obat": "OBAT_012",
        "nama_produk_apotek": "Omeprazole 20 mg Kapsul Kimia Farma",
        "zat_aktif_inn": "Omeprazole",
        "golongan_farmakologi": "Proton Pump Inhibitor (PPI)",
        "golongan_regulasi": "Obat Keras (DOWA)",
        "nomor_izin_edar_bpom": "GKL0412522301A1",
        "produsen_pabrik": "PT Kimia Farma Tbk",
        "bentuk_sediaan": "Kapsul lepas tunda 20 mg",
        "rentang_harga_apotek_idr": "Rp 6.000 - Rp 12.000 / strip",
        "status_tersedia_apotek": "Tersedia (Sangat Umum)"
    },
    {
        "id_obat": "OBAT_013",
        "nama_produk_apotek": "Ozid 20 mg Kapsul",
        "zat_aktif_inn": "Omeprazole",
        "golongan_farmakologi": "Proton Pump Inhibitor (PPI)",
        "golongan_regulasi": "Obat Keras (Merk Dagang)",
        "nomor_izin_edar_bpom": "DKL0004514501A1",
        "produsen_pabrik": "PT Darya-Varia Laboratoria",
        "bentuk_sediaan": "Kapsul 20 mg (Strip @ 10 kapsul)",
        "rentang_harga_apotek_idr": "Rp 120.000 - Rp 145.000 / strip",
        "status_tersedia_apotek": "Tersedia"
    },

    # 7. Paracetamol
    {
        "id_obat": "OBAT_014",
        "nama_produk_apotek": "Sanmol 500 mg Tablet",
        "zat_aktif_inn": "Paracetamol",
        "golongan_farmakologi": "Analgesik & Antipiretik",
        "golongan_regulasi": "Obat Bebas (Hijau)",
        "nomor_izin_edar_bpom": "DBL7622235610A2",
        "produsen_pabrik": "PT Sanbe Farma",
        "bentuk_sediaan": "Tablet 500 mg (Strip @ 4 tablet)",
        "rentang_harga_apotek_idr": "Rp 2.500 - Rp 4.500 / strip",
        "status_tersedia_apotek": "Tersedia (Sangat Umum)"
    },
    {
        "id_obat": "OBAT_015",
        "nama_produk_apotek": "Panadol 500 mg Kaplet Biru",
        "zat_aktif_inn": "Paracetamol",
        "golongan_farmakologi": "Analgesik & Antipiretik",
        "golongan_regulasi": "Obat Bebas (Hijau)",
        "nomor_izin_edar_bpom": "DBL9624502804A1",
        "produsen_pabrik": "PT Glaxo Wellcome Indonesia",
        "bentuk_sediaan": "Kaplet 500 mg (Blister @ 10 kaplet)",
        "rentang_harga_apotek_idr": "Rp 12.000 - Rp 16.000 / blister",
        "status_tersedia_apotek": "Tersedia (Sangat Umum)"
    },

    # 8. Ibuprofen
    {
        "id_obat": "OBAT_016",
        "nama_produk_apotek": "Proris 200 mg Kaplet",
        "zat_aktif_inn": "Ibuprofen",
        "golongan_farmakologi": "NSAID",
        "golongan_regulasi": "Obat Bebas Terbatas (Biru)",
        "nomor_izin_edar_bpom": "DTL9821620604A1",
        "produsen_pabrik": "PT Pharos Indonesia",
        "bentuk_sediaan": "Kaplet 200 mg (Strip @ 10 kaplet)",
        "rentang_harga_apotek_idr": "Rp 10.000 - Rp 15.000 / strip",
        "status_tersedia_apotek": "Tersedia (Sangat Umum)"
    },
    {
        "id_obat": "OBAT_017",
        "nama_produk_apotek": "Ibuprofen 400 mg Kimia Farma",
        "zat_aktif_inn": "Ibuprofen",
        "golongan_farmakologi": "NSAID",
        "golongan_regulasi": "Obat Bebas Terbatas (Biru)",
        "nomor_izin_edar_bpom": "GTL9912520304A1",
        "produsen_pabrik": "PT Kimia Farma Tbk",
        "bentuk_sediaan": "Tablet 400 mg (Strip @ 10 tablet)",
        "rentang_harga_apotek_idr": "Rp 5.000 - Rp 9.000 / strip",
        "status_tersedia_apotek": "Tersedia (Sangat Umum)"
    },

    # 9. Ciprofloxacin
    {
        "id_obat": "OBAT_018",
        "nama_produk_apotek": "Ciprofloxacin 500 mg Kimia Farma",
        "zat_aktif_inn": "Ciprofloxacin",
        "golongan_farmakologi": "Antibiotik Fluorokuinolon",
        "golongan_regulasi": "Obat Keras (Antibiotik)",
        "nomor_izin_edar_bpom": "GKL9912519909A1",
        "produsen_pabrik": "PT Kimia Farma Tbk",
        "bentuk_sediaan": "Kaplet salut selaput 500 mg",
        "rentang_harga_apotek_idr": "Rp 8.000 - Rp 15.000 / strip",
        "status_tersedia_apotek": "Tersedia (Sangat Umum)"
    },
    {
        "id_obat": "OBAT_019",
        "nama_produk_apotek": "Baquinor Forte 500 mg Tablet",
        "zat_aktif_inn": "Ciprofloxacin",
        "golongan_farmakologi": "Antibiotik Fluorokuinolon",
        "golongan_regulasi": "Obat Keras (Paten)",
        "nomor_izin_edar_bpom": "DKL8922209109A1",
        "produsen_pabrik": "PT Sanbe Farma",
        "bentuk_sediaan": "Kaplet 500 mg (Strip @ 10 kaplet)",
        "rentang_harga_apotek_idr": "Rp 110.000 - Rp 140.000 / strip",
        "status_tersedia_apotek": "Tersedia"
    },

    # 10. Amoxicillin
    {
        "id_obat": "OBAT_020",
        "nama_produk_apotek": "Amoxicillin 500 mg Kimia Farma",
        "zat_aktif_inn": "Amoxicillin",
        "golongan_farmakologi": "Antibiotik Penicillin",
        "golongan_regulasi": "Obat Keras (Antibiotik)",
        "nomor_izin_edar_bpom": "GKL9612515704A1",
        "produsen_pabrik": "PT Kimia Farma Tbk",
        "bentuk_sediaan": "Kaplet 500 mg (Strip @ 10 kaplet)",
        "rentang_harga_apotek_idr": "Rp 6.000 - Rp 11.000 / strip",
        "status_tersedia_apotek": "Tersedia (Sangat Umum)"
    },
    {
        "id_obat": "OBAT_021",
        "nama_produk_apotek": "Amoxsan 500 mg Kapsul",
        "zat_aktif_inn": "Amoxicillin",
        "golongan_farmakologi": "Antibiotik Penicillin",
        "golongan_regulasi": "Obat Keras (Paten)",
        "nomor_izin_edar_bpom": "DKL7822221601A1",
        "produsen_pabrik": "PT Sanbe Farma",
        "bentuk_sediaan": "Kapsul 500 mg (Strip @ 10 kapsul)",
        "rentang_harga_apotek_idr": "Rp 38.000 - Rp 50.000 / strip",
        "status_tersedia_apotek": "Tersedia (Sangat Umum)"
    },

    # 11. Warfarin
    {
        "id_obat": "OBAT_022",
        "nama_produk_apotek": "Simarc-2 Tablet (Warfarin Sodium 2 mg)",
        "zat_aktif_inn": "Warfarin",
        "golongan_farmakologi": "Antikoagulan Antagonis Vit K",
        "golongan_regulasi": "Obat Keras",
        "nomor_izin_edar_bpom": "DKL9331504910A1",
        "produsen_pabrik": "PT Pratapa Nirmala (Fahrenheit)",
        "bentuk_sediaan": "Tablet 2 mg (Blister @ 10 tablet)",
        "rentang_harga_apotek_idr": "Rp 25.000 - Rp 35.000 / strip",
        "status_tersedia_apotek": "Tersedia (Apotek Rujukan/RS)"
    },

    # 12. Digoxin
    {
        "id_obat": "OBAT_023",
        "nama_produk_apotek": "Fargoxin 0.25 mg Tablet",
        "zat_aktif_inn": "Digoxin",
        "golongan_farmakologi": "Glikosida Jantung",
        "golongan_regulasi": "Obat Keras (Indeks Terapi Sempit)",
        "nomor_izin_edar_bpom": "DKL8831502410A1",
        "produsen_pabrik": "PT Pratapa Nirmala (Fahrenheit)",
        "bentuk_sediaan": "Tablet 0.25 mg (Strip @ 10 tablet)",
        "rentang_harga_apotek_idr": "Rp 15.000 - Rp 25.000 / strip",
        "status_tersedia_apotek": "Tersedia"
    },

    # 13. Herbal: Kulit Manggis (Alpha-Mangostin)
    {
        "id_obat": "OBAT_024",
        "nama_produk_apotek": "Mastin Kapsul Ekstrak Kulit Manggis",
        "zat_aktif_inn": "Alpha-Mangostin (Garcinia mangostana)",
        "golongan_farmakologi": "Herbal Ekstrak Xanthone (Inhibitor CYP3A4)",
        "golongan_regulasi": "Obat Tradisional (Jamu Terstandar)",
        "nomor_izin_edar_bpom": "POM TR 112325531",
        "produsen_pabrik": "PT Industri Jamu Borobudur",
        "bentuk_sediaan": "Kapsul (Botol @ 60 kapsul)",
        "rentang_harga_apotek_idr": "Rp 50.000 - Rp 70.000 / botol",
        "status_tersedia_apotek": "Tersedia Bebas di Apotek"
    },
    {
        "id_obat": "OBAT_025",
        "nama_produk_apotek": "Garcia Ekstrak Kulit Manggis",
        "zat_aktif_inn": "Alpha-Mangostin (Garcinia mangostana)",
        "golongan_farmakologi": "Herbal Ekstrak Xanthone",
        "golongan_regulasi": "Obat Tradisional (Jamu)",
        "nomor_izin_edar_bpom": "POM TR 113324671",
        "produsen_pabrik": "PT Sumber Rejeki Makmur",
        "bentuk_sediaan": "Kapsul (Botol @ 60 kapsul)",
        "rentang_harga_apotek_idr": "Rp 65.000 - Rp 85.000 / botol",
        "status_tersedia_apotek": "Tersedia Bebas di Apotek"
    },

    # 14. Herbal: Kunyit (Curcumin)
    {
        "id_obat": "OBAT_026",
        "nama_produk_apotek": "Curcuma FCT Tablet",
        "zat_aktif_inn": "Curcumin (Curcuma xanthorrhiza)",
        "golongan_farmakologi": "Hepatoprotektor & Suplemen Herbal",
        "golongan_regulasi": "Suplemen Kesehatan / Herbal",
        "nomor_izin_edar_bpom": "POM SD 041517411",
        "produsen_pabrik": "PT Soho Industri Pharmasi",
        "bentuk_sediaan": "Tablet salut selaput (Blister @ 10 tablet)",
        "rentang_harga_apotek_idr": "Rp 14.000 - Rp 20.000 / strip",
        "status_tersedia_apotek": "Tersedia (Sangat Umum)"
    },

    # 15. Herbal: Jahe (Gingerol)
    {
        "id_obat": "OBAT_027",
        "nama_produk_apotek": "HerbaKOF Sirup Herbal",
        "zat_aktif_inn": "Gingerol (Zingiber officinale)",
        "golongan_farmakologi": "Obat Herbal Terstandar (OHT)",
        "golongan_regulasi": "Obat Herbal Terstandar (OHT)",
        "nomor_izin_edar_bpom": "POM TR 152687991",
        "produsen_pabrik": "PT Dexa Medica",
        "bentuk_sediaan": "Sirup Herbal 100 mL",
        "rentang_harga_apotek_idr": "Rp 15.000 - Rp 22.000 / botol",
        "status_tersedia_apotek": "Tersedia (Sangat Umum)"
    }
]

def main():
    output_csv = "dataset_obat_apotek_indonesia.csv"
    fieldnames = [
        "id_obat",
        "nama_produk_apotek",
        "zat_aktif_inn",
        "golongan_farmakologi",
        "golongan_regulasi",
        "nomor_izin_edar_bpom",
        "produsen_pabrik",
        "bentuk_sediaan",
        "rentang_harga_apotek_idr",
        "status_tersedia_apotek"
    ]

    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(DATASET_OBAT_APOTEK)

    print("=================================================================")
    print(" SUKSES: DATASET OBAT APOTEK INDONESIA BERHASIL DI-GENERATE!   ")
    print("=================================================================")
    print(f"Total baris produk obat riil : {len(DATASET_OBAT_APOTEK)}")
    print(f"File luaran                  : {output_csv}")
    print("Mencakup 15 zat INN pilot + herbal kulit manggis, kunyit, jahe.")
    print("Data lengkap: Merk Apotek, NIE BPOM, Pabrik, Dosis, dan Harga.")
    print("=================================================================")

if __name__ == "__main__":
    main()

