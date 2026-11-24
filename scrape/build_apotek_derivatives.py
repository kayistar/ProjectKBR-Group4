"""
build_apotek_derivatives.py
===========================
Menghasilkan dataset turunan otomatis (tanpa scrape ulang) sesuai RENCANA_KERJA.md:
  1. data/curation/sinonim_zat.csv
  2. data/apotek/dikecualikan.csv
  3. data/apotek/harga_per_unit.csv
  4. data/interactions/ddinter_31zat_pairs.csv

Semua memakai path relatif terhadap root repositori.
"""

import csv
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEET1_PATH = os.path.join(ROOT, "data", "curation", "sheet1_zat_aktif.csv")
SHEET2_PATH = os.path.join(ROOT, "data", "curation", "sheet2_interaksi.csv")
DETAIL_PATH = os.path.join(ROOT, "data", "apotek", "produk_detail.csv")
BATUK_PATH = os.path.join(ROOT, "data", "apotek", "produk_batuk.csv")
PILEK_PATH = os.path.join(ROOT, "data", "apotek", "produk_pilek.csv")
KB_DIR = os.path.join(ROOT, "KB")

OUT_SINONIM = os.path.join(ROOT, "data", "curation", "sinonim_zat.csv")
OUT_EXCLUDED = os.path.join(ROOT, "data", "apotek", "dikecualikan.csv")
OUT_HARGA = os.path.join(ROOT, "data", "apotek", "harga_per_unit.csv")
OUT_DDINTER = os.path.join(ROOT, "data", "interactions", "ddinter_31zat_pairs.csv")


def load_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_csv(path, fieldnames, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------------------
# 1. data/curation/sinonim_zat.csv
# ---------------------------------------------------------------------------
zat_rows = load_csv(SHEET1_PATH)

SYNONYMS_MAP = {
    "ZAT-001": ("paracetamol|parasetamol|acetaminophen|asetaminofen|pct", "paracetamol; asetaminofen; pct"),
    "ZAT-002": ("ibuprofen", "ibuprofen"),
    "ZAT-003": ("dextromethorphan|dekstrometorfan|dextrometorphan|dxm|dmp", "dxm; dmp; dekstrometorfan"),
    "ZAT-004": ("pseudoephedrine|pseudoefedrin|pse", "pseudoefedrin; pse"),
    "ZAT-005": ("phenylephrine|phenylefrine|fenilefrin|phenilefrin", "fenilefrin; pe"),
    "ZAT-006": ("chlorpheniramine|chlorpeniramine|chlorpheniramini|klorfeniramin|klorfeniramina|dexchlorpheniramine|ctm", "ctm; klorfeniramin"),
    "ZAT-007": ("diphenhydramine|difenhidramin|dph", "difenhidramin; dph"),
    "ZAT-008": ("cetirizine|cetirizin|setirizin", "setirizin"),
    "ZAT-009": ("bromhexine|bromheksin|bromhexin", "bromheksin"),
    "ZAT-010": ("ambroxol|ambroksol", "ambroksol"),
    "ZAT-011": ("guaifenesin|guafenesin|glyceryl guaiacolate|gliceryl guaiacolate|glicerylguaiacolat|gliseril guaiakolat|gg", "gg; glyceryl guaiacolate; guafenesin"),
    "ZAT-012": ("simvastatin", "simvastatin"),
    "ZAT-013": ("atorvastatin", "atorvastatin"),
    "ZAT-014": ("amlodipine|amlodipin", "amlodipin"),
    "ZAT-015": ("captopril|kaptopril", "kaptopril"),
    "ZAT-016": ("metformin", "metformin"),
    "ZAT-017": ("glimepiride|glimepirid", "glimepirid"),
    "ZAT-018": ("warfarin", "warfarin"),
    "ZAT-019": ("clopidogrel|klopidogrel", "klopidogrel"),
    "ZAT-020": ("digoxin|digoksin", "digoksin"),
    "ZAT-021": ("omeprazole|omeprazol", "omeprazol"),
    "ZAT-022": ("ciprofloxacin|siprofloksasin", "siprofloksasin"),
    "ZAT-023": ("amoxicillin|amoksisilin", "amoksisilin"),
    "ZAT-024": ("itraconazole|itrakonazol", "itrakonazol"),
    "ZAT-025": ("ketoconazole|ketokonazol", "ketokonazol"),
    "ZAT-026": ("fluconazole|flukonazol", "flukonazol"),
    "ZAT-027": ("alpha-mangostin|alpha mangostin|mangostin|kulit manggis|ekstrak kulit manggis|garcinia mangostana", "kulit manggis; garcinia mangostana"),
    "ZAT-028": ("curcumin|kurkumin|kunyit|temulawak|curcuma", "kurkumin; kunyit; temulawak; curcuma"),
    "ZAT-029": ("gingerol|jahe merah|jahe|zingiber", "jahe; jahe merah; zingiber"),
    "ZAT-030": ("triprolidine|tripolidine|triprolidin", "tripolidine; triprolidin"),
    "ZAT-031": ("doxylamine|doksilamin|doxylamin", "doksilamin suksinat"),
}

sinonim_out = []
for r in zat_rows:
    zid = r["id_zat"].strip()
    regex_pat, catatan = SYNONYMS_MAP.get(zid, (r["nama_zat"].lower(), ""))
    sinonim_out.append({
        "id_zat": zid,
        "nama_zat": r["nama_zat"],
        "chebi_id": r["chebi_id"],
        "chebi_iri": r["chebi_iri"],
        "regex_komposisi": regex_pat,
        "sinonim_katalog": catatan,
        "cakupan_v1": r.get("cakupan_v1", ""),
    })

save_csv(
    OUT_SINONIM,
    ["id_zat", "nama_zat", "chebi_id", "chebi_iri", "regex_komposisi", "sinonim_katalog", "cakupan_v1"],
    sinonim_out,
)

# ---------------------------------------------------------------------------
# 2. data/apotek/dikecualikan.csv & 3. data/apotek/harga_per_unit.csv
# ---------------------------------------------------------------------------
detail_rows = load_csv(DETAIL_PATH)
batuk_slugs = {r["slug"].strip() for r in load_csv(BATUK_PATH)}
pilek_slugs = {r["slug"].strip() for r in load_csv(PILEK_PATH)}
bp_slugs = batuk_slugs | pilek_slugs

excluded_rows = []
harga_rows = []


def parse_packaging(nama, kemasan, harga_str):
    nama_l = (nama or "").lower()
    kem_l = (kemasan or "").lower()
    harga = int(harga_str) if (harga_str or "").strip().isdigit() else 0

    # Determine unit type
    if any(k in nama_l or k in kem_l for k in ("sirup", "syrup", "syr", "suspensi", "drop", "tetes", "ml")):
        satuan = "mL"
        # Extract volume e.g. 60ML, 100ML, 15ML
        m_vol = re.search(r"(\d+(?:[.,]\d+)?)\s*ml\b", f"{nama_l} {kem_l}")
        if m_vol:
            qty = float(m_vol.group(1).replace(",", "."))
        else:
            qty = 1.0
            satuan = "botol"
    elif any(k in nama_l or k in kem_l for k in ("sachet", "sach", "pcs", "serbuk")):
        satuan = "sachet"
        m_dos = re.search(r"(\d+)\s*(?:strip|sach|sachet|pcs|dos)\s*x\s*(\d+)", kem_l)
        m_isi = re.search(r"isi\s*(\d+)\s*(?:pcs|sach|sachet)", kem_l)
        if "1 pcs isi 1 pcs" in kem_l:
            qty = 1.0
        elif m_dos:
            qty = float(int(m_dos.group(1)) * int(m_dos.group(2)))
        elif m_isi:
            qty = float(int(m_isi.group(1)))
        else:
            qty = 1.0
    elif any(k in nama_l or k in kem_l for k in ("kapsul", "capsule", "cap ", "caps")):
        satuan = "kapsul"
        m_mult = re.search(r"(\d+)\s*strip\s*x\s*(\d+)\s*(?:kapsul|kaplet|tablet|cap)", kem_l)
        m_isi = re.search(r"isi\s*(\d+)\s*(?:kapsul|kaplet|tablet)", kem_l)
        m_btl = re.search(r"(\d+)s\b", nama_l)
        if "1 strip" in kem_l and "x" not in kem_l and m_isi:
            qty = float(int(m_isi.group(1)))
        elif m_mult:
            qty = float(int(m_mult.group(1)) * int(m_mult.group(2)))
        elif m_isi:
            qty = float(int(m_isi.group(1)))
        elif m_btl and ("btl" in nama_l or "botol" in kem_l):
            qty = float(int(m_btl.group(1)))
        else:
            qty = 1.0
    elif any(k in nama_l or k in kem_l for k in ("tablet", "kaplet", "tab", "capl")):
        satuan = "tablet/kaplet"
        m_mult = re.search(r"(\d+)\s*strip\s*x\s*(\d+)\s*(?:tablet|kaplet)", kem_l)
        m_isi = re.search(r"isi\s*(\d+)\s*(?:tablet|kaplet)", kem_l)
        m_strip_only = re.search(r"1\s*strip\s*isi\s*1\s*strip", kem_l)
        m_name_s = re.search(r"(\d+)s\s*(?:strip|tab|capl)", nama_l)
        m_name_num = re.search(r"-(\d+)s-", f"-{nama_l}-")
        if m_mult:
            qty = float(int(m_mult.group(1)) * int(m_mult.group(2)))
        elif m_isi:
            qty = float(int(m_isi.group(1)))
        elif m_strip_only and m_name_s:
            qty = float(int(m_name_s.group(1)))
        elif "1 dos" in kem_l and m_name_num:
            qty = float(int(m_name_num.group(1)))
        else:
            qty = 1.0
    else:
        satuan = "kemasan"
        qty = 1.0

    # Heuristic sanity check: if packaging says "1 Dos isi 25 Strip" without "x N", check name e.g. 4S-STRIP-25S -> 100
    m_dos_strip = re.search(r"1\s*dos\s*isi\s*(\d+)\s*strip\b(?!\s*x)", kem_l)
    if m_dos_strip and satuan in ("tablet/kaplet", "kapsul"):
        n_strip = int(m_dos_strip.group(1))
        m_per_strip = re.search(r"(\d+)s", nama_l)
        if m_per_strip:
            per_s = int(m_per_strip.group(1))
            if per_s != n_strip:
                qty = float(n_strip * per_s)

    if harga <= 0:
        status = "tanpa_harga"
        unit_price = ""
    elif qty <= 0:
        status = "kemasan_tidak_terurai"
        unit_price = ""
    else:
        unit_price = round(harga / qty, 2)
        status = "ok" if satuan != "kemasan" and not (satuan in ("tablet/kaplet", "kapsul") and qty == 1.0 and "dos" in kem_l) else "perkiraan_per_kemasan"

    return harga, qty, satuan, unit_price, status


for r in detail_rows:
    slug = r["slug"].strip()
    nama = r["nama"].strip()
    komp = (r.get("komposisi") or "").strip()
    komp_l = komp.lower()
    harga_str = (r.get("harga_rp") or "").strip()
    in_bp = "ya" if slug in bp_slugs else "tidak"

    # Check exclusion criteria
    alasan = []
    if not komp:
        alasan.append("komposisi_kosong")
    elif "<p " in komp_l or "<div" in komp_l or "box-sizing:" in komp_l:
        alasan.append("komposisi_html_korup")
    elif len(komp) < 3:
        alasan.append("komposisi_terlalu_pendek")

    # Also check matched substances among our 31 curated substances
    matched_ids = []
    if not alasan:
        for srow in sinonim_out:
            if re.search(srow["regex_komposisi"], komp_l):
                matched_ids.append(srow["id_zat"])

    if alasan or (in_bp == "ya" and not matched_ids):
        if not alasan and in_bp == "ya" and not matched_ids:
            alasan.append("zat_di_luar_31_kurasi")
        excluded_rows.append({
            "slug": slug,
            "nama": nama,
            "kategori_batuk_pilek": in_bp,
            "alasan_pengecualian": ";".join(alasan),
            "komposisi_mentah": komp[:150],
            "harga_rp": harga_str,
        })

    harga, qty, satuan, unit_price, p_status = parse_packaging(nama, r.get("kemasan", ""), harga_str)
    harga_rows.append({
        "slug": slug,
        "nama": nama,
        "kategori_batuk_pilek": in_bp,
        "golongan": r.get("golongan", ""),
        "kemasan": r.get("kemasan", ""),
        "harga_rp": harga if harga > 0 else "",
        "jumlah_unit": int(qty) if qty.is_integer() else qty,
        "satuan_unit": satuan,
        "harga_per_unit_rp": unit_price,
        "status_parsing": p_status,
    })

save_csv(
    OUT_EXCLUDED,
    ["slug", "nama", "kategori_batuk_pilek", "alasan_pengecualian", "komposisi_mentah", "harga_rp"],
    excluded_rows,
)
save_csv(
    OUT_HARGA,
    ["slug", "nama", "kategori_batuk_pilek", "golongan", "kemasan", "harga_rp", "jumlah_unit", "satuan_unit", "harga_per_unit_rp", "status_parsing"],
    harga_rows,
)

# ---------------------------------------------------------------------------
# 4. data/interactions/ddinter_31zat_pairs.csv
# ---------------------------------------------------------------------------
# Map DDInter drug names (lowercase) -> ZAT-xxx
ddinter_name_to_zat = {}
for r in zat_rows:
    zid = r["id_zat"].strip()
    raw = r["nama_zat"].strip()
    base = re.sub(r"\s*\(.*?\)", "", raw).strip().lower()
    ddinter_name_to_zat[base] = (zid, raw, r.get("cakupan_v1", ""))
# Extra DDInter canonical names
ddinter_name_to_zat["acetaminophen"] = ddinter_name_to_zat["paracetamol"]
ddinter_name_to_zat["chlorpheniramine"] = ddinter_name_to_zat["chlorpheniramine"]
ddinter_name_to_zat["guaifenesin"] = ddinter_name_to_zat["guaifenesin"]

# Load curated pairs from sheet2_interaksi.csv
sheet2_rows = load_csv(SHEET2_PATH)
curated_pairs = {}
for r in sheet2_rows:
    a = r["chebi_a"].strip()
    b = r["chebi_b"].strip()
    pair = tuple(sorted([a, b]))
    curated_pairs[pair] = r["id"].strip()

chebi_of_zat = {r["id_zat"].strip(): r["chebi_id"].strip() for r in zat_rows}

# Cough/cold vs chronic classification based on ATC / zat role
COUGH_COLD_IDS = {f"ZAT-0{i:02d}" for i in range(1, 12)} | {"ZAT-030", "ZAT-031"}
HERBAL_IDS = {"ZAT-027", "ZAT-028", "ZAT-029"}

found_pairs = {}
for fpath in sorted(glob.glob(os.path.join(KB_DIR, "ddinter_downloads_code_*.csv"))):
    code_file = os.path.basename(fpath)
    with open(fpath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            da = row["Drug_A"].strip().lower()
            db = row["Drug_B"].strip().lower()
            if da in ddinter_name_to_zat and db in ddinter_name_to_zat:
                za_id, za_name, za_cak = ddinter_name_to_zat[da]
                zb_id, zb_name, zb_cak = ddinter_name_to_zat[db]
                if za_id == zb_id:
                    continue
                if za_id < zb_id:
                    key = (za_id, zb_id)
                    rec = (za_id, za_name, row["DDInterID_A"].strip(), zb_id, zb_name, row["DDInterID_B"].strip())
                else:
                    key = (zb_id, za_id)
                    rec = (zb_id, zb_name, row["DDInterID_B"].strip(), za_id, za_name, row["DDInterID_A"].strip())

                lvl = row["Level"].strip()
                if key not in found_pairs or (found_pairs[key]["level_ddinter"] == "Unknown" and lvl != "Unknown"):
                    ca, cb = chebi_of_zat[key[0]], chebi_of_zat[key[1]]
                    cur_id = curated_pairs.get(tuple(sorted([ca, cb])), "")
                    in_bp_chronic = (
                        (key[0] in COUGH_COLD_IDS and key[1] not in COUGH_COLD_IDS)
                        or (key[1] in COUGH_COLD_IDS and key[0] not in COUGH_COLD_IDS)
                    )
                    found_pairs[key] = {
                        "id_zat_a": rec[0],
                        "nama_zat_a": rec[1],
                        "ddinter_id_a": rec[2],
                        "id_zat_b": rec[3],
                        "nama_zat_b": rec[4],
                        "ddinter_id_b": rec[5],
                        "level_ddinter": lvl,
                        "status_data": "unknown_perlu_tanya_apoteker" if lvl == "Unknown" else "terverifikasi_ddinter",
                        "domain_batuk_pilek_x_kronis": "ya" if in_bp_chronic else "tidak",
                        "id_kurasi_sheet2": cur_id,
                        "sumber_file": code_file,
                    }

ddinter_out = sorted(found_pairs.values(), key=lambda x: (x["domain_batuk_pilek_x_kronis"] != "ya", x["level_ddinter"], x["id_zat_a"], x["id_zat_b"]))
save_csv(
    OUT_DDINTER,
    ["id_zat_a", "nama_zat_a", "ddinter_id_a", "id_zat_b", "nama_zat_b", "ddinter_id_b", "level_ddinter", "status_data", "domain_batuk_pilek_x_kronis", "id_kurasi_sheet2", "sumber_file"],
    ddinter_out,
)

# Summary stats
bp_x_chron = [x for x in ddinter_out if x["domain_batuk_pilek_x_kronis"] == "ya"]
from collections import Counter
print(f"[1] sinonim_zat.csv          : {len(sinonim_out)} baris")
print(f"[2] dikecualikan.csv         : {len(excluded_rows)} produk dikecualikan (BP: {sum(1 for x in excluded_rows if x['kategori_batuk_pilek']=='ya')})")
print(f"[3] harga_per_unit.csv       : {len(harga_rows)} produk | status={dict(Counter(x['status_parsing'] for x in harga_rows))}")
print(f"[4] ddinter_31zat_pairs.csv  : {len(ddinter_out)} pasangan total | domain batuk-pilek x kronis: {len(bp_x_chron)} -> {dict(Counter(x['level_ddinter'] for x in bp_x_chron))}")
