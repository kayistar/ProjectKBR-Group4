"""
build_kb_v2.py
==============
Merakit out/kb_v2.owl sesuai docs/RENCANA_KERJA.md:
  - 100% path relatif & data-driven dari seluruh CSV di data/
  - Tanpa hardcode produk, tanpa membocorkan kelas/efek samping/kontraindikasi/indikasi
    produk di ABox (diserahkan murni ke Reasoner HermiT via GCI + OWL Property Chains +
    AllDisjointClasses + Closure Axioms)
  - Menyambungkan:
    * 31 Zat Aktif + Enzim CYP450 (dimetabolismeOleh -> PR_P08684/P10635/P33261/P11712)
    * 17 Kelas Terapi ATC Level-4 (memilikiKelasATC4 dari data/atc/atc_all.csv)
    * Aturan pakai, waktu konsumsi, umur, berat badan (substansi_aturan_pakai.csv)
    * 14 Kondisi Pasien + kontraindikasi & pantangan makanan (substansi_kontraindikasi.csv)
    * Alergi & alergi silang OpenFDA + PIONAS (substansi_alergi.csv)
    * 22 Gejala + batas durasi swamedikasi (symptoms_selected.csv + aturan_durasi.csv)
    * 20 Interaksi kurasi + 51 pasangan DDInter domain batuk-pilek x kronis (termasuk Unknown!)
    * 21 Record SumberBukti (didukungOleh dari evidence_interaksi.csv)
    * 345+ Produk Apotek bersih + harga per unit (produk_batuk/pilek + harga_per_unit - dikecualikan)
    * Produk herbal terkurasi (sheet5_produk_herbal.csv)
    * 3 Fixture KasusPasien (Actifed+Digoxin, Dobel Paracetamol, Komix+Actifed)
"""

import csv
import datetime
import hashlib
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "out", "kb_v2.owl")
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

# Relative data paths
P_SHEET1 = os.path.join(ROOT, "data", "curation", "sheet1_zat_aktif.csv")
P_SINONIM = os.path.join(ROOT, "data", "curation", "sinonim_zat.csv")
P_ATURAN = os.path.join(ROOT, "data", "curation", "substansi_aturan_pakai.csv")
P_KONTRA = os.path.join(ROOT, "data", "curation", "substansi_kontraindikasi.csv")
P_ALERGI = os.path.join(ROOT, "data", "curation", "substansi_alergi.csv")
P_DURASI = os.path.join(ROOT, "data", "curation", "aturan_durasi.csv")
P_SHEET2 = os.path.join(ROOT, "data", "curation", "sheet2_interaksi.csv")
P_DDINTER = os.path.join(ROOT, "data", "interactions", "ddinter_31zat_pairs.csv")
P_EVIDENCE = os.path.join(ROOT, "data", "curation", "evidence_interaksi.csv")
P_HERBAL = os.path.join(ROOT, "data", "curation", "sheet5_produk_herbal.csv")
P_SYMP = os.path.join(ROOT, "data", "symptoms", "symptoms_selected.csv")
P_ATC = os.path.join(ROOT, "data", "atc", "atc_all.csv")
P_BATUK = os.path.join(ROOT, "data", "apotek", "produk_batuk.csv")
P_PILEK = os.path.join(ROOT, "data", "apotek", "produk_pilek.csv")
P_HARGA = os.path.join(ROOT, "data", "apotek", "harga_per_unit.csv")
P_EXCL = os.path.join(ROOT, "data", "apotek", "dikecualikan.csv")

# Shared kbr: vocabulary IRI (compatible with q1..q9) while Ontology IRI is kb_v2.owl
BASE = "http://purl.obolibrary.org/obo/kbr-group4/kb_v1.owl#"
ONTO = "http://purl.obolibrary.org/obo/kbr-group4/kb_v2.owl"
CHEBI = "http://purl.obolibrary.org/obo/CHEBI_"
SYMP = "http://purl.obolibrary.org/obo/SYMP_"
PRO = "http://purl.obolibrary.org/obo/PR_"
OBO = "http://www.geneontology.org/formats/oboInOwl#"
SKOS = "http://www.w3.org/2004/02/skos/core#"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
OWL_NS = "http://www.w3.org/2002/07/owl#"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
XSD = "http://www.w3.org/2001/XMLSchema#"
SWRL = "http://www.w3.org/2003/11/swrl#"
SWRLB = "http://www.w3.org/2003/11/swrlb#"

NOW = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat()


def iri(localname: str) -> str:
    return f"{BASE}{localname}"


def symp_iri(num: str) -> str:
    return f"{SYMP}{num}"


def xml_safe(s) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def slug_to_id(slug: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_]+", "_", slug).strip("_")
    return f"prod_{clean}"


def load_csv(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


# --- Load all CSV datasets ---
zat_rows = load_csv(P_SHEET1)
sinonim_rows = load_csv(P_SINONIM)
aturan_map = {r["id_zat"].strip(): r for r in load_csv(P_ATURAN)}
kontra_map = {r["id_zat"].strip(): r for r in load_csv(P_KONTRA)}
alergi_map = {r["id_zat"].strip(): r for r in load_csv(P_ALERGI)}
durasi_map = {r["obo_id"].strip(): r for r in load_csv(P_DURASI)}
sheet2_rows = load_csv(P_SHEET2)
ddinter_rows = load_csv(P_DDINTER)
evidence_rows = load_csv(P_EVIDENCE)
herbal_rows = load_csv(P_HERBAL)
symp_rows = load_csv(P_SYMP)
atc_rows = {r["atc_code"].strip(): r["atc_name"].strip() for r in load_csv(P_ATC) if r["atc_level"].strip() == "4"}
harga_map = {r["slug"].strip(): r for r in load_csv(P_HARGA)}
excl_slugs = {
    r["slug"].strip()
    for r in load_csv(P_EXCL)
    if "komposisi_kosong" in r["alasan_pengecualian"] or "komposisi_html_korup" in r["alasan_pengecualian"]
}

chebi_by_id = {r["chebi_id"].strip(): r["chebi_iri"].strip() for r in zat_rows}
chebi_by_zat = {r["id_zat"].strip(): r["chebi_iri"].strip() for r in zat_rows}

# Build dynamic regex matcher from sinonim_zat.csv
ZAT_PATTERNS = []
for s in sinonim_rows:
    tokens = [t.strip() for t in s["regex_komposisi"].split("|") if t.strip()]
    pat = "|".join(rf"\b{re.escape(t)}\b" for t in tokens)
    ZAT_PATTERNS.append((pat, s["chebi_iri"].strip(), s["id_zat"].strip()))

# Deduplicate cough/cold products excluding invalid/corrupt compositions
produk_map = {}
for r in load_csv(P_BATUK) + load_csv(P_PILEK):
    slug = r["slug"].strip()
    if slug and slug not in excl_slugs and slug not in produk_map:
        produk_map[slug] = r

parsed_products = []
for slug, r in produk_map.items():
    komp = (r.get("komposisi") or "").lower().strip()
    matched_iris = []
    for pat, z_iri, _ in ZAT_PATTERNS:
        if re.search(pat, komp) and z_iri not in matched_iris:
            matched_iris.append(z_iri)
    if matched_iris:
        parsed_products.append((r, matched_iris))

# Condition column -> KondisPasien local class name + label
KONDISI_SPEC = {
    "hipertensi_tidak_terkontrol": ("HipertensiTidakTerkontrol", "Hipertensi Tidak Terkontrol"),
    "penyakit_jantung_koroner_aritmia": ("PenyakitJantungAritmia", "Penyakit Jantung Koroner / Aritmia"),
    "hipertiroid": ("Hipertiroid", "Hipertiroid"),
    "diabetes_melitus": ("DiabetesMelitus", "Diabetes Melitus"),
    "glaukoma_sudut_sempit": ("GlaukomaSudutSempit", "Glaukoma Sudut Sempit"),
    "pembesaran_prostat_bph": ("ProstatBPH", "Pembesaran Prostat (BPH)"),
    "gagal_jantung": ("GagalJantung", "Gagal Jantung"),
    "tukak_lambung_gerd": ("TukakLambungGERD", "Tukak Lambung / GERD"),
    "gangguan_hati_berat": ("GangguanHatiBerat", "Gangguan Hati Berat"),
    "gangguan_ginjal_berat": ("GangguanGinjalBerat", "Gangguan Ginjal Berat"),
    "hamil": ("Kehamilan", "Ibu Hamil"),
    "menyusui": ("Menyusui", "Ibu Menyusui"),
    "anak_bawah_2_tahun": ("AnakBawah2Tahun", "Anak Usia < 2 Tahun"),
    "lansia_65_plus": ("Lansia65Plus", "Lansia Usia >= 65 Tahun"),
}

# CYP450 enzymes matching out/enzim_modul.owl (PRO)
CYP_ENZYMES = {
    "CYP3A4": (f"{PRO}P08684", "CYP3A4 (Cytochrome P450 3A4)"),
    "CYP2D6": (f"{PRO}P10635", "CYP2D6 (Cytochrome P450 2D6)"),
    "CYP2C19": (f"{PRO}P33261", "CYP2C19 (Cytochrome P450 2C19)"),
    "CYP2C9": (f"{PRO}P11712", "CYP2C9 (Cytochrome P450 2C9)"),
}

# Pharmacological role -> indicated SYMP symptoms (at ZatAktif level; propagated to ProduktObat via OWL property chain!)
def infer_zat_indications(peran: str) -> list[str]:
    p = (peran or "").lower()
    out = []
    if "antitusif" in p:
        out.extend([symp_iri("0000614"), symp_iri("0000025")])
    if "mukolitik" in p or "ekspektoran" in p:
        out.extend([symp_iri("0000614"), symp_iri("0020027")])
    if "dekongestan" in p:
        out.append(symp_iri("0000869"))
    if "antihistamin" in p:
        out.extend([symp_iri("0000372"), symp_iri("0000139")])
    if "antipiretik" in p or "analgesik" in p:
        out.extend([symp_iri("0000613"), symp_iri("0000504"), symp_iri("0000505")])
    return list(dict.fromkeys(out))


def map_golongan(gol_str: str) -> str:
    g = (gol_str or "").lower().strip()
    if "bebas terbatas" in g:
        return "ObatBebasTerbatas"
    if "bebas" in g:
        return "ObatBebas"
    if "jamu" in g or "herbal" in g or "fitofarmaka" in g:
        return "ObatHerbalJamu"
    return "ObatBebasTerbatas"


def map_sediaan(nama_str: str, kemasan_str: str) -> str:
    txt = f"{nama_str} {kemasan_str}".lower()
    if any(k in txt for k in ("sirup", "syrup", "syr", "suspensi", "drop")):
        return "Sirup"
    if any(k in txt for k in ("sachet", "sach", "serbuk")):
        return "Sachet"
    if any(k in txt for k in ("kapsul", "cap ", "caps")):
        return "Kapsul"
    return "Tablet"


lines = []


def w(s: str):
    lines.append(s)


# --- Header ---
w('<?xml version="1.0" encoding="UTF-8"?>')
w("<rdf:RDF")
w(f'    xmlns:rdf="{RDF_NS}"')
w(f'    xmlns:rdfs="{RDFS}"')
w(f'    xmlns:owl="{OWL_NS}"')
w(f'    xmlns:xsd="{XSD}"')
w(f'    xmlns:skos="{SKOS}"')
w(f'    xmlns:oboInOwl="{OBO}"')
w(f'    xmlns:swrl="{SWRL}"')
w(f'    xmlns:swrlb="{SWRLB}"')
w(f'    xmlns:kbr="{BASE}">')
w("")
w(f'  <owl:Ontology rdf:about="{ONTO}">')
w('    <rdfs:label xml:lang="id">KB v2 Basis Pengetahuan Interaksi Obat Batuk-Pilek &amp; Swamedikasi (Group 4)</rdfs:label>')
w(f'    <owl:versionIRI rdf:resource="{ONTO}/2.0"/>')
w('    <rdfs:comment xml:lang="id">KB v2 non-hardcode sesuai RENCANA_KERJA.md. Memuat 31 zat aktif + enzim CYP450 + ATC-4, aturan pakai/waktu konsumsi/umur/BB, 14 kondisi kontraindikasi, alergi OpenFDA, 22 gejala + durasi, 20 interaksi kurasi + DDInter domain (termasuk Unknown), 21 SumberBukti, dan 345+ produk apotek + herbal.</rdfs:comment>')
w(f"    <oboInOwl:date>{NOW}</oboInOwl:date>")
w('    <oboInOwl:creator xml:lang="id">Group 4 KBR - Universitas Sebelas Maret</oboInOwl:creator>')
w("  </owl:Ontology>")
w("")

# --- Annotation Properties ---
for ap_iri, ap_lbl in [(f"{OBO}date", "date"), (f"{OBO}creator", "creator"), (f"{SKOS}altLabel", "altLabel")]:
    w(f'  <owl:AnnotationProperty rdf:about="{ap_iri}"><rdfs:label>{ap_lbl}</rdfs:label></owl:AnnotationProperty>')
w("")

# --- Object Properties ---
obj_props = [
    ("memilikiKandungan", "memiliki kandungan zat aktif", "ProduktObat", "ZatAktif", ""),
    ("bagianDariHierarkiTerapi", "bagian dari hierarki terapi (transitif)", "owl:Thing", "owl:Thing", "TransitiveProperty"),
    ("mengindikasikanGejalaZat", "zat mengindikasikan gejala", "ZatAktif", "Gejala", ""),
    ("mengindikasikanGejala", "produk mengindikasikan gejala", "ProduktObat", "Gejala", ""),
    ("memilikiEfekSamping", "memiliki efek samping", "ProduktObat", "Gejala", ""),
    ("memilikiInteraksiDengan", "memiliki interaksi dengan", "ZatAktif", "ZatAktif", "SymmetricProperty"),
    ("menghasilkanInteraksi", "menghasilkan interaksi", "ZatAktif", "InteraksiObat", ""),
    ("melibatkanZatAktif", "interaksi melibatkan zat aktif", "InteraksiObat", "ZatAktif", ""),
    ("membutuhkanTindakLanjut", "membutuhkan tindak lanjut klinis", "owl:Thing", "TindakLanjut", ""),
    ("didukungOleh", "didukung oleh sumber bukti", "InteraksiObat", "SumberBukti", ""),
    ("dimetabolismeOleh", "dimetabolisme / berinteraksi dengan enzim CYP450", "ZatAktif", "EnzimCYP450", ""),
    ("memilikiKelasATC4", "memiliki kelas terapi ATC Level-4", "ZatAktif", "KelasTerapiATC4", ""),
    ("memilikiGolongan", "memiliki golongan regulasi BPOM", "ProduktObat", "GolonganObat", "FunctionalProperty"),
    ("memilikiBentukSediaan", "memiliki bentuk sediaan", "ProduktObat", "BentukSediaan", ""),
    ("kontraindikasiBagi", "kontraindikasi bagi kondisi pasien", "owl:Thing", "KondisiPasien", ""),
    ("perluHatiHatiBagi", "perlu kehati-hatian bagi kondisi pasien", "owl:Thing", "KondisiPasien", ""),
    ("memilikiObatPasien", "kasus pasien memiliki obat pasien", "KasusPasien", "ObatPasien", ""),
    ("digunakanPadaKasus", "obat pasien digunakan pada kasus pasien", "ObatPasien", "KasusPasien", ""),
    ("memilikiKondisiPasien", "kasus pasien memiliki kondisi penyerta", "KasusPasien", "KondisiPasien", ""),
    ("menggunakanProdukObat", "menggunakan produk obat", "ObatPasien", "ProduktObat", ""),
    ("menggunakanZatAktif", "menggunakan zat aktif rutin", "ObatPasien", "ZatAktif", ""),
]
for lname, lbl, dom, rng, special in obj_props:
    dom_iri = f"{OWL_NS}Thing" if dom == "owl:Thing" else iri(dom)
    rng_iri = f"{OWL_NS}Thing" if rng == "owl:Thing" else iri(rng)
    w(f'  <owl:ObjectProperty rdf:about="{iri(lname)}">')
    w(f'    <rdfs:label xml:lang="id">{lbl}</rdfs:label>')
    w(f'    <rdfs:domain rdf:resource="{dom_iri}"/>')
    w(f'    <rdfs:range rdf:resource="{rng_iri}"/>')
    if special:
        w(f'    <rdf:type rdf:resource="{OWL_NS}{special}"/>')
    # Add OWL 2 DL property chain axioms for pure HermiT propagation from ZatAktif -> ProduktObat!
    if lname == "kontraindikasiBagi":
        w('    <owl:propertyChainAxiom rdf:parseType="Collection">')
        w(f'      <rdf:Description rdf:about="{iri("memilikiKandungan")}"/>')
        w(f'      <rdf:Description rdf:about="{iri("kontraindikasiBagi")}"/>')
        w("    </owl:propertyChainAxiom>")
    elif lname == "mengindikasikanGejala":
        w('    <owl:propertyChainAxiom rdf:parseType="Collection">')
        w(f'      <rdf:Description rdf:about="{iri("memilikiKandungan")}"/>')
        w(f'      <rdf:Description rdf:about="{iri("mengindikasikanGejalaZat")}"/>')
        w("    </owl:propertyChainAxiom>")
    elif lname == "digunakanPadaKasus":
        w(f'    <owl:inverseOf rdf:resource="{iri("memilikiObatPasien")}"/>')
    w("  </owl:ObjectProperty>")
w("")

# --- Datatype Properties ---
data_props = [
    ("namaDagang", "nama dagang produk", "string"),
    ("namaProdusen", "nama produsen", "string"),
    ("nomorBPOM", "nomor izin edar BPOM", "string"),
    ("hargaRupiah", "harga katalog (Rp)", "integer"),
    ("hargaPerUnitRp", "harga per unit (Rp)", "decimal"),
    ("jumlahUnitKemasan", "jumlah unit per kemasan", "decimal"),
    ("satuanUnit", "satuan unit (mL/tablet/sachet)", "string"),
    ("statusParsingHarga", "status normalisasi harga", "string"),
    ("kemasanTeks", "teks kemasan", "string"),
    ("komposisiTeks", "teks komposisi", "string"),
    ("nomorSlugK24", "slug K24Klik", "string"),
    ("urlK24", "URL K24Klik", "anyURI"),
    ("kodeATC", "kode ATC WHO", "string"),
    ("kodeATC4", "kode ATC Level 4", "string"),
    ("chebiID", "ID ChEBI", "string"),
    ("dosisDewasa", "dosis dewasa per zat", "string"),
    ("dosisAnak", "dosis anak per zat", "string"),
    ("dosisMgPerKg", "referensi dosis mg/kgBB", "string"),
    ("usiaMinSwamedikasi", "usia minimum swamedikasi (tahun)", "string"),
    ("bbMinSwamedikasi", "berat badan minimum swamedikasi (kg)", "string"),
    ("aksiBawahBatas", "aksi bila di bawah batas umur/BB", "string"),
    ("frekuensiMinum", "frekuensi minum", "string"),
    ("waktuMinumTeks", "waktu minum obat", "string"),
    ("kodeHubunganMakan", "kode hubungan dengan makan", "string"),
    ("maksHariSwamedikasi", "maksimal hari swamedikasi", "string"),
    ("maksDosisHarian", "maksimal dosis harian dewasa", "string"),
    ("peringatanKhusus", "peringatan khusus zat", "string"),
    ("pantanganMakanan", "pantangan makanan dan minuman", "string"),
    ("golonganAlergen", "golongan alergen", "string"),
    ("pemicuAlergiSilang", "pemicu alergi silang (cross-reactivity)", "string"),
    ("gejalaAlergi", "gejala alergi yang perlu diwaspadai", "string"),
    ("kutipanSumberAlergi", "kutipan label OpenFDA/PIONAS alergi", "string"),
    ("urlSumberAlergi", "URL sumber alergi", "string"),
    ("tingkatBukti", "tingkat bukti klinis", "string"),
    ("statusDataInteraksi", "status data interaksi", "string"),
    ("sumberPustaka", "sumber pustaka", "string"),
    ("urlSumber", "URL sumber bukti", "string"),
    ("kutipanBukti", "kutipan bukti", "string"),
    ("batasBukti", "batas bukti klinis", "string"),
    ("mekanismeKlinis", "mekanisme interaksi", "string"),
    ("efekKlinis", "efek klinis interaksi", "string"),
    ("rekomendasiKlinis", "rekomendasi klinis", "string"),
    ("deskripsiAwam", "deskripsi gejala bahasa awam", "string"),
    ("batasHariGejala", "batas hari swamedikasi gejala", "integer"),
    ("alasanRujukGejala", "alasan rujuk bila lewat batas hari", "string"),
    ("umurPasienTahun", "umur pasien dalam tahun", "decimal"),
    ("durasiGejalaHari", "durasi gejala pasien dalam hari", "integer"),
]
for lname, lbl, xsd_local in data_props:
    w(f'  <owl:DatatypeProperty rdf:about="{iri(lname)}">')
    w(f'    <rdfs:label xml:lang="id">{lbl}</rdfs:label>')
    w(f'    <rdfs:range rdf:resource="{XSD}{xsd_local}"/>')
    w("  </owl:DatatypeProperty>")
w("")

# --- TBox Classes ---
cls_hier = [
    ("ProduktObat", "Produk Obat", None),
    ("ObatBatukPilek", "Obat Batuk dan/atau Pilek", "ProduktObat"),
    ("ObatBatukMurni", "Obat Batuk Murni", "ObatBatukPilek"),
    ("ObatPilekMurni", "Obat Pilek Murni", "ObatBatukPilek"),
    ("ObatKombinasiBatukPilek", "Obat Kombinasi Batuk dan Pilek", "ObatBatukPilek"),
    ("ProdukHerbal", "Produk Herbal / Jamu", "ProduktObat"),
    ("ZatAktif", "Zat Aktif Farmakologis", None),
    ("KelasTerapiATC4", "Kelas Terapi ATC Level-4", None),
    ("EnzimCYP450", "Enzim CYP450 Metabolisme", None),
    ("Gejala", "Gejala Klinis", None),
    ("GejalaIndikasi", "Gejala Indikasi", "Gejala"),
    ("GejalaEfekSamping", "Gejala Efek Samping", "Gejala"),
    ("GejalaRedFlag", "Gejala Red Flag", "Gejala"),
    ("InteraksiObat", "Interaksi Obat", None),
    ("InteraksiMajor", "Interaksi Major (Kontraindikasi Klinis)", "InteraksiObat"),
    ("InteraksiModerate", "Interaksi Moderate (Perlu Pemantauan Klinis)", "InteraksiObat"),
    ("InteraksiMinor", "Interaksi Minor (Risiko Klinis Rendah)", "InteraksiObat"),
    ("InteraksiUnknown", "Interaksi Tidak Diketahui (Belum Diteliti — Tanya Apoteker)", "InteraksiObat"),
    ("SumberBukti", "Sumber Bukti Klinis", None),
    ("TindakLanjut", "Tindak Lanjut Klinis", None),
    ("SegeraKeDokter", "Segera ke Dokter / IGD", "TindakLanjut"),
    ("TanyaApoteker", "Konsultasikan ke Apoteker", "TindakLanjut"),
    ("Pantau", "Pantau Mandiri", "TindakLanjut"),
    ("GolonganObat", "Golongan Obat BPOM", None),
    ("ObatBebas", "Obat Bebas (Lingkaran Hijau)", "GolonganObat"),
    ("ObatBebasTerbatas", "Obat Bebas Terbatas (Lingkaran Biru)", "GolonganObat"),
    ("ObatHerbalJamu", "Obat Herbal / Jamu / Fitofarmaka", "GolonganObat"),
    ("BentukSediaan", "Bentuk Sediaan", None),
    ("Sirup", "Sirup / Suspensi", "BentukSediaan"),
    ("Tablet", "Tablet / Kaplet", "BentukSediaan"),
    ("Kapsul", "Kapsul", "BentukSediaan"),
    ("Sachet", "Sachet / Serbuk", "BentukSediaan"),
    ("KondisiPasien", "Kondisi Pasien", None),
    ("DuplikasiTerapetik", "Duplikasi Terapetik", None),
    ("DuplikasiKandungan", "Duplikasi Kandungan Zat Aktif", "DuplikasiTerapetik"),
    ("DuplikasiKelasATC", "Duplikasi Kelas Terapi ATC-4", "DuplikasiTerapetik"),
    ("KasusPasien", "Kasus Pasien", None),
    ("ObatPasien", "Penggunaan Obat Pasien", None),
]
for lname, lbl, parent in cls_hier:
    ptag = f"{OWL_NS}Thing" if parent is None else iri(parent)
    w(f'  <owl:Class rdf:about="{iri(lname)}">')
    w(f'    <rdfs:label xml:lang="id">{lbl}</rdfs:label>')
    w(f'    <rdfs:subClassOf rdf:resource="{ptag}"/>')
    w("  </owl:Class>")

# Declare 14 KondisiPasien subclasses & individuals
for _, (klname, klbl) in KONDISI_SPEC.items():
    w(f'  <owl:Class rdf:about="{iri(klname)}">')
    w(f'    <rdfs:subClassOf rdf:resource="{iri("KondisiPasien")}"/>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(klbl)}</rdfs:label>')
    w("  </owl:Class>")
    w(f'  <owl:NamedIndividual rdf:about="{iri(klname)}">')
    w(f'    <rdf:type rdf:resource="{iri(klname)}"/>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(klbl)}</rdfs:label>')
    w("  </owl:NamedIndividual>")

# Declare 4 CYP450 Enzymes (linked to PRO IRIs)
for ename, (eiri, elbl) in CYP_ENZYMES.items():
    w(f'  <owl:Class rdf:about="{eiri}">')
    w(f'    <rdfs:subClassOf rdf:resource="{iri("EnzimCYP450")}"/>')
    w(f'    <rdfs:label xml:lang="id">{elbl}</rdfs:label>')
    w("  </owl:Class>")
    w(f'  <owl:NamedIndividual rdf:about="{eiri}">')
    w(f'    <rdf:type rdf:resource="{eiri}"/>')
    w(f'    <rdfs:label xml:lang="id">{elbl}</rdfs:label>')
    w("  </owl:NamedIndividual>")
w("")

# --- TBox GCI Rules (R-01 s.d. R-08 + ObatKombinasi + InteraksiUnknown) ---
# R-01: ObatBatukMurni
w(f'  <owl:Class rdf:about="{iri("ObatBatukMurni")}">')
w('    <owl:equivalentClass><owl:Class><owl:intersectionOf rdf:parseType="Collection">')
w(f'      <rdf:Description rdf:about="{iri("ProduktObat")}"/>')
w('      <owl:Restriction><owl:onProperty rdf:resource="' + iri("memilikiKandungan") + '"/>')
w('        <owl:someValuesFrom><owl:Class><owl:unionOf rdf:parseType="Collection">')
for cid in ("CHEBI:4480", "CHEBI:5536", "CHEBI:3180", "CHEBI:2688"):
    w(f'          <rdf:Description rdf:about="{chebi_by_id[cid]}"/>')
w("        </owl:unionOf></owl:Class></owl:someValuesFrom></owl:Restriction>")
w('      <owl:Restriction><owl:onProperty rdf:resource="' + iri("memilikiKandungan") + '"/>')
w('        <owl:allValuesFrom><owl:Class><owl:complementOf><owl:Class><owl:unionOf rdf:parseType="Collection">')
for cid in ("CHEBI:50346", "CHEBI:8093"):
    w(f'          <rdf:Description rdf:about="{chebi_by_id[cid]}"/>')
w("        </owl:unionOf></owl:Class></owl:complementOf></owl:Class></owl:allValuesFrom></owl:Restriction>")
w("    </owl:intersectionOf></owl:Class></owl:equivalentClass>")
w("  </owl:Class>")

# R-02: ObatPilekMurni
w(f'  <owl:Class rdf:about="{iri("ObatPilekMurni")}">')
w('    <owl:equivalentClass><owl:Class><owl:intersectionOf rdf:parseType="Collection">')
w(f'      <rdf:Description rdf:about="{iri("ProduktObat")}"/>')
w('      <owl:Restriction><owl:onProperty rdf:resource="' + iri("memilikiKandungan") + '"/>')
w('        <owl:someValuesFrom><owl:Class><owl:unionOf rdf:parseType="Collection">')
for cid in ("CHEBI:50346", "CHEBI:8093", "CHEBI:3587", "CHEBI:3561", "CHEBI:46195", "CHEBI:84116"):
    w(f'          <rdf:Description rdf:about="{chebi_by_id[cid]}"/>')
w("        </owl:unionOf></owl:Class></owl:someValuesFrom></owl:Restriction>")
w('      <owl:Restriction><owl:onProperty rdf:resource="' + iri("memilikiKandungan") + '"/>')
w('        <owl:allValuesFrom><owl:Class><owl:complementOf><owl:Class><owl:unionOf rdf:parseType="Collection">')
for cid in ("CHEBI:4480", "CHEBI:5536", "CHEBI:3180", "CHEBI:2688"):
    w(f'          <rdf:Description rdf:about="{chebi_by_id[cid]}"/>')
w("        </owl:unionOf></owl:Class></owl:complementOf></owl:Class></owl:allValuesFrom></owl:Restriction>")
w("    </owl:intersectionOf></owl:Class></owl:equivalentClass>")
w("  </owl:Class>")

# ObatKombinasiBatukPilek
w(f'  <owl:Class rdf:about="{iri("ObatKombinasiBatukPilek")}">')
w('    <owl:equivalentClass><owl:Class><owl:intersectionOf rdf:parseType="Collection">')
w(f'      <rdf:Description rdf:about="{iri("ProduktObat")}"/>')
w('      <owl:Restriction><owl:onProperty rdf:resource="' + iri("memilikiKandungan") + '"/>')
w('        <owl:someValuesFrom><owl:Class><owl:unionOf rdf:parseType="Collection">')
for cid in ("CHEBI:4480", "CHEBI:5536", "CHEBI:3180", "CHEBI:2688"):
    w(f'          <rdf:Description rdf:about="{chebi_by_id[cid]}"/>')
w("        </owl:unionOf></owl:Class></owl:someValuesFrom></owl:Restriction>")
w('      <owl:Restriction><owl:onProperty rdf:resource="' + iri("memilikiKandungan") + '"/>')
w('        <owl:someValuesFrom><owl:Class><owl:unionOf rdf:parseType="Collection">')
for cid in ("CHEBI:50346", "CHEBI:8093", "CHEBI:3587", "CHEBI:46195", "CHEBI:84116"):
    w(f'          <rdf:Description rdf:about="{chebi_by_id[cid]}"/>')
w("        </owl:unionOf></owl:Class></owl:someValuesFrom></owl:Restriction>")
w("    </owl:intersectionOf></owl:Class></owl:equivalentClass>")
w("  </owl:Class>")

# R-03: _AH1Product
w(f'  <owl:Class rdf:about="{iri("_AH1Product")}">')
w('    <rdfs:label xml:lang="id">Produk Antihistamin H1 Gen-1 (Sedatif)</rdfs:label>')
w('    <owl:equivalentClass><owl:Class><owl:intersectionOf rdf:parseType="Collection">')
w(f'      <rdf:Description rdf:about="{iri("ProduktObat")}"/>')
w('      <owl:Restriction><owl:onProperty rdf:resource="' + iri("memilikiKandungan") + '"/>')
w('        <owl:someValuesFrom><owl:Class><owl:unionOf rdf:parseType="Collection">')
for cid in ("CHEBI:3587", "CHEBI:4634", "CHEBI:84116", "CHEBI:51380"):
    w(f'          <rdf:Description rdf:about="{chebi_by_id[cid]}"/>')
w("        </owl:unionOf></owl:Class></owl:someValuesFrom></owl:Restriction>")
w("    </owl:intersectionOf></owl:Class></owl:equivalentClass>")
w('    <rdfs:subClassOf><owl:Restriction><owl:onProperty rdf:resource="' + iri("memilikiEfekSamping") + '"/><owl:someValuesFrom rdf:resource="' + symp_iri("0000024") + '"/></owl:Restriction></rdfs:subClassOf>')
w("  </owl:Class>")

# R-04: _DekongestanProduct
w(f'  <owl:Class rdf:about="{iri("_DekongestanProduct")}">')
w('    <rdfs:label xml:lang="id">Produk Dekongestan Oral</rdfs:label>')
w('    <owl:equivalentClass><owl:Class><owl:intersectionOf rdf:parseType="Collection">')
w(f'      <rdf:Description rdf:about="{iri("ProduktObat")}"/>')
w('      <owl:Restriction><owl:onProperty rdf:resource="' + iri("memilikiKandungan") + '"/>')
w('        <owl:someValuesFrom><owl:Class><owl:unionOf rdf:parseType="Collection">')
for cid in ("CHEBI:50346", "CHEBI:8093"):
    w(f'          <rdf:Description rdf:about="{chebi_by_id[cid]}"/>')
w("        </owl:unionOf></owl:Class></owl:someValuesFrom></owl:Restriction>")
w("    </owl:intersectionOf></owl:Class></owl:equivalentClass>")
w('    <rdfs:subClassOf><owl:Restriction><owl:onProperty rdf:resource="' + iri("memilikiEfekSamping") + '"/><owl:someValuesFrom rdf:resource="' + symp_iri("0000530") + '"/></owl:Restriction></rdfs:subClassOf>')
w("  </owl:Class>")

# R-05, R-06, InteraksiUnknown
w(f'  <owl:Class rdf:about="{iri("InteraksiMajor")}">')
w('    <rdfs:subClassOf><owl:Restriction><owl:onProperty rdf:resource="' + iri("membutuhkanTindakLanjut") + '"/><owl:someValuesFrom rdf:resource="' + iri("SegeraKeDokter") + '"/></owl:Restriction></rdfs:subClassOf>')
w("  </owl:Class>")
w(f'  <owl:Class rdf:about="{iri("InteraksiModerate")}">')
w('    <rdfs:subClassOf><owl:Restriction><owl:onProperty rdf:resource="' + iri("membutuhkanTindakLanjut") + '"/><owl:someValuesFrom><owl:Class><owl:unionOf rdf:parseType="Collection">')
w(f'      <rdf:Description rdf:about="{iri("TanyaApoteker")}"/><rdf:Description rdf:about="{iri("Pantau")}"/>')
w("    </owl:unionOf></owl:Class></owl:someValuesFrom></owl:Restriction></rdfs:subClassOf>")
w("  </owl:Class>")
w(f'  <owl:Class rdf:about="{iri("InteraksiUnknown")}">')
w('    <rdfs:subClassOf><owl:Restriction><owl:onProperty rdf:resource="' + iri("membutuhkanTindakLanjut") + '"/><owl:someValuesFrom rdf:resource="' + iri("TanyaApoteker") + '"/></owl:Restriction></rdfs:subClassOf>')
w("  </owl:Class>")

# R-07: ProdukKombinasiCTMDPH
w(f'  <owl:Class rdf:about="{iri("ProdukKombinasiCTMDPH")}">')
w('    <owl:equivalentClass><owl:Class><owl:intersectionOf rdf:parseType="Collection">')
w(f'      <rdf:Description rdf:about="{iri("ProduktObat")}"/>')
w('      <owl:Restriction><owl:onProperty rdf:resource="' + iri("memilikiKandungan") + '"/><owl:someValuesFrom rdf:resource="' + chebi_by_id["CHEBI:3587"] + '"/></owl:Restriction>')
w('      <owl:Restriction><owl:onProperty rdf:resource="' + iri("memilikiKandungan") + '"/><owl:someValuesFrom rdf:resource="' + chebi_by_id["CHEBI:4634"] + '"/></owl:Restriction>')
w("    </owl:intersectionOf></owl:Class></owl:equivalentClass>")
w(f'    <rdfs:subClassOf rdf:resource="{iri("DuplikasiTerapetik")}"/>')
w("  </owl:Class>")

# R-08: ProdukDenganPSE
w(f'  <owl:Class rdf:about="{iri("ProdukDenganPSE")}">')
w('    <owl:equivalentClass><owl:Class><owl:intersectionOf rdf:parseType="Collection">')
w(f'      <rdf:Description rdf:about="{iri("ProduktObat")}"/>')
w('      <owl:Restriction><owl:onProperty rdf:resource="' + iri("memilikiKandungan") + '"/><owl:someValuesFrom rdf:resource="' + chebi_by_id["CHEBI:50346"] + '"/></owl:Restriction>')
w("    </owl:intersectionOf></owl:Class></owl:equivalentClass>")
w('    <rdfs:subClassOf><owl:Restriction><owl:onProperty rdf:resource="' + iri("kontraindikasiBagi") + '"/><owl:someValuesFrom rdf:resource="' + iri("HipertensiTidakTerkontrol") + '"/></owl:Restriction></rdfs:subClassOf>')
w("  </owl:Class>")

# O (Nominal): TindakLanjut = {SegeraKeDokter, TanyaApoteker, Pantau}
w(f'  <owl:Class rdf:about="{iri("TindakLanjut")}">')
w('    <owl:equivalentClass><owl:Class><owl:oneOf rdf:parseType="Collection">')
for tl in ("SegeraKeDokter", "TanyaApoteker", "Pantau"):
    w(f'      <rdf:Description rdf:about="{iri(tl)}"/>')
w("    </owl:oneOf></owl:Class></owl:equivalentClass>")
w("  </owl:Class>")

# Q (Qualified Cardinality): KasusPolifarmasi = KasusPasien & (>= 2 memilikiObatPasien ObatPasien)
w(f'  <owl:Class rdf:about="{iri("KasusPolifarmasi")}">')
w('    <rdfs:label xml:lang="id">Kasus Pasien Polifarmasi (&gt;= 2 Obat)</rdfs:label>')
w(f'    <rdfs:subClassOf rdf:resource="{iri("KasusPasien")}"/>')
w('    <owl:equivalentClass><owl:Class><owl:intersectionOf rdf:parseType="Collection">')
w(f'      <rdf:Description rdf:about="{iri("KasusPasien")}"/>')
w('      <owl:Restriction>')
w('        <owl:onProperty rdf:resource="' + iri("memilikiObatPasien") + '"/>')
w(f'        <owl:minQualifiedCardinality rdf:datatype="{XSD}nonNegativeInteger">2</owl:minQualifiedCardinality>')
w(f'        <owl:onClass rdf:resource="{iri("ObatPasien")}"/>')
w('      </owl:Restriction>')
w("    </owl:intersectionOf></owl:Class></owl:equivalentClass>")
w("  </owl:Class>")
w("")

# --- Dynamic ABox 1: ATC Level-4 Classes (used by our 31 substances) ---
used_atc4 = set()
for r in zat_rows:
    code = r["kode_atc"].strip()
    if len(code) >= 5:
        used_atc4.add(code[:5])
for a4 in sorted(used_atc4):
    aname = atc_rows.get(a4, f"ATC-4 {a4}")
    w(f'  <owl:NamedIndividual rdf:about="{iri("atc4_" + a4)}">')
    w(f'    <rdf:type rdf:resource="{iri("KelasTerapiATC4")}"/>')
    w(f'    <kbr:kodeATC4>{xml_safe(a4)}</kbr:kodeATC4>')
    w(f'    <rdfs:label xml:lang="en">{xml_safe(aname)}</rdfs:label>')
    w("  </owl:NamedIndividual>")
w("")

# --- Dynamic ABox 2: 31 ZatAktif + CYP450 + ATC4 + Aturan Pakai + Kontraindikasi + Alergi ---
enzyme_link_count = 0
kontra_link_count = 0
for r in zat_rows:
    zid = r["id_zat"].strip()
    z_iri = r["chebi_iri"].strip()
    code_atc = r["kode_atc"].strip()
    atc4 = code_atc[:5] if len(code_atc) >= 5 else ""
    at = aturan_map.get(zid, {})
    kt = kontra_map.get(zid, {})
    al = alergi_map.get(zid, {})

    w(f'  <owl:Class rdf:about="{z_iri}">')
    w(f'    <rdfs:subClassOf rdf:resource="{iri("ZatAktif")}"/>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(r["nama_zat"])}</rdfs:label>')
    w("  </owl:Class>")

    w(f'  <owl:NamedIndividual rdf:about="{z_iri}">')
    w(f'    <rdf:type rdf:resource="{iri("ZatAktif")}"/>')
    w(f'    <rdf:type rdf:resource="{z_iri}"/>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(r["nama_zat"])}</rdfs:label>')
    w(f'    <kbr:kodeATC>{xml_safe(code_atc)}</kbr:kodeATC>')
    w(f'    <kbr:chebiID>{xml_safe(r["chebi_id"])}</kbr:chebiID>')
    if atc4 and atc4 in used_atc4:
        w(f'    <kbr:kodeATC4>{xml_safe(atc4)}</kbr:kodeATC4>')
        w(f'    <kbr:memilikiKelasATC4 rdf:resource="{iri("atc4_" + atc4)}"/>')

    # Link CYP450 enzymes dynamically from enzim_terkait!
    enz_txt = (r.get("enzim_terkait") or "").upper()
    for ename, (eiri, _) in CYP_ENZYMES.items():
        if ename in enz_txt:
            w(f'    <kbr:dimetabolismeOleh rdf:resource="{eiri}"/>')
            enzyme_link_count += 1

    # Link pharmacological indications (propagated to ProduktObat via property chain!)
    for s_iri in infer_zat_indications(r.get("peran_farmakologis", "")):
        w(f'    <kbr:mengindikasikanGejalaZat rdf:resource="{s_iri}"/>')

    # Link kontraindikasi & perluHatiHati at ZatAktif level (propagated to ProduktObat via property chain!)
    for col, (klname, _) in KONDISI_SPEC.items():
        val = (kt.get(col) or "").strip()
        if val == "Kontraindikasi":
            w(f'    <kbr:kontraindikasiBagi rdf:resource="{iri(klname)}"/>')
            kontra_link_count += 1
        elif val == "PerluHatiHati_TanyaDokter":
            w(f'    <kbr:perluHatiHatiBagi rdf:resource="{iri(klname)}"/>')

    # Data properties: Aturan Pakai, Waktu Minum, Umur, BB
    if at:
        for prop, col in [
            ("dosisDewasa", "dosis_dewasa"),
            ("dosisAnak", "dosis_anak"),
            ("dosisMgPerKg", "dosis_mg_per_kg"),
            ("usiaMinSwamedikasi", "usia_min_swamedikasi_tahun"),
            ("bbMinSwamedikasi", "bb_min_swamedikasi_kg"),
            ("aksiBawahBatas", "aksi_jika_bawah_batas"),
            ("frekuensiMinum", "frekuensi"),
            ("waktuMinumTeks", "waktu_minum_teks"),
            ("kodeHubunganMakan", "kode_hubungan_makan"),
            ("maksHariSwamedikasi", "maks_hari_swamedikasi"),
            ("maksDosisHarian", "maks_dosis_harian_dewasa"),
            ("peringatanKhusus", "peringatan_khusus"),
        ]:
            if at.get(col):
                w(f'    <kbr:{prop}>{xml_safe(at[col])}</kbr:{prop}>')
    if kt.get("pantangan_makanan_minuman"):
        w(f'    <kbr:pantanganMakanan>{xml_safe(kt["pantangan_makanan_minuman"])}</kbr:pantanganMakanan>')
    if al:
        for prop, col in [
            ("golonganAlergen", "golongan_alergen"),
            ("pemicuAlergiSilang", "pemicu_alergi_silang"),
            ("gejalaAlergi", "gejala_alergi_waspada"),
            ("kutipanSumberAlergi", "kutipan_fda_atau_label"),
            ("urlSumberAlergi", "url_sumber"),
        ]:
            if al.get(col):
                w(f'    <kbr:{prop}>{xml_safe(al[col])}</kbr:{prop}>')
    w("  </owl:NamedIndividual>")

# Disjointness across all 31 ZatAktif classes (essential for R-01/R-02 under OWA!)
w("  <owl:AllDisjointClasses>")
w('    <owl:members rdf:parseType="Collection">')
for r in zat_rows:
    w(f'      <rdf:Description rdf:about="{r["chebi_iri"].strip()}"/>')
w("    </owl:members>")
w("  </owl:AllDisjointClasses>")
w("")

# --- Dynamic ABox 3: 22 Gejala + Batas Durasi ---
for r in symp_rows:
    oid = r["obo_id"].strip()
    s_iri = r["iri"].strip()
    kat = r["kategori"].strip()
    dur = durasi_map.get(oid, {})

    w(f'  <owl:Class rdf:about="{s_iri}">')
    w(f'    <rdfs:subClassOf rdf:resource="{iri(kat)}"/>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(r["label_id"])}</rdfs:label>')
    w(f'    <rdfs:label xml:lang="en">{xml_safe(r["label_en"])}</rdfs:label>')
    w("  </owl:Class>")
    w(f'  <owl:NamedIndividual rdf:about="{s_iri}">')
    w(f'    <rdf:type rdf:resource="{iri(kat)}"/>')
    w(f'    <rdf:type rdf:resource="{s_iri}"/>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(r["label_id"])}</rdfs:label>')
    w(f'    <rdfs:label xml:lang="en">{xml_safe(r["label_en"])}</rdfs:label>')
    w(f'    <skos:altLabel xml:lang="id">{xml_safe(r["label_id"])}</skos:altLabel>')
    w(f'    <kbr:deskripsiAwam>{xml_safe(r["deskripsi"])}</kbr:deskripsiAwam>')
    if dur:
        w(f'    <kbr:batasHariGejala rdf:datatype="{XSD}integer">{int(dur["batas_hari_swamedikasi"])}</kbr:batasHariGejala>')
        w(f'    <kbr:alasanRujukGejala>{xml_safe(dur["alasan_rujuk"])}</kbr:alasanRujukGejala>')
        w(f'    <kbr:membutuhkanTindakLanjut rdf:resource="{iri(dur["tindak_lanjut_jika_lewat_batas"])}"/>')
    w("  </owl:NamedIndividual>")
w("")

# --- Dynamic ABox 4: SumberBukti (21 records) ---
ev_by_int = {}
for ev in evidence_rows:
    eid = f'bukti_{ev["id_bukti"].strip().replace("-", "_")}'
    iid = ev["id_interaksi"].strip()
    ev_by_int.setdefault(iid, []).append(eid)
    w(f'  <owl:NamedIndividual rdf:about="{iri(eid)}">')
    w(f'    <rdf:type rdf:resource="{iri("SumberBukti")}"/>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(ev["nama_sumber"])}</rdfs:label>')
    w(f'    <kbr:urlSumber>{xml_safe(ev["url_sumber"])}</kbr:urlSumber>')
    w(f'    <kbr:kutipanBukti>{xml_safe(ev["kutipan"])}</kbr:kutipanBukti>')
    w(f'    <kbr:batasBukti>{xml_safe(ev["batas_bukti"])}</kbr:batasBukti>')
    w("  </owl:NamedIndividual>")
w("")

# --- Dynamic ABox 5: 20 Curated Interactions + DDInter Domain Pairs (including Unknown!) ---
curated_pair_keys = set()
for r in sheet2_rows:
    iid = r["id"].strip()
    int_iri = iri(f"int_{iid}")
    sev = r["tingkat_keparahan"].strip()
    sev_cls = f"Interaksi{sev}"
    za = chebi_by_id[r["chebi_a"].strip()]
    zb = chebi_by_id[r["chebi_b"].strip()]
    curated_pair_keys.add(tuple(sorted([za, zb])))
    lbl = f'{r["zat_a"]} + {r["zat_b"]} ({sev})'

    w(f'  <owl:NamedIndividual rdf:about="{int_iri}">')
    w(f'    <rdf:type rdf:resource="{iri(sev_cls)}"/>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(lbl)}</rdfs:label>')
    w(f'    <kbr:melibatkanZatAktif rdf:resource="{za}"/>')
    w(f'    <kbr:melibatkanZatAktif rdf:resource="{zb}"/>')
    w(f'    <kbr:membutuhkanTindakLanjut rdf:resource="{iri(r["tindak_lanjut"].strip())}"/>')
    w(f'    <kbr:tingkatBukti>{xml_safe(r["tingkat_bukti"])}</kbr:tingkatBukti>')
    w('    <kbr:statusDataInteraksi>kurasi_terverifikasi</kbr:statusDataInteraksi>')
    w(f'    <kbr:sumberPustaka>{xml_safe(r["sumber"])}</kbr:sumberPustaka>')
    w(f'    <kbr:mekanismeKlinis>{xml_safe(r["mekanisme_detail"])}</kbr:mekanismeKlinis>')
    w(f'    <kbr:efekKlinis>{xml_safe(r["efek_klinis"])}</kbr:efekKlinis>')
    w(f'    <kbr:rekomendasiKlinis>{xml_safe(r["rekomendasi_klinis"])}</kbr:rekomendasiKlinis>')
    for eid in ev_by_int.get(iid, []):
        w(f'    <kbr:didukungOleh rdf:resource="{iri(eid)}"/>')
    w("  </owl:NamedIndividual>")
    w(f'  <rdf:Description rdf:about="{za}">')
    w(f'    <kbr:memilikiInteraksiDengan rdf:resource="{zb}"/>')
    w(f'    <kbr:menghasilkanInteraksi rdf:resource="{int_iri}"/>')
    w("  </rdf:Description>")

ddinter_added = 0
for idx, r in enumerate(ddinter_rows, 1):
    if r["domain_batuk_pilek_x_kronis"] != "ya":
        continue
    za = chebi_by_zat[r["id_zat_a"].strip()]
    zb = chebi_by_zat[r["id_zat_b"].strip()]
    if tuple(sorted([za, zb])) in curated_pair_keys:
        continue
    lvl = r["level_ddinter"].strip()
    sev_cls = f"Interaksi{lvl}" if lvl in ("Major", "Moderate", "Minor", "Unknown") else "InteraksiUnknown"
    tl = "SegeraKeDokter" if lvl == "Major" else "TanyaApoteker"
    int_iri = iri(f"int_DDINTER_{idx:03d}")
    lbl = f'{r["nama_zat_a"]} + {r["nama_zat_b"]} (DDInter: {lvl})'
    ddinter_added += 1

    w(f'  <owl:NamedIndividual rdf:about="{int_iri}">')
    w(f'    <rdf:type rdf:resource="{iri(sev_cls)}"/>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(lbl)}</rdfs:label>')
    w(f'    <kbr:melibatkanZatAktif rdf:resource="{za}"/>')
    w(f'    <kbr:melibatkanZatAktif rdf:resource="{zb}"/>')
    w(f'    <kbr:membutuhkanTindakLanjut rdf:resource="{iri(tl)}"/>')
    w(f'    <kbr:statusDataInteraksi>{xml_safe(r["status_data"])}</kbr:statusDataInteraksi>')
    w(f'    <kbr:sumberPustaka>DDInter 2.0 ({xml_safe(r["sumber_file"])})</kbr:sumberPustaka>')
    if lvl == "Unknown":
        w('    <kbr:rekomendasiKlinis>Status Unknown pada DDInter (belum ada klasifikasi tingkat bahaya) — jangan dianggap aman, konsultasikan ke apoteker.</kbr:rekomendasiKlinis>')
    w("  </owl:NamedIndividual>")
    w(f'  <rdf:Description rdf:about="{za}">')
    w(f'    <kbr:memilikiInteraksiDengan rdf:resource="{zb}"/>')
    w(f'    <kbr:menghasilkanInteraksi rdf:resource="{int_iri}"/>')
    w("  </rdf:Description>")
w("")

# --- Dynamic ABox 6: Produk Apotek (from CSVs + harga_per_unit.csv, NO hardcoded classes!) ---
slug_to_pid = {}
for r, matched_iris in parsed_products:
    slug = r["slug"].strip()
    pid = slug_to_id(slug)
    slug_to_pid[slug] = pid
    gol = map_golongan(r.get("golongan", ""))
    sed = map_sediaan(r.get("nama", ""), r.get("kemasan", ""))
    hrec = harga_map.get(slug, {})

    w(f'  <owl:NamedIndividual rdf:about="{iri(pid)}">')
    w(f'    <rdf:type rdf:resource="{iri("ProduktObat")}"/>')
    # Closure axiom on memilikiKandungan so HermiT infers R-01/R-02 accurately
    w('    <rdf:type><owl:Restriction><owl:onProperty rdf:resource="' + iri("memilikiKandungan") + '"/>')
    if len(matched_iris) == 1:
        w(f'      <owl:allValuesFrom rdf:resource="{matched_iris[0]}"/>')
    else:
        w('      <owl:allValuesFrom><owl:Class><owl:unionOf rdf:parseType="Collection">')
        for z_iri in matched_iris:
            w(f'        <rdf:Description rdf:about="{z_iri}"/>')
        w("      </owl:unionOf></owl:Class></owl:allValuesFrom>")
    w("    </owl:Restriction></rdf:type>")

    for z_iri in matched_iris:
        w(f'    <kbr:memilikiKandungan rdf:resource="{z_iri}"/>')
    w(f'    <kbr:memilikiGolongan rdf:resource="{iri(gol)}"/>')
    w(f'    <kbr:memilikiBentukSediaan rdf:resource="{iri(sed)}"/>')
    w(f'    <kbr:namaDagang>{xml_safe(r["nama"])}</kbr:namaDagang>')
    if r.get("pabrik"):
        w(f'    <kbr:namaProdusen>{xml_safe(r["pabrik"])}</kbr:namaProdusen>')
    if r.get("nie_bpom"):
        w(f'    <kbr:nomorBPOM>{xml_safe(r["nie_bpom"])}</kbr:nomorBPOM>')
    harga_str = (r.get("harga_rp") or "").strip()
    if harga_str.isdigit() and int(harga_str) > 0:
        w(f'    <kbr:hargaRupiah rdf:datatype="{XSD}integer">{int(harga_str)}</kbr:hargaRupiah>')
    if hrec.get("harga_per_unit_rp"):
        w(f'    <kbr:hargaPerUnitRp rdf:datatype="{XSD}decimal">{hrec["harga_per_unit_rp"]}</kbr:hargaPerUnitRp>')
    if hrec.get("jumlah_unit"):
        w(f'    <kbr:jumlahUnitKemasan rdf:datatype="{XSD}decimal">{hrec["jumlah_unit"]}</kbr:jumlahUnitKemasan>')
    if hrec.get("satuan_unit"):
        w(f'    <kbr:satuanUnit>{xml_safe(hrec["satuan_unit"])}</kbr:satuanUnit>')
    if hrec.get("status_parsing"):
        w(f'    <kbr:statusParsingHarga>{xml_safe(hrec["status_parsing"])}</kbr:statusParsingHarga>')
    if r.get("kemasan"):
        w(f'    <kbr:kemasanTeks>{xml_safe(r["kemasan"])}</kbr:kemasanTeks>')
    w(f'    <kbr:komposisiTeks>{xml_safe(r["komposisi"])}</kbr:komposisiTeks>')
    w(f'    <kbr:nomorSlugK24>{xml_safe(slug)}</kbr:nomorSlugK24>')
    if r.get("url"):
        w(f'    <kbr:urlK24 rdf:datatype="{XSD}anyURI">{xml_safe(r["url"])}</kbr:urlK24>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(r["nama"])}</rdfs:label>')
    w("  </owl:NamedIndividual>")

# --- Dynamic ABox 7: Produk Herbal (sheet5_produk_herbal.csv) ---
for h in herbal_rows:
    hid = f'prod_{h["id_produk_herbal"].strip().replace("-", "_")}'
    w(f'  <owl:NamedIndividual rdf:about="{iri(hid)}">')
    w(f'    <rdf:type rdf:resource="{iri("ProdukHerbal")}"/>')
    w(f'    <kbr:memilikiKandungan rdf:resource="{chebi_by_id["CHEBI:67547"]}"/>')
    w(f'    <kbr:memilikiGolongan rdf:resource="{iri("ObatHerbalJamu")}"/>')
    w(f'    <kbr:memilikiBentukSediaan rdf:resource="{iri("Kapsul")}"/>')
    w(f'    <kbr:namaDagang>{xml_safe(h["nama_produk"])}</kbr:namaDagang>')
    w(f'    <kbr:namaProdusen>{xml_safe(h["pendaftar_bpom"])}</kbr:namaProdusen>')
    w(f'    <kbr:nomorBPOM>{xml_safe(h["nomor_izin_edar"])}</kbr:nomorBPOM>')
    w(f'    <kbr:komposisiTeks>{xml_safe(h["komposisi_per_kapsul"])}</kbr:komposisiTeks>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(h["nama_produk"])}</rdfs:label>')
    w("  </owl:NamedIndividual>")
w("")

# --- Reference Individuals ---
for lname, lbl in [
    ("SegeraKeDokter", "Segera ke Dokter / IGD"),
    ("TanyaApoteker", "Konsultasikan ke Apoteker"),
    ("Pantau", "Pantau Mandiri"),
    ("ObatBebas", "Obat Bebas (Lingkaran Hijau)"),
    ("ObatBebasTerbatas", "Obat Bebas Terbatas (Lingkaran Biru)"),
    ("ObatHerbalJamu", "Obat Herbal / Jamu / Fitofarmaka"),
    ("Sirup", "Sirup / Suspensi"),
    ("Tablet", "Tablet / Kaplet"),
    ("Kapsul", "Kapsul"),
    ("Sachet", "Sachet / Serbuk"),
]:
    w(f'  <owl:NamedIndividual rdf:about="{iri(lname)}">')
    w(f'    <rdf:type rdf:resource="{iri(lname)}"/>')
    w(f'    <rdfs:label xml:lang="id">{lbl}</rdfs:label>')
    w("  </owl:NamedIndividual>")
w("")

# --- ABox 8: Fixture KasusPasien (untuk uji q4 & T3) ---
actifed_pid = slug_to_pid.get("ACTIFED-PLUS-COUGH-SUPPRESS-SYR-MERAH-60ML-275", "")
komix_pid = slug_to_pid.get("KOMIX-JERUK-NIPIS-7ML-SACH-30S-8909", "")
procold_pid = slug_to_pid.get("PROCOLD-FLU&BATUK-CAPL-6S-STRIP-24S-2072", "")
sanmol_pid = slug_to_pid.get("SANMOL-FORTE-250MG-5ML-SYR-60ML-8741", "")

if actifed_pid:
    w(f'  <owl:NamedIndividual rdf:about="{iri("kasus_ActifedDigoxin")}">')
    w(f'    <rdf:type rdf:resource="{iri("KasusPasien")}"/>')
    w('    <rdfs:label xml:lang="id">Kasus Uji 1: Actifed Plus Merah + Digoxin Rutin</rdfs:label>')
    w(f'    <kbr:memilikiObatPasien rdf:resource="{iri("obatPasien_Actifed1")}"/>')
    w(f'    <kbr:memilikiObatPasien rdf:resource="{iri("obatPasien_Digoxin1")}"/>')
    w("  </owl:NamedIndividual>")
    w(f'  <owl:NamedIndividual rdf:about="{iri("obatPasien_Actifed1")}"><rdf:type rdf:resource="{iri("ObatPasien")}"/><kbr:menggunakanProdukObat rdf:resource="{iri(actifed_pid)}"/></owl:NamedIndividual>')
    w(f'  <owl:NamedIndividual rdf:about="{iri("obatPasien_Digoxin1")}"><rdf:type rdf:resource="{iri("ObatPasien")}"/><kbr:menggunakanZatAktif rdf:resource="{chebi_by_id["CHEBI:4551"]}"/></owl:NamedIndividual>')

if procold_pid and sanmol_pid:
    w(f'  <owl:NamedIndividual rdf:about="{iri("kasus_DobelParacetamol")}">')
    w(f'    <rdf:type rdf:resource="{iri("KasusPasien")}"/>')
    w('    <rdfs:label xml:lang="id">Kasus Uji 2: Dobel Paracetamol (Procold + Sanmol)</rdfs:label>')
    w(f'    <kbr:memilikiObatPasien rdf:resource="{iri("obatPasien_Procold2")}"/>')
    w(f'    <kbr:memilikiObatPasien rdf:resource="{iri("obatPasien_Sanmol2")}"/>')
    w("  </owl:NamedIndividual>")
    w(f'  <owl:NamedIndividual rdf:about="{iri("obatPasien_Procold2")}"><rdf:type rdf:resource="{iri("ObatPasien")}"/><kbr:menggunakanProdukObat rdf:resource="{iri(procold_pid)}"/></owl:NamedIndividual>')
    w(f'  <owl:NamedIndividual rdf:about="{iri("obatPasien_Sanmol2")}"><rdf:type rdf:resource="{iri("ObatPasien")}"/><kbr:menggunakanProdukObat rdf:resource="{iri(sanmol_pid)}"/></owl:NamedIndividual>')

if komix_pid and actifed_pid:
    w(f'  <owl:NamedIndividual rdf:about="{iri("kasus_KomixActifed")}">')
    w(f'    <rdf:type rdf:resource="{iri("KasusPasien")}"/>')
    w('    <rdfs:label xml:lang="id">Kasus Uji 3: Komix + Actifed (Dobel DXM &amp; Dobel Antihistamin)</rdfs:label>')
    w(f'    <kbr:memilikiObatPasien rdf:resource="{iri("obatPasien_Komix3")}"/>')
    w(f'    <kbr:memilikiObatPasien rdf:resource="{iri("obatPasien_Actifed3")}"/>')
    w("  </owl:NamedIndividual>")
    w(f'  <owl:NamedIndividual rdf:about="{iri("obatPasien_Komix3")}"><rdf:type rdf:resource="{iri("ObatPasien")}"/><kbr:menggunakanProdukObat rdf:resource="{iri(komix_pid)}"/></owl:NamedIndividual>')
    w(f'  <owl:NamedIndividual rdf:about="{iri("obatPasien_Actifed3")}"><rdf:type rdf:resource="{iri("ObatPasien")}"/><kbr:menggunakanProdukObat rdf:resource="{iri(actifed_pid)}"/></owl:NamedIndividual>')

# Explicit owl:AllDifferent for ObatPasien fixtures so SWRL DifferentIndividualsAtom fires under OWA
w("  <owl:AllDifferent>")
w('    <owl:distinctMembers rdf:parseType="Collection">')
for op_name in ["obatPasien_Actifed1", "obatPasien_Digoxin1", "obatPasien_Procold2", "obatPasien_Sanmol2", "obatPasien_Komix3", "obatPasien_Actifed3"]:
    w(f'      <rdf:Description rdf:about="{iri(op_name)}"/>')
w("    </owl:distinctMembers>")
w("  </owl:AllDifferent>")
w("")

# --- ABox 9: SWRL Rules (swrl:Imp) untuk Protege Rules Tab & Reasoner HermiT ---
swrl_vars = ["p", "z", "z1", "z2", "k", "op", "op1", "op2", "p1", "p2", "kond", "g", "int", "atc", "u"]
for v in swrl_vars:
    w(f'  <swrl:Variable rdf:about="{iri("var_" + v)}"/>')


def swrl_class_atom(cls_iri: str, var_name: str) -> str:
    return (
        f'<swrl:ClassAtom><swrl:classPredicate rdf:resource="{cls_iri}"/>'
        f'<swrl:argument1 rdf:resource="{iri("var_" + var_name)}"/></swrl:ClassAtom>'
    )


def swrl_obj_atom(prop_iri: str, var1: str, var2_is_var: bool, var2_val: str) -> str:
    arg2 = iri("var_" + var2_val) if var2_is_var else var2_val
    return (
        f'<swrl:IndividualPropertyAtom><swrl:propertyPredicate rdf:resource="{prop_iri}"/>'
        f'<swrl:argument1 rdf:resource="{iri("var_" + var1)}"/>'
        f'<swrl:argument2 rdf:resource="{arg2}"/></swrl:IndividualPropertyAtom>'
    )


def swrl_data_atom(prop_iri: str, var1: str, var2: str) -> str:
    return (
        f'<swrl:DatavaluedPropertyAtom><swrl:propertyPredicate rdf:resource="{prop_iri}"/>'
        f'<swrl:argument1 rdf:resource="{iri("var_" + var1)}"/>'
        f'<swrl:argument2 rdf:resource="{iri("var_" + var2)}"/></swrl:DatavaluedPropertyAtom>'
    )


def swrl_diff_atom(var1: str, var2: str) -> str:
    return (
        f'<swrl:DifferentIndividualsAtom>'
        f'<swrl:argument1 rdf:resource="{iri("var_" + var1)}"/>'
        f'<swrl:argument2 rdf:resource="{iri("var_" + var2)}"/></swrl:DifferentIndividualsAtom>'
    )


def swrl_builtin_lt(var_name: str, val_int: int) -> str:
    return (
        f'<swrl:BuiltinAtom><swrl:builtin rdf:resource="{SWRLB}lessThan"/>'
        f'<swrl:arguments><rdf:List>'
        f'<rdf:first rdf:resource="{iri("var_" + var_name)}"/>'
        f'<rdf:rest><rdf:List>'
        f'<rdf:first rdf:datatype="{XSD}integer">{val_int}</rdf:first>'
        f'<rdf:rest rdf:resource="{RDF_NS}nil"/>'
        f'</rdf:List></rdf:rest>'
        f'</rdf:List></swrl:arguments></swrl:BuiltinAtom>'
    )


def emit_swrl_rule(rule_id: str, label: str, comment: str, body_atoms: list[str], head_atoms: list[str]):
    w(f'  <swrl:Imp rdf:about="{iri(rule_id)}">')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(label)}</rdfs:label>')
    w(f'    <rdfs:comment xml:lang="id">{xml_safe(comment)}</rdfs:comment>')
    w('    <swrl:body><swrl:AtomList>')
    for i, atom in enumerate(body_atoms):
        w('      <rdf:first>' + atom + '</rdf:first>')
        if i < len(body_atoms) - 1:
            w('      <rdf:rest><swrl:AtomList>')
        else:
            w(f'      <rdf:rest rdf:resource="{RDF_NS}nil"/>')
    for _ in range(len(body_atoms) - 1):
        w('      </swrl:AtomList></rdf:rest>')
    w('    </swrl:AtomList></swrl:body>')
    w('    <swrl:head><swrl:AtomList>')
    for i, atom in enumerate(head_atoms):
        w('      <rdf:first>' + atom + '</rdf:first>')
        if i < len(head_atoms) - 1:
            w('      <rdf:rest><swrl:AtomList>')
        else:
            w(f'      <rdf:rest rdf:resource="{RDF_NS}nil"/>')
    for _ in range(len(head_atoms) - 1):
        w('      </swrl:AtomList></rdf:rest>')
    w('    </swrl:AtomList></swrl:head>')
    w('  </swrl:Imp>')


# 11 fast DL-safe SWRL rules (modularized to avoid combinatorial explosion in HermiT)
emit_swrl_rule(
    "SWRL_R01_EfekSampingAH1",
    "SWRL-R01: Produk Antihistamin H1 Gen-1 -> Efek Samping Mengantuk",
    "_AH1Product(?p) -> memilikiEfekSamping(?p, SYMP_0000024)",
    [swrl_class_atom(iri("_AH1Product"), "p")],
    [swrl_obj_atom(iri("memilikiEfekSamping"), "p", False, symp_iri("0000024"))],
)
emit_swrl_rule(
    "SWRL_R02_EfekSampingDekongestan",
    "SWRL-R02: Produk Dekongestan Oral -> Efek Samping Palpitasi",
    "_DekongestanProduct(?p) -> memilikiEfekSamping(?p, SYMP_0000530)",
    [swrl_class_atom(iri("_DekongestanProduct"), "p")],
    [swrl_obj_atom(iri("memilikiEfekSamping"), "p", False, symp_iri("0000530"))],
)
emit_swrl_rule(
    "SWRL_R03_KontraindikasiPSEHipertensi",
    "SWRL-R03: Produk Mengandung Pseudoephedrine -> Kontraindikasi Hipertensi",
    "ProdukDenganPSE(?p) -> kontraindikasiBagi(?p, HipertensiTidakTerkontrol)",
    [swrl_class_atom(iri("ProdukDenganPSE"), "p")],
    [swrl_obj_atom(iri("kontraindikasiBagi"), "p", False, iri("HipertensiTidakTerkontrol"))],
)
emit_swrl_rule(
    "SWRL_R04_TindakLanjutMajor",
    "SWRL-R04: Interaksi Major -> SegeraKeDokter",
    "InteraksiMajor(?int) -> membutuhkanTindakLanjut(?int, SegeraKeDokter)",
    [swrl_class_atom(iri("InteraksiMajor"), "int")],
    [swrl_obj_atom(iri("membutuhkanTindakLanjut"), "int", False, iri("SegeraKeDokter"))],
)
emit_swrl_rule(
    "SWRL_R05_TindakLanjutModerate",
    "SWRL-R05: Interaksi Moderate -> TanyaApoteker",
    "InteraksiModerate(?int) -> membutuhkanTindakLanjut(?int, TanyaApoteker)",
    [swrl_class_atom(iri("InteraksiModerate"), "int")],
    [swrl_obj_atom(iri("membutuhkanTindakLanjut"), "int", False, iri("TanyaApoteker"))],
)
emit_swrl_rule(
    "SWRL_R06_TindakLanjutUnknown",
    "SWRL-R06: Interaksi Unknown -> TanyaApoteker (Jangan Diklaim Aman)",
    "InteraksiUnknown(?int) -> membutuhkanTindakLanjut(?int, TanyaApoteker)",
    [swrl_class_atom(iri("InteraksiUnknown"), "int")],
    [swrl_obj_atom(iri("membutuhkanTindakLanjut"), "int", False, iri("TanyaApoteker"))],
)
emit_swrl_rule(
    "SWRL_R07_EkstrakZatObatPasien",
    "SWRL-R07: Propagasi Zat Aktif dari Produk Obat ke ObatPasien",
    "ObatPasien(?op) ^ menggunakanProdukObat(?op, ?p) ^ memilikiKandungan(?p, ?z) -> menggunakanZatAktif(?op, ?z)",
    [
        swrl_class_atom(iri("ObatPasien"), "op"),
        swrl_obj_atom(iri("menggunakanProdukObat"), "op", True, "p"),
        swrl_obj_atom(iri("memilikiKandungan"), "p", True, "z"),
    ],
    [swrl_obj_atom(iri("menggunakanZatAktif"), "op", True, "z")],
)
emit_swrl_rule(
    "SWRL_R08_DuplikasiKandungan",
    "SWRL-R08: Deteksi Duplikasi Zat Aktif pada Keranjang KasusPasien",
    "KasusPasien(?k) ^ memilikiObatPasien(?k, ?op1) ^ memilikiObatPasien(?k, ?op2) ^ DifferentFrom(?op1, ?op2) ^ menggunakanZatAktif(?op1, ?z) ^ menggunakanZatAktif(?op2, ?z) -> DuplikasiKandungan(?k)",
    [
        swrl_class_atom(iri("KasusPasien"), "k"),
        swrl_obj_atom(iri("memilikiObatPasien"), "k", True, "op1"),
        swrl_obj_atom(iri("memilikiObatPasien"), "k", True, "op2"),
        swrl_diff_atom("op1", "op2"),
        swrl_obj_atom(iri("menggunakanZatAktif"), "op1", True, "z"),
        swrl_obj_atom(iri("menggunakanZatAktif"), "op2", True, "z"),
    ],
    [swrl_class_atom(iri("DuplikasiKandungan"), "k")],
)
emit_swrl_rule(
    "SWRL_R09_KasusActifedDigoxin",
    "SWRL-R09: KasusPasien dengan ObatPasien ber-Pseudoephedrine dan Digoxin -> TanyaApoteker",
    "KasusPasien(?k) ^ memilikiObatPasien(?k, ?op1) ^ memilikiObatPasien(?k, ?op2) ^ menggunakanZatAktif(?op1, CHEBI_50346) ^ menggunakanZatAktif(?op2, CHEBI_4551) -> membutuhkanTindakLanjut(?k, TanyaApoteker)",
    [
        swrl_class_atom(iri("KasusPasien"), "k"),
        swrl_obj_atom(iri("memilikiObatPasien"), "k", True, "op1"),
        swrl_obj_atom(iri("memilikiObatPasien"), "k", True, "op2"),
        swrl_obj_atom(iri("menggunakanZatAktif"), "op1", False, chebi_by_id["CHEBI:50346"]),
        swrl_obj_atom(iri("menggunakanZatAktif"), "op2", False, chebi_by_id["CHEBI:4551"]),
    ],
    [swrl_obj_atom(iri("membutuhkanTindakLanjut"), "k", False, iri("TanyaApoteker"))],
)
emit_swrl_rule(
    "SWRL_R10_DuplikasiParacetamol",
    "SWRL-R10: KasusPasien dengan 2 ObatPasien berbeda mengandung Paracetamol -> DuplikasiKandungan",
    "KasusPasien(?k) ^ memilikiObatPasien(?k, ?op1) ^ memilikiObatPasien(?k, ?op2) ^ DifferentFrom(?op1, ?op2) ^ menggunakanZatAktif(?op1, CHEBI_46195) ^ menggunakanZatAktif(?op2, CHEBI_46195) -> DuplikasiKandungan(?k)",
    [
        swrl_class_atom(iri("KasusPasien"), "k"),
        swrl_obj_atom(iri("memilikiObatPasien"), "k", True, "op1"),
        swrl_obj_atom(iri("memilikiObatPasien"), "k", True, "op2"),
        swrl_diff_atom("op1", "op2"),
        swrl_obj_atom(iri("menggunakanZatAktif"), "op1", False, chebi_by_id["CHEBI:46195"]),
        swrl_obj_atom(iri("menggunakanZatAktif"), "op2", False, chebi_by_id["CHEBI:46195"]),
    ],
    [swrl_class_atom(iri("DuplikasiKandungan"), "k")],
)
emit_swrl_rule(
    "SWRL_R11_KontraindikasiPSEKasus",
    "SWRL-R11: KasusPasien Hipertensi menggunakan Pseudoephedrine -> SegeraKeDokter",
    "KasusPasien(?k) ^ memilikiKondisiPasien(?k, HipertensiTidakTerkontrol) ^ memilikiObatPasien(?k, ?op) ^ menggunakanZatAktif(?op, CHEBI_50346) -> membutuhkanTindakLanjut(?k, SegeraKeDokter)",
    [
        swrl_class_atom(iri("KasusPasien"), "k"),
        swrl_obj_atom(iri("memilikiKondisiPasien"), "k", False, iri("HipertensiTidakTerkontrol")),
        swrl_obj_atom(iri("memilikiObatPasien"), "k", True, "op"),
        swrl_obj_atom(iri("menggunakanZatAktif"), "op", False, chebi_by_id["CHEBI:50346"]),
    ],
    [swrl_obj_atom(iri("membutuhkanTindakLanjut"), "k", False, iri("SegeraKeDokter"))],
)

w("</rdf:RDF>")

content = "\n".join(lines)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(content)

sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
print(f"[OK] {OUT_PATH}")
print(f"     Ukuran              : {os.path.getsize(OUT_PATH):,} bytes | SHA-256: {sha256[:16]}...")
print(f"     Zat Aktif           : {len(zat_rows)} | Relasi CYP450: {enzyme_link_count} | Relasi Kontraindikasi: {kontra_link_count}")
print(f"     ATC Level-4         : {len(used_atc4)} kelas terapi")
print(f"     Gejala + Durasi     : {len(symp_rows)}")
print(f"     Interaksi Kurasi    : {len(sheet2_rows)} | Tambahan DDInter domain: {ddinter_added} | SumberBukti: {len(evidence_rows)}")
print(f"     Produk Apotek       : {len(parsed_products)} + {len(herbal_rows)} herbal")
