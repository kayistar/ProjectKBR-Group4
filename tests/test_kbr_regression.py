"""
test_kbr_regression.py
======================
Uji regresi formal sesuai docs/RENCANA_KERJA.md Bagian 5 & 8:
  - 5 skenario T1 (batuk kering dewasa; batuk berdahak anak 4 th; hipertensi + PSE; hamil; demam 5 hari)
  - 10 kelompok uji T2 (alternatif lebih murah dengan kandungan identik & satuan sebanding)
  - 3 keranjang uji T3 (dobel paracetamol; Komix + Actifed; Actifed + Digoxin) + uji negatif Unknown != aman
  - 3 skenario substitusi T4 (hipertensi + PSE; BPH + CTM; tukak lambung + Ibuprofen)
  - 5 kartu edukasi T5 (Actifed, Komix, Sanmol, OB Combi, Siladex)
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scrape"))

from kbr_engine import KBRKnowledgeEngine


def test_t1_five_scenarios():
    eng = KBRKnowledgeEngine()

    # 1. Batuk kering dewasa
    r1 = eng.recommend_t1(["SYMP:0000025"], durasi_hari=2, umur_tahun=28)
    assert len(r1["rekomendasi_produk"]) >= 1
    assert r1["rekomendasi_produk"][0]["aturan_pakai_per_zat"]

    # 2. Batuk berdahak anak 4 tahun (hanya produk aman usia <=4 & sediaan anak)
    r2 = eng.recommend_t1(["SYMP:0020027"], durasi_hari=2, umur_tahun=4)
    assert len(r2["rekomendasi_produk"]) >= 1
    for item in r2["rekomendasi_produk"]:
        assert any(k in item["nama"].lower() for k in ("anak", "child", "kids", "sirup", "syrup", "syr", "drop"))

    # 3. Hipertensi tidak terkontrol + hidung tersumbat -> produk PSE/PE harus terblokir!
    r3 = eng.recommend_t1(["SYMP:0000869"], durasi_hari=2, umur_tahun=50, kondisi=["hipertensi_tidak_terkontrol"])
    assert r3["triase"] == "TanyaApoteker"
    for item in r3["rekomendasi_produk"]:
        assert "pseudo" not in item["komposisi"].lower()

    # 4. Ibu hamil -> triase minimal TanyaApoteker, bukan Pantau
    r4 = eng.recommend_t1(["SYMP:0000613"], durasi_hari=1, umur_tahun=27, kondisi=["hamil"])
    assert r4["triase"] in ("TanyaApoteker", "SegeraKeDokter")

    # 5. Demam 5 hari (> batas 3 hari) -> SegeraKeDokter & tidak merekomendasikan produk OTC!
    r5 = eng.recommend_t1(["SYMP:0000613"], durasi_hari=5, umur_tahun=30)
    assert r5["triase"] == "SegeraKeDokter"
    assert len(r5["rekomendasi_produk"]) == 0


def test_t2_cheaper_alternatives():
    eng = KBRKnowledgeEngine()
    # Cari kelompok zat dengan >= 2 produk valid berharga & satuan sama
    from collections import defaultdict
    groups = defaultdict(list)
    for p in eng.products.values():
        if p["status_harga"] == "ok" and p["harga_per_unit"] is not None:
            groups[(p["zids"], p["satuan_unit"])].append(p)

    # Ambil kelompok yang punya variasi harga (>1 harga berbeda)
    valid_groups = []
    for key, plist in groups.items():
        plist.sort(key=lambda x: x["harga_per_unit"])
        if len(plist) >= 2 and plist[-1]["harga_per_unit"] > plist[0]["harga_per_unit"]:
            valid_groups.append((key, plist))

    assert len(valid_groups) >= 10, f"Hanya ditemukan {len(valid_groups)} kelompok T2"
    for _, plist in valid_groups[:10]:
        most_exp = plist[-1]
        res = eng.cheaper_alternatives_t2(most_exp["slug"])
        assert len(res["alternatif_lebih_murah"]) >= 1
        assert res["alternatif_lebih_murah"][0]["harga_per_unit"] < most_exp["harga_per_unit"]


def test_t3_cart_screening_and_negative_unknown():
    eng = KBRKnowledgeEngine()

    # 1. 2 merek ber-paracetamol -> deteksi DuplikasiKandungan Paracetamol
    c1 = eng.screen_cart_t3(["PROCOLD-FLU&BATUK-CAPL-6S-STRIP-24S-2072", "SANMOL-F-650MG-TAB-4S-STRIP-25S-17789"])
    assert any(m["jenis"] == "DuplikasiKandungan" and "Paracetamol" in m["detail"] for m in c1["masalah"])

    # 2. Komix + Actifed -> deteksi dobel DXM + dobel kelas ATC R06A / interaksi
    c2 = eng.screen_cart_t3(["KOMIX-JERUK-NIPIS-7ML-SACH-30S-8909", "ACTIFED-PLUS-COUGH-SUPPRESS-SYR-MERAH-60ML-275"])
    assert any(m["jenis"] == "DuplikasiKandungan" and "Dextromethorphan" in m["detail"] for m in c2["masalah"])

    # 3. Actifed + Digoxin rutin -> deteksi InteraksiModerate PSE + Digoxin
    c3 = eng.screen_cart_t3(["ACTIFED-PLUS-COUGH-SUPPRESS-SYR-MERAH-60ML-275"], obat_rutin=["Digoxin"])
    assert any("Pseudoephedrine" in m.get("pasangan", "") and "Digoxin" in m.get("pasangan", "") for m in c3["masalah"])

    # 4. Uji Negatif: pasangan yang belum ada datanya TIDAK BOLEH menghasilkan kata "aman"
    unk = eng.check_pair_interaction("ZAT-011", "ZAT-016")  # Guaifenesin + Metformin
    assert unk["status"] in ("tidak_diketahui", "unknown_perlu_tanya_apoteker")
    assert unk["tindak_lanjut"] == "TanyaApoteker"
    assert "aman" not in unk["rekomendasi"].lower()


def test_t4_safe_substitution():
    eng = KBRKnowledgeEngine()

    # 1. Hipertensi + produk PSE (Actifed Merah)
    s1 = eng.safe_substitution_t4("ACTIFED-PLUS-COUGH-SUPPRESS-SYR-MERAH-60ML-275", "hipertensi_tidak_terkontrol")
    assert s1["alasan_penolakan"]
    assert len(s1["alternatif_aman"]) >= 1

    # 2. BPH + produk CTM (Komix)
    s2 = eng.safe_substitution_t4("KOMIX-JERUK-NIPIS-7ML-SACH-30S-8909", "pembesaran_prostat_bph")
    assert s2["alasan_penolakan"]
    assert len(s2["alternatif_aman"]) >= 1

    # 3. Tukak lambung + Ibuprofen
    ibu_prod = next((p["slug"] for p in eng.products.values() if "ZAT-002" in p["zids"]), None)
    assert ibu_prod is not None
    s3 = eng.safe_substitution_t4(ibu_prod, "tukak_lambung_gerd")
    assert s3["alasan_penolakan"]
    assert len(s3["alternatif_aman"]) >= 1


def test_t5_five_education_cards():
    eng = KBRKnowledgeEngine()
    slugs = [
        "ACTIFED-PLUS-COUGH-SUPPRESS-SYR-MERAH-60ML-275",
        "KOMIX-JERUK-NIPIS-7ML-SACH-30S-8909",
        "SANMOL-F-650MG-TAB-4S-STRIP-25S-17789",
        "OB-COMBI-ATT-MENTHOL-SYR-60ML-34066",
        "SILADEX-COUGH-N-COLD-SYR-100ML-9753",
    ]
    for s in slugs:
        card = eng.generate_education_card_t5(s)
        assert "Cara Pakai" in card
        assert "Sumber:" in card
        assert "Disclaimer" in card


if __name__ == "__main__":
    test_t1_five_scenarios()
    print("[PASS] T1: 5 skenario rekomendasi personal")
    test_t2_cheaper_alternatives()
    print("[PASS] T2: 10 kelompok alternatif lebih murah")
    test_t3_cart_screening_and_negative_unknown()
    print("[PASS] T3: 3 keranjang uji + uji negatif Unknown != aman")
    test_t4_safe_substitution()
    print("[PASS] T4: 3 skenario substitusi aman")
    test_t5_five_education_cards()
    print("[PASS] T5: 5 kartu edukasi & explainability")
    print("=== SEMUA UJI REGRESI LULUS 100% ===")
