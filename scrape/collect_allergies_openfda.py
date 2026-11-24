"""
collect_allergies_openfda.py
============================
Mengambil bukti kontraindikasi hipersensitivitas / alergi dan alergi silang
dari OpenFDA Drug Label API (https://api.fda.gov/drug/label.json) untuk
31 zat aktif di data/curation/sheet1_zat_aktif.csv.

Output:
  1. data/curation/openfda_allergy_raw.json   (jejak respons & kutipan asli FDA)
  2. data/curation/substansi_alergi.csv       (tabel kurasi siap pakai KB)
"""

import csv
import datetime
import json
import os
import re
import time
import urllib.parse
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEET1_PATH = os.path.join(ROOT, "data", "curation", "sheet1_zat_aktif.csv")
OUT_RAW_JSON = os.path.join(ROOT, "data", "curation", "openfda_allergy_raw.json")
OUT_CSV = os.path.join(ROOT, "data", "curation", "substansi_alergi.csv")

TODAY = datetime.date.today().isoformat()

# Nama generik standar USAN untuk kueri OpenFDA
FDA_SEARCH_NAME = {
    "ZAT-001": "acetaminophen",
    "ZAT-002": "ibuprofen",
    "ZAT-003": "dextromethorphan",
    "ZAT-004": "pseudoephedrine",
    "ZAT-005": "phenylephrine",
    "ZAT-006": "chlorpheniramine",
    "ZAT-007": "diphenhydramine",
    "ZAT-008": "cetirizine",
    "ZAT-009": "bromhexine",
    "ZAT-010": "ambroxol",
    "ZAT-011": "guaifenesin",
    "ZAT-012": "simvastatin",
    "ZAT-013": "atorvastatin",
    "ZAT-014": "amlodipine",
    "ZAT-015": "captopril",
    "ZAT-016": "metformin",
    "ZAT-017": "glimepiride",
    "ZAT-018": "warfarin",
    "ZAT-019": "clopidogrel",
    "ZAT-020": "digoxin",
    "ZAT-021": "omeprazole",
    "ZAT-022": "ciprofloxacin",
    "ZAT-023": "amoxicillin",
    "ZAT-024": "itraconazole",
    "ZAT-025": "ketoconazole",
    "ZAT-026": "fluconazole",
    "ZAT-027": None,  # Herbal: Alpha-Mangostin
    "ZAT-028": None,  # Herbal: Curcumin
    "ZAT-029": None,  # Herbal: Gingerol
    "ZAT-030": "triprolidine",
    "ZAT-031": "doxylamine",
}

# Metadata klinis alergen & cross-reactivity terkurasi (farmakologi + ATC)
ALLERGY_PROFILE = {
    "ZAT-001": ("Anilide / Paracetamol", "Alergi Paracetamol / Acetaminophen", "Tidak ada alergi silang kelas NSAID (aman bagi sebagian besar pasien alergi aspirin/NSAID dengan pengawasan)", "Ruam kulit, biduran (urtikaria), pembengkakan wajah, reaksi kulit serius (SJS/TEN jarang)", "SegeraKeDokter"),
    "ZAT-002": ("NSAID (Turunan Asam Propionat)", "Alergi Ibuprofen", "Aspirin; Naproxen; Diclofenac; Asam Mefenamat; Celecoxib / NSAID lain (risiko asma-terinduksi-aspirin)", "Urtikaria, angioedema (bengkak bibir/kelopak mata), bronkospasme / sesak napas, anafilaksis", "SegeraKeDokter"),
    "ZAT-003": ("Antitusif Derivat Morfinan", "Alergi Dextromethorphan", "Jarang alergi silang dengan opioid; hati-hati bila hipersensitif komponen sirup", "Ruam, gatal, urtikaria, angioedema", "TanyaApoteker"),
    "ZAT-004": ("Dekongestan Simpatomimetik", "Alergi Pseudoephedrine", "Efedrin / Fenilefrin / Fenilpropanolamin (amina simpatomimetik)", "Ruam alergi, gatal, bengkak wajah", "TanyaApoteker"),
    "ZAT-005": ("Dekongestan Agonis Alfa-1", "Alergi Phenylephrine", "Pseudoefedrin / amina simpatomimetik lain; sulfit pada beberapa sediaan", "Ruam, urtikaria, dermatitis kontak (sediaan topikal)", "TanyaApoteker"),
    "ZAT-006": ("Antihistamin H1 Alkilamin", "Alergi Chlorpheniramine (CTM)", "Dexchlorpheniramine; Brompheniramine; antihistamin H1 etilendiamin/alkilamin sejenis", "Ruam kulit, fotosensitivitas, urtikaria", "TanyaApoteker"),
    "ZAT-007": ("Antihistamin H1 Etanolamin", "Alergi Diphenhydramine", "Dimenhydrinate; Doxylamine; Carbinoxamine (sesama kelas etanolamin)", "Ruam, urtikaria, syok anafilaksis jarang", "TanyaApoteker"),
    "ZAT-008": ("Antihistamin H1 Piperazin (Gen-2)", "Alergi Cetirizine", "Hydroxyzine; Levocetirizine (turunan piperazin)", "Angioedema, urtikaria, pruritus, sesak napas (jarang)", "SegeraKeDokter"),
    "ZAT-009": ("Mukolitik Benzilamina", "Alergi Bromhexine", "Ambroxol (metabolit aktif bromhexine — alergi silang langsung!)", "Ruam kulit, urtikaria, bronkospasme, reaksi kulit berat (EM/SJS sangat jarang)", "SegeraKeDokter"),
    "ZAT-010": ("Mukolitik (Metabolit Bromhexine)", "Alergi Ambroxol", "Bromhexine (prekursor ambroxol — alergi silang langsung!)", "Ruam, urtikaria, angioedema, reaksi mukokutan berat (SJS jarang)", "SegeraKeDokter"),
    "ZAT-011": ("Ekspektoran Derivat Guaiakol", "Alergi Guaifenesin", "Tidak ada alergi silang spesifik mayor", "Ruam kulit, gatal (jarang)", "TanyaApoteker"),
    "ZAT-012": ("Statin (Inhibitor HMG-CoA Reduktase)", "Alergi Simvastatin", "Atorvastatin; Pravastatin; Rosuvastatin (kelas statin)", "Ruam, angioedema, sindrom hipersensitivitas (lupus-like/anafilaksis jarang)", "SegeraKeDokter"),
    "ZAT-013": ("Statin (Inhibitor HMG-CoA Reduktase)", "Alergi Atorvastatin", "Simvastatin; Rosuvastatin; Fluvastatin (kelas statin)", "Ruam, urtikaria, angioedema, reaksi hipersensitivitas sistemik", "SegeraKeDokter"),
    "ZAT-014": ("Antagonis Kalsium Dihidropiridin", "Alergi Amlodipine", "Nifedipine; Nicardipine (sesama dihidropiridin)", "Ruam makulopapular, angioedema, pruritus", "SegeraKeDokter"),
    "ZAT-015": ("ACE Inhibitor", "Alergi / Angioedema Captopril", "Enalapril; Lisinopril; Ramipril (seluruh kelas ACE inhibitor — riwayat angioedema kontraindikasi mutlak)", "Angioedema wajah/lidah/tenggorokan (mengancam napas!), ruam, batuk kering", "SegeraKeDokter"),
    "ZAT-016": ("Biguanid Antidiabetes", "Alergi Metformin", "Tidak ada alergi silang kelas spesifik", "Ruam kulit, urtikaria (jarang)", "TanyaApoteker"),
    "ZAT-017": ("Sulfonilurea Antidiabetes", "Alergi Glimepiride", "Glibenclamide; Gliclazide; Sulfonamida / obat sulfa (peringatan silang pada alergi sulfa berat)", "Ruam alergi, urtikaria, fotosensitivitas, trombositopenia alergi", "SegeraKeDokter"),
    "ZAT-018": ("Antikoagulan Antagonis Vitamin K", "Alergi Warfarin", "Acenocoumarol; derivat kumarin lain", "Ruam kulit, urtikaria, nekrosis kulit terkait warfarin (jarang)", "SegeraKeDokter"),
    "ZAT-019": ("Antiplatelet Tienopiridin", "Alergi Clopidogrel", "Prasugrel; Ticlopidine (sesama golongan tienopiridin)", "Ruam kulit, urtikaria, angioedema, reaksi hematologi hipersensitivitas", "SegeraKeDokter"),
    "ZAT-020": ("Glikosida Jantung", "Alergi Digoxin", "Digitoxin / glikosida digitalis lain", "Ruam kulit, urtikaria, eosinofilia (sangat jarang)", "SegeraKeDokter"),
    "ZAT-021": ("Proton Pump Inhibitor (PPI)", "Alergi Omeprazole", "Esomeprazole; Lansoprazole; Pantoprazole (kelas PPI benzimidazol)", "Ruam, angioedema, bronkospasme, nefritis interstisial akut, reaksi kulit berat", "SegeraKeDokter"),
    "ZAT-022": ("Antibiotik Fluorokuinolon", "Alergi Ciprofloxacin", "Levofloxacin; Ofloxacin; Moxifloxacin (seluruh kelas kuinolon)", "Urtikaria, angioedema, sesak napas, syok anafilaksis, fotosensitivitas", "SegeraKeDokter"),
    "ZAT-023": ("Antibiotik Beta-Laktam Penisilin", "Alergi Amoxicillin", "Penisilin; Ampicillin; Co-amoxiclav; hati-hati silang dengan Sefalosporin (Cefadroxil/Cefixime)", "Biduran akut, sesak napas, bengkak laring/wajah, syok anafilaksis", "SegeraKeDokter"),
    "ZAT-024": ("Antijamur Triazol", "Alergi Itraconazole", "Fluconazole; Voriconazole; Ketoconazole (antijamur azol)", "Ruam, pruritus, urtikaria, angioedema", "SegeraKeDokter"),
    "ZAT-025": ("Antijamur Imidazol", "Alergi Ketoconazole", "Miconazole; Itraconazole; Fluconazole (antijamur azol)", "Ruam kulit, pruritus, anafilaksis setelah dosis pertama (jarang)", "SegeraKeDokter"),
    "ZAT-026": ("Antijamur Triazol", "Alergi Fluconazole", "Itraconazole; Ketoconazole; Voriconazole (antijamur azol)", "Ruam eksfoliatif, SJS/TEN jarang, anafilaksis", "SegeraKeDokter"),
    "ZAT-027": ("Herbal Xanthone (Clusiaceae)", "Alergi Kulit Buah Manggis", "Alergi buah manggis / tanaman famili Clusiaceae", "Gatal, ruam, bengkak mulut/tenggorokan pada individu hipersensitif", "TanyaApoteker"),
    "ZAT-028": ("Herbal Kurkuminoid (Zingiberaceae)", "Alergi Kunyit / Temulawak", "Jahe / tanaman famili Zingiberaceae (alergi silang rimpang jarang); alergi pewarna kuning kurkumin", "Dermatitis kontak, urtikaria, gangguan saluran cerna", "TanyaApoteker"),
    "ZAT-029": ("Herbal Gingerol (Zingiberaceae)", "Alergi Jahe Merah / Jahe", "Kunyit / temulawak / kapulaga (famili Zingiberaceae)", "Ruam kulit, gatal mulut/tenggorokan pada individu alergi jahe", "TanyaApoteker"),
    "ZAT-030": ("Antihistamin H1 Alkilamin", "Alergi Triprolidine", "Chlorpheniramine (CTM); Brompheniramine (sesama kelas alkilamin)", "Ruam, urtikaria, reaksi hipersensitivitas", "TanyaApoteker"),
    "ZAT-031": ("Antihistamin H1 Etanolamin", "Alergi Doxylamine", "Diphenhydramine; Dimenhydrinate (sesama kelas etanolamin)", "Ruam, gatal, hipersensitivitas jarang", "TanyaApoteker"),
}

KW_RE = re.compile(
    r"(hypersensitiv|allerg|anaphyla|aspirin|nsaid|penicillin|cephalosporin|sulfonamid|angioedema|urticaria|bronchospasm|cross-sensitiv)",
    re.IGNORECASE,
)


def query_openfda(generic_name: str):
    q = urllib.parse.quote(f'openfda.generic_name:"{generic_name}"')
    url = f"https://api.fda.gov/drug/label.json?search={q}&limit=10"
    req = urllib.request.Request(url, headers={"User-Agent": "ProjectKBR-Group4/1.0 (UNS Academic)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        results = data.get("results") or []
        if not results:
            return None

        def score(r):
            ofda = r.get("openfda", {})
            subs = ofda.get("substance_name") or []
            gens = ofda.get("generic_name") or []
            has_set = 1 if ofda.get("spl_set_id") else 0
            is_single = 2 if (len(subs) == 1 or (len(gens) == 1 and " and " not in gens[0].lower() and "," not in gens[0])) else 0
            has_contra = 2 if r.get("contraindications") else (1 if r.get("do_not_use") or r.get("warnings") else 0)
            return (is_single, has_set, has_contra)

        results.sort(key=score, reverse=True)
        return results[0]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        return {"error": f"HTTP {e.code}"}
    except Exception as e:
        return {"error": str(e)}


def extract_allergy_snippet(record: dict) -> str:
    texts = []
    for field in ("contraindications", "do_not_use", "warnings_and_cautions", "warnings", "stop_use", "boxed_warning"):
        val = record.get(field)
        if isinstance(val, list):
            texts.extend(val)
        elif isinstance(val, str):
            texts.append(val)
    combined = " ".join(texts)
    sentences = re.split(r"(?<=[.!?])\s+", combined)
    matched = [s.strip() for s in sentences if KW_RE.search(s)]
    if matched:
        snippet = " ".join(matched[:2])
    else:
        for fallback_f in ("contraindications", "do_not_use", "warnings"):
            if record.get(fallback_f):
                v0 = record[fallback_f][0] if isinstance(record[fallback_f], list) else str(record[fallback_f])
                snippet = v0.strip()
                break
        else:
            snippet = ""
    return re.sub(r"\s+", " ", snippet)[:420]


def main():
    with open(SHEET1_PATH, "r", encoding="utf-8") as f:
        zat_rows = list(csv.DictReader(f))

    raw_traces = []
    csv_out = []

    for r in zat_rows:
        zid = r["id_zat"].strip()
        nama = r["nama_zat"].strip()
        atc = r["kode_atc"].strip()
        fda_name = FDA_SEARCH_NAME.get(zid)
        prof = ALLERGY_PROFILE[zid]

        snippet = ""
        source_url = ""
        eff_time = ""
        set_id = ""
        status_sumber = ""

        if fda_name:
            res = query_openfda(fda_name)
            time.sleep(0.15)  # rate-limit polite delay
            if res and "error" not in res:
                openfda = res.get("openfda", {})
                set_ids = openfda.get("spl_set_id") or []
                set_id = set_ids[0] if set_ids else ""
                eff_time = res.get("effective_time", "")
                snippet = extract_allergy_snippet(res)
                if set_id:
                    source_url = f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={set_id}"
                else:
                    source_url = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:%22{urllib.parse.quote(fda_name)}%22&limit=1"
                status_sumber = f"OpenFDA Drug Label API (effective_time: {eff_time or 'N/A'})"
                raw_traces.append({
                    "id_zat": zid,
                    "nama_zat": nama,
                    "fda_query": fda_name,
                    "spl_set_id": set_id,
                    "effective_time": eff_time,
                    "url": source_url,
                    "snippet": snippet,
                })
            else:
                # Tidak terdaftar di label FDA AS (mis. Bromhexine, Ambroxol)
                source_url = "https://pionas.pom.go.id"
                snippet = f"Tidak terdapat di label OpenFDA AS; rujuk monograf PIONAS BPOM untuk hipersensitivitas {nama}."
                status_sumber = "PIONAS BPOM RI (tidak terdaftar di OpenFDA AS)"
                raw_traces.append({
                    "id_zat": zid,
                    "nama_zat": nama,
                    "fda_query": fda_name,
                    "status": "not_in_openfda",
                    "fallback": source_url,
                })
        else:
            source_url = "https://pionas.pom.go.id / DOI: 10.1016/j.phymed.2011.01.010"
            snippet = f"Bahan herbal (non-FDA Drug Label); kewaspadaan alergi tumbuhan/famili terkait untuk {nama}."
            status_sumber = "Kurasi Literatur Herbal & BPOM"
            raw_traces.append({
                "id_zat": zid,
                "nama_zat": nama,
                "status": "herbal_non_fda",
                "url": source_url,
            })

        csv_out.append({
            "id_zat": zid,
            "nama_zat": nama,
            "kode_atc": atc,
            "golongan_alergen": prof[0],
            "alergi_langsung": prof[1],
            "pemicu_alergi_silang": prof[2],
            "gejala_alergi_waspada": prof[3],
            "tindak_lanjut": prof[4],
            "kutipan_fda_atau_label": snippet,
            "url_sumber": source_url,
            "tanggal_akses": TODAY,
            "status_sumber": status_sumber,
        })

    with open(OUT_RAW_JSON, "w", encoding="utf-8") as f:
        json.dump(raw_traces, f, indent=2, ensure_ascii=False)

    fieldnames = [
        "id_zat", "nama_zat", "kode_atc", "golongan_alergen", "alergi_langsung",
        "pemicu_alergi_silang", "gejala_alergi_waspada", "tindak_lanjut",
        "kutipan_fda_atau_label", "url_sumber", "tanggal_akses", "status_sumber",
    ]
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(csv_out)

    fda_ok = sum(1 for x in csv_out if "OpenFDA Drug Label API" in x["status_sumber"])
    print(f"[OK] substansi_alergi.csv : {len(csv_out)} baris | OpenFDA terverifikasi: {fda_ok} | PIONAS/Herbal: {len(csv_out) - fda_ok}")
    print(f"[OK] Jejak raw JSON       : {OUT_RAW_JSON}")


if __name__ == "__main__":
    main()
