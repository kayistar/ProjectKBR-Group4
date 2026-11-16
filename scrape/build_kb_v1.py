"""
build_kb_v1.py
==============
Merakit kb_v1.owl: Knowledge Base Interaksi Obat Batuk-Pilek (Group 4)
Berisi TBox (kelas + properti + aturan GCI/SWRL) + ABox (12 produk apotek percontohan).

Struktur OWL:
  Ontology IRI : http://purl.obolibrary.org/obo/kbr-group4/kb_v1.owl
  Prefix lokal : :  → http://purl.obolibrary.org/obo/kbr-group4/kb_v1.owl#
  Referensi ext: imports kb_referensi_lengkap.owl (ChEBI, DrON, PRO, DINTO, SYMP)

TBox Kelas Utama (didefinisikan secara lokal):
  ProduktObat, ObatBatukPilek, ObatBatukMurni, ObatPilekMurni, ObatKombinasiBatukPilek
  ZatAktif (bridged ke ChEBI)
  Gejala (bridged ke SYMP)
  InteraksiObat (dengan sub-kelas: InteraksiMajor, InteraksiModerate, InteraksiMinor)
  TindakLanjut (SegeraKeDokter, TanyaApoteker, Pantau)
  GolonganObat (ObatBebas, ObatBebasTerbatas, ObatHerbal)
  BentukSediaan (Sirup, Tablet, Kapsul, Kaplet, Sachet)

TBox Object Properties:
  memilikiKandungan           (ProduktObat → ZatAktif)
  mengindikasikanGejala       (ProduktObat → Gejala)
  memilikiEfekSamping         (ProduktObat → Gejala)
  memilikiInteraksiDengan     (ZatAktif → ZatAktif / symetric)
  menghasilkanInteraksi       (pasangan ZatAktif → InteraksiObat)
  membutuhkanTindakLanjut     (InteraksiObat → TindakLanjut)
  dimetabolismeOleh           (ZatAktif → Enzim CYP450 via PRO)
  memilikiGolongan            (ProduktObat → GolonganObat)
  memilikiBentukSediaan       (ProduktObat → BentukSediaan)

TBox Data Properties:
  namaDagang      (string)
  namaProdusen    (string)
  nomorBPOM       (string)
  hargaRupiah     (integer)
  kodeATC         (string)
  chebiID         (string)
  doseInfo        (string)

TBox GCI Rules (R-01 s.d. R-08):
  R-01: Obat yang mengandung antitusif → ObatBatuk (atau ObatKombinasi)
  R-02: Obat yang mengandung dekongestan → ObatPilek (atau ObatKombinasi)
  R-03: Obat yang mengandung antihistamin-H1 → dapat menyebabkan Mengantuk
  R-04: Obat yang mengandung dekongestan oral → dapat menyebabkan Palpitasi
  R-05: ZatAktif yang memiliki interaksi Major → wajib SegeraKeDokter
  R-06: ZatAktif yang memiliki interaksi Moderate → wajib TanyaApoteker/Pantau
  R-07: Obat dengan bahan CTM + Diphenhydramine → terdeteksi DuplikasiTerapetik
  R-08: Obat dengan Pseudoephedrine → kontraindikasi pasien HipertensiTidakTerkontrol

ABox Individu (12 produk apotek):
  1.  Siladex Cough N Cold Syrup 100mL    (DXM + PSE + Doxylamine)
  2.  Actifed Plus Syrup Merah 60mL       (Triprolidine + PSE + DXM)
  3.  Komix Jeruk Nipis 7mL Sachet        (GG + DXM + CTM)
  4.  Vicks F44 Anak Syrup 54mL           (GG + DXM)
  5.  Procold Flu & Batuk Kaplet          (PCT + DXM + PSE)
  6.  Paramex Flu & Batuk Tablet          (PCT + PSE + DXM)
  7.  Alpara Kaplet                       (PCT + PPA + CTM + DXM)
  8.  OB Combi ATT Menthol Sirup 60mL     (DXM + Diphenhydramine)
  9.  Sanmol Forte 250mg/5mL Syrup        (Paracetamol)
  10. Triaminic Batuk Pilek Syrup 60mL    (PSE + DXM)
  11. Promedex Tablet                     (DXM + GG + CTM)
  12. Lapifed DM Syrup 100mL              (Triprolidine + PSE + DXM)
"""

import textwrap, os, datetime, hashlib

OUT_PATH = r"d:\UNS\SMT_5\KBR\PROJECT\ProjectKBR-Group4\out\kb_v1.owl"
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

BASE = "http://purl.obolibrary.org/obo/kbr-group4/kb_v1.owl#"
ONTO = "http://purl.obolibrary.org/obo/kbr-group4/kb_v1.owl"
REF_OWL = "http://purl.obolibrary.org/obo/kbr-group4/kb_referensi_lengkap.owl"
CHEBI  = "http://purl.obolibrary.org/obo/CHEBI_"
SYMP   = "http://purl.obolibrary.org/obo/SYMP_"
PRO    = "http://purl.obolibrary.org/obo/PR_"
DINTO  = "http://purl.obolibrary.org/obo/DINTO_"
OBO    = "http://www.geneontology.org/formats/oboInOwl#"
SKOS   = "http://www.w3.org/2004/02/skos/core#"
RDFS   = "http://www.w3.org/2000/01/rdf-schema#"
OWL_NS = "http://www.w3.org/2002/07/owl#"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
XSD    = "http://www.w3.org/2001/XMLSchema#"

def iri(localname):
    return f"{BASE}{localname}"

def chebi(num):
    return f"{CHEBI}{num}"

def symp(num):
    return f"{SYMP}{num}"

NOW = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat()

# ============================================================
#  BUILDER  –  tuliskan RDF/XML OWL 2 DL secara manual
# ============================================================
lines = []

def w(s):
    lines.append(s)

# --- Header XML + Ontology Declaration ---------------------------
w('<?xml version="1.0" encoding="UTF-8"?>')
w('<rdf:RDF')
w(f'    xmlns:rdf="{RDF_NS}"')
w(f'    xmlns:rdfs="{RDFS}"')
w(f'    xmlns:owl="{OWL_NS}"')
w(f'    xmlns:xsd="{XSD}"')
w(f'    xmlns:skos="{SKOS}"')
w(f'    xmlns:oboInOwl="{OBO}"')
w(f'    xmlns:kbr="{BASE}">')
w('')
w(f'  <!-- ======================================================= -->')
w(f'  <!-- Ontology: kb_v1.owl                                     -->')
w(f'  <!-- Group 4 KBR - Interaksi Obat Batuk-Pilek Indonesia      -->')
w(f'  <!-- Generated: {NOW}                       -->')
w(f'  <!-- ======================================================= -->')
w(f'  <owl:Ontology rdf:about="{ONTO}">')
w(f'    <rdfs:label xml:lang="en">KB v1 Drug Interaction Knowledge Base (Cough &amp; Cold Products - Indonesia)</rdfs:label>')
w(f'    <rdfs:label xml:lang="id">KB v1 Basis Pengetahuan Interaksi Obat Batuk-Pilek (Produk Apotek Indonesia)</rdfs:label>')
w(f'    <owl:versionIRI rdf:resource="{ONTO}/1.0"/>')
w(f'    <rdfs:comment xml:lang="id">Basis pengetahuan interaksi obat batuk-pilek generasi pertama. TBox mendefinisikan kelas produk, zat aktif, gejala, interaksi, tindak lanjut klinis, serta 8 aturan GCI inferensi. ABox mendaftarkan 12 individu produk apotek Indonesia pilihan dari data K24Klik.</rdfs:comment>')
w(f'    <oboInOwl:date>{NOW}</oboInOwl:date>')
w(f'    <oboInOwl:creator xml:lang="id">Group 4 KBR - Universitas Sebelas Maret, Semester 5, 2026/2027</oboInOwl:creator>')
w(f'  </owl:Ontology>')
w('')

# ============================================================
#  SECTION A0 – Annotation Properties Declaration (for OWL 2 DL)
# ============================================================
w(f'  <!-- ======================================================= -->')
w(f'  <!-- A0. ANNOTATION PROPERTIES                               -->')
w(f'  <!-- ======================================================= -->')
w('')

ann_props = [
    ("http://www.geneontology.org/formats/oboInOwl#date", "date"),
    ("http://www.geneontology.org/formats/oboInOwl#creator", "creator"),
    ("http://www.w3.org/2004/02/skos/core#altLabel", "altLabel"),
]
for ap_iri, ap_lbl in ann_props:
    w(f'  <owl:AnnotationProperty rdf:about="{ap_iri}">')
    w(f'    <rdfs:label>{ap_lbl}</rdfs:label>')
    w(f'  </owl:AnnotationProperty>')
    w('')

# ============================================================
#  SECTION A – Object Properties
# ============================================================
w(f'  <!-- ======================================================= -->')
w(f'  <!-- A. OBJECT PROPERTIES                                    -->')
w(f'  <!-- ======================================================= -->')
w('')

object_properties = [
    ("memilikiKandungan", "memiliki kandungan zat aktif", "has active ingredient",
     "ProduktObat", "ZatAktif", "", ""),
    ("mengindikasikanGejala", "mengindikasikan / mengatasi gejala", "indicates symptom",
     "ProduktObat", "Gejala", "", ""),
    ("memilikiEfekSamping", "memiliki efek samping yang mungkin terjadi", "has side effect symptom",
     "ProduktObat", "Gejala", "", ""),
    ("memilikiInteraksiDengan", "memiliki interaksi farmakokinetik/farmakodinamik dengan", "has drug interaction with",
     "ZatAktif", "ZatAktif", "owl:SymmetricProperty", ""),
    ("menghasilkanInteraksi", "menghasilkan / menyebabkan kejadian interaksi", "produces drug interaction event",
     "ZatAktif", "InteraksiObat", "", ""),
    ("membutuhkanTindakLanjut", "membutuhkan tindak lanjut klinis tertentu", "requires clinical follow-up",
     "InteraksiObat", "TindakLanjut", "", ""),
    ("dimetabolismeOleh", "dimetabolisme / diubah oleh enzim CYP450", "is metabolized by enzyme",
     "ZatAktif", "EnzimCYP450", "", ""),
    ("memilikiGolongan", "memiliki golongan regulasi BPOM", "has regulatory class",
     "ProduktObat", "GolonganObat", "", "owl:FunctionalProperty"),
    ("memilikiBentukSediaan", "memiliki bentuk sediaan farmasi", "has dosage form",
     "ProduktObat", "BentukSediaan", "", ""),
    ("diproduksiOleh", "diproduksi / dipasarkan oleh produsen farmasi", "is manufactured by",
     "ProduktObat", "owl:Thing", "", ""),
    ("kontraindikasiBagi", "bersifat kontraindikasi bagi kondisi pasien tertentu", "is contraindicated for patient condition",
     "ProduktObat", "KondisiPasien", "", ""),
]

for lname, label_id, label_en, domain_cls, range_cls, extra_type, extra_type2 in object_properties:
    w(f'  <owl:ObjectProperty rdf:about="{iri(lname)}">')
    w(f'    <rdfs:label xml:lang="id">{label_id}</rdfs:label>')
    w(f'    <rdfs:label xml:lang="en">{label_en}</rdfs:label>')
    if domain_cls:
        w(f'    <rdfs:domain rdf:resource="{iri(domain_cls)}"/>')
    if range_cls and not range_cls.startswith("owl:"):
        w(f'    <rdfs:range rdf:resource="{iri(range_cls)}"/>')
    elif range_cls.startswith("owl:"):
        owl_local = range_cls.split(":")[1]
        w(f'    <rdfs:range rdf:resource="{OWL_NS}{owl_local}"/>')
    if extra_type:
        tag = extra_type.replace("owl:","")
        w(f'    <rdf:type rdf:resource="{OWL_NS}{tag}"/>')
    if extra_type2:
        tag2 = extra_type2.replace("owl:","")
        w(f'    <rdf:type rdf:resource="{OWL_NS}{tag2}"/>')
    w(f'  </owl:ObjectProperty>')
    w('')

# ============================================================
#  SECTION B – Data Properties
# ============================================================
w(f'  <!-- ======================================================= -->')
w(f'  <!-- B. DATA PROPERTIES                                      -->')
w(f'  <!-- ======================================================= -->')
w('')

data_props = [
    ("namaDagang",    "nama dagang / merek produk (terdaftar BPOM)",     "trade name",           "xsd:string"),
    ("namaProdusen",  "nama perusahaan farmasi produsen/pemegang izin",  "manufacturer name",    "xsd:string"),
    ("nomorBPOM",     "nomor izin edar resmi BPOM (NIE)",                "BPOM registration no", "xsd:string"),
    ("hargaRupiah",   "harga satuan terkecil kemasan (Rupiah)",          "unit price IDR",       "xsd:integer"),
    ("kodeATC",       "kode ATC Level 5 WHO (Anatomical Therapeutic Chemical)", "ATC code",      "xsd:string"),
    ("chebiID",       "identifier ChEBI zat kimia aktif",                "ChEBI identifier",     "xsd:string"),
    ("doseInfoPer5mL","informasi dosis zat aktif per unit sediaan",      "dose info",            "xsd:string"),
    ("nomorSlugK24",  "slug/ID unik produk pada katalog K24Klik",        "K24Klik slug",         "xsd:string"),
    ("urlK24",        "URL halaman detail produk pada K24Klik",          "K24Klik product URL",  "xsd:anyURI"),
    ("tingkatBukti",  "tingkat bukti literatur interaksi (A/B/C)",       "evidence level",       "xsd:string"),
]

for lname, label_id, label_en, xsd_type in data_props:
    xsd_prefix, xsd_local = xsd_type.split(":")
    w(f'  <owl:DatatypeProperty rdf:about="{iri(lname)}">')
    w(f'    <rdfs:label xml:lang="id">{label_id}</rdfs:label>')
    w(f'    <rdfs:label xml:lang="en">{label_en}</rdfs:label>')
    w(f'    <rdfs:range rdf:resource="{XSD}{xsd_local}"/>')
    w(f'  </owl:DatatypeProperty>')
    w('')

# ============================================================
#  SECTION C – TBox: Class Hierarchy
# ============================================================
w(f'  <!-- ======================================================= -->')
w(f'  <!-- C. TBOX – CLASS HIERARCHY                               -->')
w(f'  <!-- ======================================================= -->')
w('')

#  ---------- C1. ProduktObat hierarchy ----------
cls_hier = [
    # (IRI_local, label_id, label_en, parent_local_or_full_IRI, comment_id)
    ("ProduktObat",
     "Produk Obat",
     "Pharmaceutical Product",
     None,
     "Kelas akar semua produk farmasi yang terdaftar di apotek Indonesia dan memiliki NIE BPOM."),
    ("ObatBatukPilek",
     "Obat Batuk dan/atau Pilek",
     "Cough and/or Cold Medication",
     "ProduktObat",
     "Produk farmasi yang diindikasikan untuk mengatasi gejala batuk, pilek, atau keduanya; berisi minimal satu zat aktif antitusif, ekspektoran, mukolitik, atau dekongestan."),
    ("ObatBatukMurni",
     "Obat Batuk (Murni)",
     "Cough-only Medication",
     "ObatBatukPilek",
     "Produk berindikasi khusus batuk: mengandung antitusif (Dextromethorphan, Diphenhydramine) dan/atau ekspektoran/mukolitik (Guaifenesin, Bromhexine, Ambroxol) tanpa dekongestan nasal."),
    ("ObatPilekMurni",
     "Obat Pilek / Flu (Murni)",
     "Cold/Flu-only Medication",
     "ObatBatukPilek",
     "Produk berindikasi khusus pilek/flu: mengandung dekongestan (Pseudoephedrine, Phenylephrine) dan/atau antihistamin H1 (CTM, Triprolidine) atau antipiretik, tanpa antitusif."),
    ("ObatKombinasiBatukPilek",
     "Obat Kombinasi Batuk dan Pilek",
     "Combination Cough-Cold Medication",
     "ObatBatukPilek",
     "Produk multi-komponen yang sekaligus mengandung antitusif/ekspektoran DAN dekongestan/antihistamin. Contoh: Siladex Cough N Cold, Actifed Merah, Komix, Procold."),
    ("ZatAktif",
     "Zat Aktif / Bahan Farmakologis",
     "Active Pharmaceutical Ingredient (API)",
     None,
     "Senyawa kimia atau bahan biologis yang memberikan efek farmakologis dalam suatu produk obat. Setiap individu ZatAktif terkait dengan entri ChEBI, kode ATC, dan data enzim metabolisme."),
    ("EnzimCYP450",
     "Enzim CYP450 Metabolisme",
     "CYP450 Metabolic Enzyme",
     None,
     "Enzim sitokrom P450 yang bertanggung jawab atas metabolisme hepatik obat. Terkait dengan entri PRO (Protein Ontology). Sub-kelas: CYP3A4, CYP2D6, CYP2C19, CYP2C9."),
    ("CYP3A4",   "CYP3A4 (Enzim Metabolisme Utama)", "CYP3A4 Enzyme",   "EnzimCYP450", "Isoform CYP450 paling dominan (>50% obat); major metaboliser statin, azol, amlodipine, dextromethorphan."),
    ("CYP2D6",   "CYP2D6 (Enzim Metabolisme Utama)", "CYP2D6 Enzyme",   "EnzimCYP450", "Isoform polimorfik; metaboliser utama dextromethorphan (O-demetilasi), codeine, dan antihistamin."),
    ("CYP2C19",  "CYP2C19 (Enzim Metabolisme Utama)","CYP2C19 Enzyme",  "EnzimCYP450", "Isoform polimorfik; bioaktivasi clopidogrel, metabolisme omeprazole. Dihambat oleh omeprazole → interaksi kritis."),
    ("CYP2C9",   "CYP2C9 (Enzim Metabolisme Utama)", "CYP2C9 Enzyme",   "EnzimCYP450", "Metaboliser warfarin S-enantiomer, glimepiride, ibuprofen, fluconazole. Inhibitor kuat = azol."),
    ("Gejala",
     "Gejala Klinis",
     "Clinical Symptom",
     None,
     "Manifestasi klinis yang diamati pada pasien, baik sebagai tanda indikasi penyakit maupun efek samping atau efek berbahaya (red flag) akibat penggunaan obat."),
    ("GejalaIndikasi",   "Gejala Indikasi Penyakit", "Indication Symptom", "Gejala",
     "Gejala yang menjadi target terapi produk obat batuk-pilek (mis. batuk, pilek, demam, hidung tersumbat)."),
    ("GejalaEfekSamping","Gejala Efek Samping Obat",  "Side Effect Symptom","Gejala",
     "Efek yang tidak diinginkan akibat penggunaan obat, misalnya mengantuk, palpitasi, mulut kering."),
    ("GejalaRedFlag",    "Gejala Bahaya / Red Flag",  "Red Flag Symptom",   "Gejala",
     "Gejala yang mengindikasikan kondisi serius: sesak napas, mengi, batuk berdarah, urin gelap. Memerlukan rujukan segera ke dokter."),
    ("InteraksiObat",
     "Interaksi Obat",
     "Drug-Drug Interaction",
     None,
     "Modifikasi efek farmakokinetik atau farmakodinamik suatu obat akibat kehadiran obat atau bahan lain, yang dapat meningkatkan toksisitas atau menurunkan efikasi terapi."),
    ("InteraksiMajor",   "Interaksi Major (Kontraindikasi Klinis)",       "Major Drug Interaction",    "InteraksiObat",
     "Interaksi dengan risiko tinggi menyebabkan bahaya serius atau kematian; umumnya harus dihindari atau memerlukan penggantian obat segera (mis. itraconazole + simvastatin, omeprazole + clopidogrel)."),
    ("InteraksiModerate","Interaksi Moderate (Perlu Pemantauan Klinis)",  "Moderate Drug Interaction", "InteraksiObat",
     "Interaksi dengan konsekuensi klinis bermakna yang masih dapat dikelola dengan pemantauan atau penyesuaian dosis; konsultasikan ke apoteker."),
    ("InteraksiMinor",   "Interaksi Minor (Risiko Klinis Rendah)",        "Minor Drug Interaction",    "InteraksiObat",
     "Interaksi dengan efek kecil dan jarang bermakna secara klinis; monitoring rutin cukup."),
    ("TindakLanjut",
     "Tindak Lanjut Klinis",
     "Clinical Follow-up Action",
     None,
     "Rekomendasi aksi klinis yang dihasilkan sistem KB setelah mendeteksi interaksi atau gejala tertentu."),
    ("SegeraKeDokter","Segera ke Dokter / IGD",   "Seek Immediate Medical Attention", "TindakLanjut",
     "Kondisi darurat atau kontraindikasi berat; pasien harus segera dirujuk ke fasilitas kesehatan."),
    ("TanyaApoteker", "Konsultasikan ke Apoteker","Consult Pharmacist",                "TindakLanjut",
     "Interaksi moderate atau efek samping bermakna; pasien disarankan mendiskusikan dengan apoteker sebelum melanjutkan penggunaan."),
    ("Pantau",        "Pantau Mandiri",            "Self-monitor",                      "TindakLanjut",
     "Risiko rendah; pasien dapat melanjutkan pengobatan sambil memantau gejala secara mandiri sesuai petunjuk pada kemasan."),
    ("GolonganObat",
     "Golongan Regulasi Obat (BPOM)",
     "Drug Regulatory Class (BPOM)",
     None,
     "Klasifikasi produk farmasi berdasarkan ketentuan Permenkes Indonesia (BPOM)."),
    ("ObatBebas",         "Obat Bebas (Lingkaran Hijau)",         "Over-the-Counter Drug (Green Circle)",   "GolonganObat", "Dapat dibeli tanpa resep di apotek/toko obat; logo lingkaran hijau BPOM."),
    ("ObatBebasTerbatas", "Obat Bebas Terbatas (Lingkaran Biru)", "Limited OTC Drug (Blue Circle)",          "GolonganObat", "Dapat dibeli tanpa resep namun dibatasi jumlah/kemasan; logo lingkaran biru BPOM."),
    ("ObatHerbalJamu",    "Obat Herbal / Jamu / Fitofarmaka",     "Herbal/Jamu/Phytopharmacy Product",      "GolonganObat", "Produk berbasis bahan alam (simplisia, ekstrak); mencakup jamu, obat herbal terstandar, dan fitofarmaka."),
    ("BentukSediaan",
     "Bentuk Sediaan Farmasi",
     "Pharmaceutical Dosage Form",
     None,
     "Bentuk fisik produk farmasi yang dikonsumsi oleh pasien."),
    ("Sirup",   "Sediaan Sirup / Suspensi",   "Syrup / Suspension",  "BentukSediaan", "Sediaan cair oral; umumnya lebih disukai untuk anak-anak."),
    ("Tablet",  "Sediaan Tablet / Kaplet",    "Tablet / Caplet",     "BentukSediaan", "Sediaan padat oral; termasuk tablet biasa, kaplet, dan tablet salut."),
    ("Kapsul",  "Sediaan Kapsul",             "Capsule",             "BentukSediaan", "Sediaan padat dengan cangkang gelatin yang menutupi serbuk atau butiran."),
    ("Sachet",  "Sediaan Sachet / Serbuk",    "Sachet / Powder",     "BentukSediaan", "Sediaan serbuk atau cairan dalam kemasan sekali pakai individual."),
    ("KondisiPasien",
     "Kondisi Pasien yang Relevan",
     "Patient Condition",
     None,
     "Kondisi medis pasien yang mempengaruhi pemilihan atau keamanan terapi obat."),
    ("HipertensiTidakTerkontrol","Hipertensi Tidak Terkontrol","Uncontrolled Hypertension","KondisiPasien",
     "Tekanan darah sistolik ≥160 mmHg atau diastolik ≥100 mmHg; kontraindikasi dekongestan oral (PSE, PE)."),
    ("GagalJantung",    "Gagal Jantung",        "Heart Failure",       "KondisiPasien", "Disfungsi pompa jantung; kontraindikasi dekongestan adrenergik pada pengguna digoxin/antiaritmia."),
    ("ProstatBPH",      "Pembesaran Prostat BPH","Benign Prostatic Hyperplasia","KondisiPasien","Risiko retensi urin diperparah oleh efek antikolinergik antihistamin generasi 1."),
    ("DuplikasiTerapetik",
     "Duplikasi Terapetik (Kontra-indikasi Farmasi)",
     "Therapeutic Duplication",
     None,
     "Kondisi di mana pasien mengonsumsi dua atau lebih obat dengan mekanisme aksi yang sama/tumpang tindih, meningkatkan risiko efek samping tanpa manfaat tambahan. Contoh: CTM + Diphenhydramine."),
]

for item in cls_hier:
    lname, label_id, label_en, parent, comment = item
    if parent is None:
        parent_tag = f'<rdfs:subClassOf rdf:resource="{OWL_NS}Thing"/>'
    else:
        parent_tag = f'<rdfs:subClassOf rdf:resource="{iri(parent)}"/>'
    w(f'  <owl:Class rdf:about="{iri(lname)}">')
    w(f'    <rdfs:label xml:lang="id">{label_id}</rdfs:label>')
    w(f'    <rdfs:label xml:lang="en">{label_en}</rdfs:label>')
    w(f'    {parent_tag}')
    w(f'    <rdfs:comment xml:lang="id">{comment}</rdfs:comment>')
    w(f'  </owl:Class>')
    w('')

# ============================================================
#  SECTION D – TBox: Defined / Equivalent Classes  (GCI Rules R-01..R-08)
# ============================================================
w(f'  <!-- ======================================================= -->')
w(f'  <!-- D. GCI RULES (General Concept Inclusions)  R-01..R-08  -->')
w(f'  <!-- ======================================================= -->')
w('')

# R-01: ObatBatukMurni ≡ ProduktObat ⊓ ∃memilikiKandungan.{antitusif/ekspektoran}
# Approx via rdfs:subClassOf restriction (OWL 2 DL compatible)
w(f'  <!-- R-01: Setiap produk yang mengandung antitusif → subclass ObatBatukMurni -->')
w(f'  <!-- Encoded as: ObatBatukMurni ⊑ ProduktObat ⊓ (∃memilikiKandungan.(Antitusif ⊔ Ekspektoran ⊔ Mukolitik)) -->')
w(f'  <owl:Class rdf:about="{iri("ObatBatukMurni")}">')
w(f'    <owl:equivalentClass>')
w(f'      <owl:Class>')
w(f'        <owl:intersectionOf rdf:parseType="Collection">')
w(f'          <rdf:Description rdf:about="{iri("ProduktObat")}"/>')
w(f'          <owl:Restriction>')
w(f'            <owl:onProperty rdf:resource="{iri("memilikiKandungan")}"/>')
w(f'            <owl:someValuesFrom>')
w(f'              <owl:Class>')
w(f'                <owl:unionOf rdf:parseType="Collection">')
w(f'                  <!-- Antitusif: DXM (CHEBI:4480) -->')
w(f'                  <rdf:Description rdf:about="{chebi("4480")}"/>')
w(f'                  <!-- Ekspektoran: Guaifenesin (CHEBI:5536) -->')
w(f'                  <rdf:Description rdf:about="{chebi("5536")}"/>')
w(f'                  <!-- Mukolitik: Bromhexine (CHEBI:3180) -->')
w(f'                  <rdf:Description rdf:about="{chebi("3180")}"/>')
w(f'                  <!-- Mukolitik: Ambroxol (CHEBI:2688) -->')
w(f'                  <rdf:Description rdf:about="{chebi("2688")}"/>')
w(f'                </owl:unionOf>')
w(f'              </owl:Class>')
w(f'            </owl:someValuesFrom>')
w(f'          </owl:Restriction>')
w(f'          <owl:Restriction>')
w(f'            <owl:onProperty rdf:resource="{iri("memilikiKandungan")}"/>')
w(f'            <owl:allValuesFrom>')
w(f'              <owl:Class>')
w(f'                <owl:complementOf>')
w(f'                  <owl:Class>')
w(f'                    <owl:unionOf rdf:parseType="Collection">')
w(f'                      <!-- Dekongestan: PSE (CHEBI:50346), PE (CHEBI:8093) -->')
w(f'                      <rdf:Description rdf:about="{chebi("50346")}"/>')
w(f'                      <rdf:Description rdf:about="{chebi("8093")}"/>')
w(f'                    </owl:unionOf>')
w(f'                  </owl:Class>')
w(f'                </owl:complementOf>')
w(f'              </owl:Class>')
w(f'            </owl:allValuesFrom>')
w(f'          </owl:Restriction>')
w(f'        </owl:intersectionOf>')
w(f'      </owl:Class>')
w(f'    </owl:equivalentClass>')
w(f'  </owl:Class>')
w('')

# R-02: ObatPilekMurni ≡ ProduktObat ⊓ ∃memilikiKandungan.Dekongestan ⊓ ¬∃memilikiKandungan.Antitusif
w(f'  <!-- R-02: Setiap produk yang mengandung dekongestan (dan tidak antitusif) → ObatPilekMurni -->')
w(f'  <owl:Class rdf:about="{iri("ObatPilekMurni")}">')
w(f'    <owl:equivalentClass>')
w(f'      <owl:Class>')
w(f'        <owl:intersectionOf rdf:parseType="Collection">')
w(f'          <rdf:Description rdf:about="{iri("ProduktObat")}"/>')
w(f'          <owl:Restriction>')
w(f'            <owl:onProperty rdf:resource="{iri("memilikiKandungan")}"/>')
w(f'            <owl:someValuesFrom>')
w(f'              <owl:Class>')
w(f'                <owl:unionOf rdf:parseType="Collection">')
w(f'                  <rdf:Description rdf:about="{chebi("50346")}"/>')
w(f'                  <rdf:Description rdf:about="{chebi("8093")}"/>')
w(f'                </owl:unionOf>')
w(f'              </owl:Class>')
w(f'            </owl:someValuesFrom>')
w(f'          </owl:Restriction>')
w(f'          <owl:Restriction>')
w(f'            <owl:onProperty rdf:resource="{iri("memilikiKandungan")}"/>')
w(f'            <owl:allValuesFrom>')
w(f'              <owl:Class>')
w(f'                <owl:complementOf rdf:resource="{chebi("4480")}"/>')
w(f'              </owl:Class>')
w(f'            </owl:allValuesFrom>')
w(f'          </owl:Restriction>')
w(f'        </owl:intersectionOf>')
w(f'      </owl:Class>')
w(f'    </owl:equivalentClass>')
w(f'  </owl:Class>')
w('')

# R-03: Produk dengan CTM/Diphenhydramine → memilikiEfekSamping.Mengantuk
w(f'  <!-- R-03: Produk dengan antihistamin-H1 gen 1 → wajib punya efek samping Mengantuk -->')
w(f'  <owl:Class rdf:about="{iri("_AH1Product")}">')
w(f'    <rdfs:label xml:lang="id">Produk mengandung antihistamin H1 generasi pertama</rdfs:label>')
w(f'    <owl:equivalentClass>')
w(f'      <owl:Class>')
w(f'        <owl:intersectionOf rdf:parseType="Collection">')
w(f'          <rdf:Description rdf:about="{iri("ProduktObat")}"/>')
w(f'          <owl:Restriction>')
w(f'            <owl:onProperty rdf:resource="{iri("memilikiKandungan")}"/>')
w(f'            <owl:someValuesFrom>')
w(f'              <owl:Class>')
w(f'                <owl:unionOf rdf:parseType="Collection">')
w(f'                  <!-- CTM: Chlorpheniramine (CHEBI:3587) -->')
w(f'                  <rdf:Description rdf:about="{chebi("3587")}"/>')
w(f'                  <!-- Diphenhydramine (CHEBI:4634) -->')
w(f'                  <rdf:Description rdf:about="{chebi("4634")}"/>')
w(f'                  <!-- Triprolidine – kelas lokal -->')
w(f'                  <rdf:Description rdf:about="{iri("Triprolidine")}"/>')
w(f'                  <!-- Doxylamine – kelas lokal -->')
w(f'                  <rdf:Description rdf:about="{iri("Doxylamine")}"/>')
w(f'                </owl:unionOf>')
w(f'              </owl:Class>')
w(f'            </owl:someValuesFrom>')
w(f'          </owl:Restriction>')
w(f'        </owl:intersectionOf>')
w(f'      </owl:Class>')
w(f'    </owl:equivalentClass>')
w(f'    <rdfs:subClassOf>')
w(f'      <owl:Restriction>')
w(f'        <owl:onProperty rdf:resource="{iri("memilikiEfekSamping")}"/>')
w(f'        <owl:someValuesFrom rdf:resource="{symp("0000024")}"/>')
w(f'      </owl:Restriction>')
w(f'    </rdfs:subClassOf>')
w(f'  </owl:Class>')
w('')

# Deklarasikan kelas bantu lokal untuk zat yang belum di-import ChEBI
for local_zat in [("Triprolidine","Triprolidine","Antihistamin H1 Gen-1 sedatif; kombinasi dekongestan populer (mis. Actifed)."),
                   ("Doxylamine","Doksylamine","Antihistamin H1 Gen-1 sedatif kuat; antitusif di Vicks F44 DWS, Siladex Cough N Cold.")]:
    ln, lbl_en, cmt = local_zat
    w(f'  <owl:Class rdf:about="{iri(ln)}">')
    w(f'    <rdfs:subClassOf rdf:resource="{iri("ZatAktif")}"/>')
    w(f'    <rdfs:label xml:lang="en">{lbl_en}</rdfs:label>')
    w(f'    <rdfs:comment xml:lang="id">{cmt}</rdfs:comment>')
    w(f'  </owl:Class>')
    w('')

# R-04: Produk dengan Dekongestan oral → dapat menyebabkan Palpitasi
w(f'  <!-- R-04: Produk dengan dekongestan oral → memilikiEfekSamping Palpitasi -->')
w(f'  <owl:Class rdf:about="{iri("_DekongestanProduct")}">')
w(f'    <rdfs:label xml:lang="id">Produk mengandung dekongestan oral (PSE atau PE)</rdfs:label>')
w(f'    <owl:equivalentClass>')
w(f'      <owl:Class>')
w(f'        <owl:intersectionOf rdf:parseType="Collection">')
w(f'          <rdf:Description rdf:about="{iri("ProduktObat")}"/>')
w(f'          <owl:Restriction>')
w(f'            <owl:onProperty rdf:resource="{iri("memilikiKandungan")}"/>')
w(f'            <owl:someValuesFrom>')
w(f'              <owl:Class>')
w(f'                <owl:unionOf rdf:parseType="Collection">')
w(f'                  <rdf:Description rdf:about="{chebi("50346")}"/>')
w(f'                  <rdf:Description rdf:about="{chebi("8093")}"/>')
w(f'                </owl:unionOf>')
w(f'              </owl:Class>')
w(f'            </owl:someValuesFrom>')
w(f'          </owl:Restriction>')
w(f'        </owl:intersectionOf>')
w(f'      </owl:Class>')
w(f'    </owl:equivalentClass>')
w(f'    <rdfs:subClassOf>')
w(f'      <owl:Restriction>')
w(f'        <owl:onProperty rdf:resource="{iri("memilikiEfekSamping")}"/>')
w(f'        <owl:someValuesFrom rdf:resource="{symp("0000530")}"/>')
w(f'      </owl:Restriction>')
w(f'    </rdfs:subClassOf>')
w(f'  </owl:Class>')
w('')

# R-05: InteraksiMajor → membutuhkanTindakLanjut SegeraKeDokter (GCI)
w(f'  <!-- R-05: Semua interaksi Major → wajib punya tindak lanjut SegeraKeDokter -->')
w(f'  <owl:Class rdf:about="{iri("InteraksiMajor")}">')
w(f'    <rdfs:subClassOf>')
w(f'      <owl:Restriction>')
w(f'        <owl:onProperty rdf:resource="{iri("membutuhkanTindakLanjut")}"/>')
w(f'        <owl:someValuesFrom rdf:resource="{iri("SegeraKeDokter")}"/>')
w(f'      </owl:Restriction>')
w(f'    </rdfs:subClassOf>')
w(f'  </owl:Class>')
w('')

# R-06: InteraksiModerate → membutuhkanTindakLanjut TanyaApoteker / Pantau
w(f'  <!-- R-06: Semua interaksi Moderate → wajib punya tindak lanjut TanyaApoteker ATAU Pantau -->')
w(f'  <owl:Class rdf:about="{iri("InteraksiModerate")}">')
w(f'    <rdfs:subClassOf>')
w(f'      <owl:Restriction>')
w(f'        <owl:onProperty rdf:resource="{iri("membutuhkanTindakLanjut")}"/>')
w(f'        <owl:someValuesFrom>')
w(f'          <owl:Class>')
w(f'            <owl:unionOf rdf:parseType="Collection">')
w(f'              <rdf:Description rdf:about="{iri("TanyaApoteker")}"/>')
w(f'              <rdf:Description rdf:about="{iri("Pantau")}"/>')
w(f'            </owl:unionOf>')
w(f'          </owl:Class>')
w(f'        </owl:someValuesFrom>')
w(f'      </owl:Restriction>')
w(f'    </rdfs:subClassOf>')
w(f'  </owl:Class>')
w('')

# R-07: Produk dengan CTM + Diphenhydramine → DuplikasiTerapetik
w(f'  <!-- R-07: Produk dengan CTM DAN Diphenhydramine → terdeteksi DuplikasiTerapetik (menyebabkan sedasi berat) -->')
w(f'  <owl:Class rdf:about="{iri("ProdukKombinasiCTMDPH")}">')
w(f'    <rdfs:label xml:lang="id">Produk CTM + Diphenhydramine = Duplikasi Terapetik Antihistamin H1</rdfs:label>')
w(f'    <owl:equivalentClass>')
w(f'      <owl:Class>')
w(f'        <owl:intersectionOf rdf:parseType="Collection">')
w(f'          <rdf:Description rdf:about="{iri("ProduktObat")}"/>')
w(f'          <owl:Restriction>')
w(f'            <owl:onProperty rdf:resource="{iri("memilikiKandungan")}"/>')
w(f'            <owl:someValuesFrom rdf:resource="{chebi("3587")}"/>')
w(f'          </owl:Restriction>')
w(f'          <owl:Restriction>')
w(f'            <owl:onProperty rdf:resource="{iri("memilikiKandungan")}"/>')
w(f'            <owl:someValuesFrom rdf:resource="{chebi("4634")}"/>')
w(f'          </owl:Restriction>')
w(f'        </owl:intersectionOf>')
w(f'      </owl:Class>')
w(f'    </owl:equivalentClass>')
w(f'    <rdfs:subClassOf rdf:resource="{iri("DuplikasiTerapetik")}"/>')
w(f'  </owl:Class>')
w('')

# R-08: Produk dengan PSE → kontraindikasiBagi HipertensiTidakTerkontrol
w(f'  <!-- R-08: Produk dengan Pseudoephedrine → kontraindikasiBagi pasien HipertensiTidakTerkontrol -->')
w(f'  <owl:Class rdf:about="{iri("ProdukDenganPSE")}">')
w(f'    <rdfs:label xml:lang="id">Produk dengan Pseudoephedrine → kontraindikasi hipertensi</rdfs:label>')
w(f'    <owl:equivalentClass>')
w(f'      <owl:Class>')
w(f'        <owl:intersectionOf rdf:parseType="Collection">')
w(f'          <rdf:Description rdf:about="{iri("ProduktObat")}"/>')
w(f'          <owl:Restriction>')
w(f'            <owl:onProperty rdf:resource="{iri("memilikiKandungan")}"/>')
w(f'            <owl:someValuesFrom rdf:resource="{chebi("50346")}"/>')
w(f'          </owl:Restriction>')
w(f'        </owl:intersectionOf>')
w(f'      </owl:Class>')
w(f'    </owl:equivalentClass>')
w(f'    <rdfs:subClassOf>')
w(f'      <owl:Restriction>')
w(f'        <owl:onProperty rdf:resource="{iri("kontraindikasiBagi")}"/>')
w(f'        <owl:someValuesFrom rdf:resource="{iri("HipertensiTidakTerkontrol")}"/>')
w(f'      </owl:Restriction>')
w(f'    </rdfs:subClassOf>')
w(f'  </owl:Class>')
w('')

# ============================================================
#  SECTION E – ABox: Individual Instances (12 produk pilot)
# ============================================================
w(f'  <!-- ======================================================= -->')
w(f'  <!-- E. ABOX – 12 INDIVIDU PRODUK APOTEK INDONESIA          -->')
w(f'  <!-- ======================================================= -->')
w('')

# Format: (local_id, nama, slug, nie, pabrik, harga, url,
#          golongan_cls, sediaan_cls, owl_classes[],
#          kandungan_chebi_iris[], indikasi_symp_iris[], efeksamping_symp_iris[],
#          compose_text, kode_atc_note)
#
# kandungan_chebi_iris: list of CHEBI or local IRIs
# classes: list of local class names the individual is of

SYMP_BATUK       = symp("0000614")
SYMP_BATUK_KERING= symp("0000025")
SYMP_BATUK_DAH   = symp("0020027")
SYMP_PILEK       = symp("0000372")
SYMP_HIDUNG      = symp("0000869")
SYMP_BERSIN      = symp("0000139")
SYMP_DEMAM       = symp("0000613")
SYMP_SAKITKEPALA = symp("0000504")
SYMP_TENGGOROKAN = symp("0000505")
SYMP_MENGANTUK   = symp("0000024")
SYMP_PUSING      = symp("0000610")
SYMP_MULUT_KERING= symp("0000260")
SYMP_PALPITASI   = symp("0000530")
SYMP_MUAL        = symp("0000458")

CHEBI_PCT = chebi("46195")  # Paracetamol
CHEBI_IBU = chebi("5855")   # Ibuprofen
CHEBI_DXM = chebi("4480")   # Dextromethorphan
CHEBI_PSE = chebi("50346")  # Pseudoephedrine
CHEBI_PE  = chebi("8093")   # Phenylephrine
CHEBI_CTM = chebi("3587")   # Chlorpheniramine
CHEBI_DPH = chebi("4634")   # Diphenhydramine
CHEBI_CE  = chebi("3561")   # Cetirizine
CHEBI_GG  = chebi("5536")   # Guaifenesin
CHEBI_BMX = chebi("3180")   # Bromhexine
CHEBI_AMB = chebi("2688")   # Ambroxol
TRIPO     = iri("Triprolidine")
DOXA      = iri("Doxylamine")

individuals = [
    # 1 - Siladex Cough N Cold Syrup 100mL - Kombinasi DXM+PSE+Doxylamine
    dict(
        lid="prod_SiladexCoughNColSyr100",
        nama="Siladex Cough N Cold Syrup 100mL",
        slug="SILADEX-COUGH-N-COLD-SYR-100ML-9753",
        nie="DTL8713002537A1", pabrik="PT Konimex", harga=25149,
        url="https://www.k24klik.com/p/SILADEX-COUGH-N-COLD-SYR-100ML-9753",
        golongan="ObatBebasTerbatas", sediaan="Sirup",
        classes=["ObatKombinasiBatukPilek","_AH1Product","_DekongestanProduct"],
        kandungan=[CHEBI_DXM, CHEBI_PSE, DOXA],
        indikasi=[SYMP_BATUK_KERING, SYMP_HIDUNG, SYMP_PILEK],
        efeksamping=[SYMP_MENGANTUK, SYMP_PALPITASI],
        komposisi="Dextromethorphan HBr 7,5 mg; Pseudoephedrine HCl 15 mg; Doxylamine Succinate 2 mg / 5 mL",
    ),
    # 2 - Actifed Plus Syrup Merah 60mL - Kombinasi Triprolidine+PSE+DXM
    dict(
        lid="prod_ActifedPlusSyrMerah60",
        nama="Actifed Plus Cough Suppress Syrup Merah 60mL",
        slug="ACTIFED-PLUS-COUGH-SUPPRESS-SYR-MERAH-60ML-275",
        nie="DTL1624504137A1", pabrik="GlaxoSmithKline (GSK)", harga=0,
        url="https://www.k24klik.com/p/ACTIFED-PLUS-COUGH-SUPPRESS-SYR-MERAH-60ML-275",
        golongan="ObatBebasTerbatas", sediaan="Sirup",
        classes=["ObatKombinasiBatukPilek","_AH1Product","_DekongestanProduct"],
        kandungan=[TRIPO, CHEBI_PSE, CHEBI_DXM],
        indikasi=[SYMP_BATUK_KERING, SYMP_HIDUNG, SYMP_PILEK, SYMP_BERSIN],
        efeksamping=[SYMP_MENGANTUK, SYMP_PALPITASI, SYMP_MULUT_KERING],
        komposisi="Triprolidine HCl 1,25 mg; Pseudoephedrine HCl 30 mg; Dextromethorphan HBr 10 mg / 5 mL",
    ),
    # 3 - Komix Jeruk Nipis 7mL Sachet - GG+DXM+CTM
    dict(
        lid="prod_KomixJerukNipis7mL",
        nama="Komix Jeruk Nipis 7mL Sachet",
        slug="KOMIX-JERUK-NIPIS-7ML-SACH-30S-8909",
        nie="DTL9502807737A1", pabrik="Kalbe Farma", harga=2360,
        url="https://www.k24klik.com/p/KOMIX-JERUK-NIPIS-7ML-SACH-30S-8909",
        golongan="ObatBebasTerbatas", sediaan="Sachet",
        classes=["ObatKombinasiBatukPilek","_AH1Product"],
        kandungan=[CHEBI_GG, CHEBI_DXM, CHEBI_CTM],
        indikasi=[SYMP_BATUK_DAH, SYMP_BATUK_KERING, SYMP_PILEK],
        efeksamping=[SYMP_MENGANTUK, SYMP_MULUT_KERING, SYMP_MUAL],
        komposisi="Guaifenesin 100 mg; Dextromethorphan HBr 15 mg; Chlorpheniramine Maleate 2 mg",
    ),
    # 4 - Vicks F44 Anak Syrup 54mL - GG+DXM (Batuk Murni)
    dict(
        lid="prod_VicksF44AnakSyr54",
        nama="Vicks F44 Anak Syrup 54mL",
        slug="VICKS-F44-ANAK-SYR-54ML-8839",
        nie="DTL0704519837A1", pabrik="Darya-Varia Laboratoria", harga=30331,
        url="https://www.k24klik.com/p/VICKS-F44-ANAK-SYR-54ML-8839",
        golongan="ObatBebasTerbatas", sediaan="Sirup",
        classes=["ObatBatukMurni"],
        kandungan=[CHEBI_GG, CHEBI_DXM],
        indikasi=[SYMP_BATUK_KERING, SYMP_BATUK_DAH],
        efeksamping=[SYMP_MUAL],
        komposisi="Guaifenesin; Dextromethorphan HBr (kadar pediatrik sesuai kemasan)",
    ),
    # 5 - Procold Flu & Batuk Kaplet - PCT+DXM+PSE
    dict(
        lid="prod_ProcoldFluBatuKaplet",
        nama="Procold Flu dan Batuk Kaplet",
        slug="PROCOLD-FLU-BATUK-CAPL-6S-STRIP-24S-2072",
        nie="DTL1111641504A1", pabrik="Kalbe Farma", harga=0,
        url="https://www.k24klik.com/p/PROCOLD-FLU&BATUK-CAPL-6S-STRIP-24S-2072",
        golongan="ObatBebasTerbatas", sediaan="Tablet",
        classes=["ObatKombinasiBatukPilek","_DekongestanProduct"],
        kandungan=[CHEBI_PCT, CHEBI_DXM, CHEBI_PSE],
        indikasi=[SYMP_DEMAM, SYMP_SAKITKEPALA, SYMP_BATUK_KERING, SYMP_HIDUNG, SYMP_PILEK],
        efeksamping=[SYMP_PALPITASI, SYMP_MUAL],
        komposisi="Paracetamol 500 mg; Dextromethorphan HBr 10 mg; Pseudoephedrine HCl 30 mg",
    ),
    # 6 - Paramex Flu & Batuk Tablet - PCT+PSE+DXM
    dict(
        lid="prod_ParamexFluBatukTab",
        nama="Paramex Flu dan Batuk Tablet",
        slug="PARAMEX-FLU-BATUK-TAB-4S-STRIP-25S-9318",
        nie="DTL9813017510A1", pabrik="Konimex", harga=3320,
        url="https://www.k24klik.com/p/PARAMEX-FLU&BATUK-TAB-4S-STRIP-25S-9318",
        golongan="ObatBebasTerbatas", sediaan="Tablet",
        classes=["ObatKombinasiBatukPilek","_DekongestanProduct"],
        kandungan=[CHEBI_PCT, CHEBI_PSE, CHEBI_DXM],
        indikasi=[SYMP_DEMAM, SYMP_SAKITKEPALA, SYMP_BATUK_KERING, SYMP_HIDUNG, SYMP_PILEK],
        efeksamping=[SYMP_PALPITASI, SYMP_MUAL],
        komposisi="Paracetamol 500 mg; Pseudoephedrine HCl 30 mg; Dextromethorphan HBr 15 mg",
    ),
    # 7 - Alpara Kaplet - PCT+PPA+CTM+DXM
    dict(
        lid="prod_AlparaKaplet",
        nama="Alpara Kaplet",
        slug="ALPARA-CAPL-10S-STRIP-15S-1603",
        nie="DTL9230902604A1", pabrik="Molex Ayus", harga=0,
        url="https://www.k24klik.com/p/ALPARA-CAPL-10S-STRIP-15S-1603",
        golongan="ObatBebasTerbatas", sediaan="Tablet",
        classes=["ObatKombinasiBatukPilek","_AH1Product"],
        kandungan=[CHEBI_PCT, CHEBI_CTM, CHEBI_DXM],  # PPA = phenylpropanolamine belum di-import, skip
        indikasi=[SYMP_DEMAM, SYMP_SAKITKEPALA, SYMP_BATUK_KERING, SYMP_PILEK, SYMP_BERSIN],
        efeksamping=[SYMP_MENGANTUK, SYMP_MULUT_KERING],
        komposisi="Paracetamol 500 mg; Phenylpropanolamine HCl 12,5 mg; Chlorpheniramine Maleate 2 mg; Dextromethorphan HBr 15 mg",
    ),
    # 8 - OB Combi ATT Menthol Sirup 60mL - DXM+Diphenhydramine
    dict(
        lid="prod_OBCombiATTMentholSyr60",
        nama="OB Combi ATT Menthol Sirup 60mL",
        slug="OB-COMBI-ATT-MENTHOL-SYR-60ML-34066",
        nie="", pabrik="Combiphar", harga=21097,
        url="https://www.k24klik.com/p/OB-COMBI-ATT-MENTHOL-SYR-60ML-34066",
        golongan="ObatBebasTerbatas", sediaan="Sirup",
        classes=["ObatKombinasiBatukPilek","_AH1Product"],
        kandungan=[CHEBI_DXM, CHEBI_DPH],
        indikasi=[SYMP_BATUK_KERING],
        efeksamping=[SYMP_MENGANTUK, SYMP_MULUT_KERING],
        komposisi="Dextromethorphan HBr 12,5 mg; Diphenhydramine HCl 7,5 mg / 5 mL",
    ),
    # 9 - Sanmol Forte 250mg/5mL Syrup - Paracetamol murni
    dict(
        lid="prod_SanmolForte250Syr60",
        nama="Sanmol Forte 250mg/5mL Syrup 60mL",
        slug="SANMOL-FORTE-250MG-5ML-SYR-60ML-8741",
        nie="DBL1322235037B1", pabrik="Sanbe Farma", harga=0,
        url="https://www.k24klik.com/p/SANMOL-FORTE-250MG-5ML-SYR-60ML-8741",
        golongan="ObatBebas", sediaan="Sirup",
        classes=["ObatPilekMurni"],
        kandungan=[CHEBI_PCT],
        indikasi=[SYMP_DEMAM, SYMP_SAKITKEPALA, SYMP_TENGGOROKAN],
        efeksamping=[SYMP_MUAL],
        komposisi="Paracetamol 250 mg / 5 mL",
    ),
    # 10 - Triaminic Batuk Pilek Syrup 60mL - PSE+DXM
    dict(
        lid="prod_TriaminicBatukPilekSyr60",
        nama="Triaminic Batuk Pilek Syrup 60mL",
        slug="TRIAMINIC-BATUK-PILEK-SYR-60ML-326",
        nie="DTL1624503737A1", pabrik="Novartis Indonesia", harga=0,
        url="https://www.k24klik.com/p/TRIAMINIC-BATUK-PILEK-SYR-60ML-326",
        golongan="ObatBebasTerbatas", sediaan="Sirup",
        classes=["ObatKombinasiBatukPilek","_DekongestanProduct"],
        kandungan=[CHEBI_PSE, CHEBI_DXM],
        indikasi=[SYMP_BATUK_KERING, SYMP_HIDUNG, SYMP_PILEK],
        efeksamping=[SYMP_PALPITASI, SYMP_PUSING],
        komposisi="Pseudoephedrine HCl 15 mg; Dextromethorphan HBr 5 mg / 5 mL",
    ),
    # 11 - Promedex Tablet - DXM+GG+CTM
    dict(
        lid="prod_PromedexTab",
        nama="Promedex Tablet",
        slug="PROMEDEX-TAB-100S-16748",
        nie="DTL7617623910A1", pabrik="Interbat", harga=34574,
        url="https://www.k24klik.com/p/PROMEDEX-TAB-100S-16748",
        golongan="ObatBebasTerbatas", sediaan="Tablet",
        classes=["ObatKombinasiBatukPilek","_AH1Product"],
        kandungan=[CHEBI_DXM, CHEBI_GG, CHEBI_CTM],
        indikasi=[SYMP_BATUK_KERING, SYMP_BATUK_DAH, SYMP_PILEK],
        efeksamping=[SYMP_MENGANTUK, SYMP_MULUT_KERING, SYMP_MUAL],
        komposisi="Dextromethorphan HBr 15 mg; Guaifenesin 100 mg; Chlorpheniramine Maleate 1 mg",
    ),
    # 12 - Lapifed DM Syrup 100mL - Triprolidine+PSE+DXM
    dict(
        lid="prod_LapifedDMSyr100",
        nama="Lapifed DM Syrup 100mL",
        slug="LAPIFED-DM-SYR-100ML-295",
        nie="DTL9813308837A1", pabrik="Lapi Laboratories", harga=0,
        url="https://www.k24klik.com/p/LAPIFED-DM-SYR-100ML-295",
        golongan="ObatBebasTerbatas", sediaan="Sirup",
        classes=["ObatKombinasiBatukPilek","_AH1Product","_DekongestanProduct"],
        kandungan=[TRIPO, CHEBI_PSE, CHEBI_DXM],
        indikasi=[SYMP_BATUK_KERING, SYMP_HIDUNG, SYMP_PILEK, SYMP_BERSIN],
        efeksamping=[SYMP_MENGANTUK, SYMP_PALPITASI, SYMP_MULUT_KERING],
        komposisi="Triprolidine HCl 1,25 mg; Pseudoephedrine HCl 30 mg; Dextromethorphan HBr 10 mg / 5 mL",
    ),
]

def xml_safe(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','&quot;')

for idx, ind in enumerate(individuals, 1):
    lid = ind["lid"]
    w(f'  <!-- Individual #{idx}: {ind["nama"]} -->')
    w(f'  <owl:NamedIndividual rdf:about="{iri(lid)}">')
    # Class assertions
    primary_cls = ind["classes"][0]
    w(f'    <rdf:type rdf:resource="{iri(primary_cls)}"/>')
    for cls in ind["classes"][1:]:
        w(f'    <rdf:type rdf:resource="{iri(cls)}"/>')
    # Also assert ProduktObat
    w(f'    <rdf:type rdf:resource="{iri("ProduktObat")}"/>')
    # Also assert ObatBatukPilek
    w(f'    <rdf:type rdf:resource="{iri("ObatBatukPilek")}"/>')
    # Golongan & Sediaan
    w(f'    <kbr:memilikiGolongan rdf:resource="{iri(ind["golongan"])}"/>')
    w(f'    <kbr:memilikiBentukSediaan rdf:resource="{iri(ind["sediaan"])}"/>')
    # Kandungan
    for k in ind["kandungan"]:
        w(f'    <kbr:memilikiKandungan rdf:resource="{k}"/>')
    # Indikasi gejala
    for s in ind["indikasi"]:
        w(f'    <kbr:mengindikasikanGejala rdf:resource="{s}"/>')
    # Efek samping
    for s in ind["efeksamping"]:
        w(f'    <kbr:memilikiEfekSamping rdf:resource="{s}"/>')
    # Data properties
    w(f'    <kbr:namaDagang>{xml_safe(ind["nama"])}</kbr:namaDagang>')
    w(f'    <kbr:namaProdusen>{xml_safe(ind["pabrik"])}</kbr:namaProdusen>')
    if ind["nie"]:
        w(f'    <kbr:nomorBPOM>{xml_safe(ind["nie"])}</kbr:nomorBPOM>')
    if ind["harga"] > 0:
        w(f'    <kbr:hargaRupiah rdf:datatype="{XSD}integer">{ind["harga"]}</kbr:hargaRupiah>')
    w(f'    <kbr:nomorSlugK24>{xml_safe(ind["slug"])}</kbr:nomorSlugK24>')
    w(f'    <kbr:urlK24 rdf:datatype="{XSD}anyURI">{xml_safe(ind["url"])}</kbr:urlK24>')
    w(f'    <kbr:doseInfoPer5mL>{xml_safe(ind["komposisi"])}</kbr:doseInfoPer5mL>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(ind["nama"])}</rdfs:label>')
    w(f'  </owl:NamedIndividual>')
    w('')

# ============================================================
#  SECTION F – TBox & ABox: ZatAktif Classes & Individuals (29 zat)
# ============================================================
w(f'  <!-- ======================================================= -->')
w(f'  <!-- F. ZAT AKTIF: CLASSES & INDIVIDUALS                     -->')
w(f'  <!-- ======================================================= -->')
w('')

import csv

sheet1_path = r"d:\UNS\SMT_5\KBR\PROJECT\ProjectKBR-Group4\data\curation\sheet1_zat_aktif.csv"
zat_rows = []
if os.path.exists(sheet1_path):
    with open(sheet1_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            zat_rows.append(r)

for r in zat_rows:
    z_iri = r["chebi_iri"]
    z_name = r["nama_zat"]
    z_atc = r["kode_atc"]
    z_chebi = r["chebi_id"]
    z_desc = r["peran_farmakologis"]
    
    # Declare Class
    w(f'  <owl:Class rdf:about="{z_iri}">')
    w(f'    <rdfs:subClassOf rdf:resource="{iri("ZatAktif")}"/>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(z_name)}</rdfs:label>')
    w(f'    <rdfs:comment xml:lang="id">{xml_safe(z_desc)}</rdfs:comment>')
    w(f'  </owl:Class>')
    
    # Declare Individual (Punning)
    w(f'  <owl:NamedIndividual rdf:about="{z_iri}">')
    w(f'    <rdf:type rdf:resource="{iri("ZatAktif")}"/>')
    w(f'    <rdf:type rdf:resource="{z_iri}"/>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(z_name)}</rdfs:label>')
    w(f'    <kbr:kodeATC>{xml_safe(z_atc)}</kbr:kodeATC>')
    w(f'    <kbr:chebiID>{xml_safe(z_chebi)}</kbr:chebiID>')
    w(f'    <rdfs:comment xml:lang="id">{xml_safe(z_desc)}</rdfs:comment>')
    w(f'  </owl:NamedIndividual>')
    w('')

# Local ZatAktif not in ChEBI (Triprolidine, Doxylamine)
for lname, lbl_en, kode_atc, keterangan in [
    ("Triprolidine", "Triprolidine HCl", "R06AX", "Antihistamin H1 gen-1; kombinasi dengan pseudoephedrine"),
    ("Doxylamine", "Doxylamine Succinate", "R06AA09", "Antihistamin H1 gen-1 sangat sedatif; antitusif di Vicks F44 DWS, Siladex Cough N Cold"),
]:
    w(f'  <owl:Class rdf:about="{iri(lname)}">')
    w(f'    <rdfs:subClassOf rdf:resource="{iri("ZatAktif")}"/>')
    w(f'    <rdfs:label xml:lang="en">{lbl_en}</rdfs:label>')
    w(f'    <rdfs:comment xml:lang="id">{xml_safe(keterangan)}</rdfs:comment>')
    w(f'  </owl:Class>')
    w(f'  <owl:NamedIndividual rdf:about="{iri(lname)}">')
    w(f'    <rdf:type rdf:resource="{iri("ZatAktif")}"/>')
    w(f'    <rdf:type rdf:resource="{iri(lname)}"/>')
    w(f'    <rdfs:label xml:lang="en">{lbl_en}</rdfs:label>')
    w(f'    <kbr:kodeATC>{kode_atc}</kbr:kodeATC>')
    w(f'    <rdfs:comment xml:lang="id">{xml_safe(keterangan)}</rdfs:comment>')
    w(f'  </owl:NamedIndividual>')
    w('')

# ============================================================
#  SECTION G – ABox: Interaksi Obat Individuals (from sheet2)
# ============================================================
w(f'  <!-- ======================================================= -->')
w(f'  <!-- G. ABOX – INTERAKSI OBAT INDIVIDUALS (dari sheet2 kurasi) -->')
w(f'  <!-- ======================================================= -->')
w('')

interactions_abox = [
    # (lid, cls, zat_a_iri, zat_b_iri, tindak_lanjut_iri, tingkat_bukti, label_id)
    ("int_ItraSimvastatin", "InteraksiMajor",
     chebi("6076"), chebi("9150"), iri("SegeraKeDokter"), "A",
     "Interaksi Major: Itraconazole inhibisi CYP3A4 → akumulasi Simvastatin → risiko rhabdomyolysis"),
    ("int_KetAtorva", "InteraksiMajor",
     chebi("47519"), chebi("39548"), iri("SegeraKeDokter"), "A",
     "Interaksi Major: Ketoconazole inhibisi CYP3A4 → toksisitas Atorvastatin"),
    ("int_OmeClopidogrel", "InteraksiMajor",
     chebi("7772"), chebi("37941"), iri("SegeraKeDokter"), "A",
     "Interaksi Major: Omeprazole inhibisi CYP2C19 → penurunan efikasi Clopidogrel"),
    ("int_IbuprofenWarfarin", "InteraksiMajor",
     chebi("5855"), chebi("10033"), iri("SegeraKeDokter"), "A",
     "Interaksi Major: Ibuprofen inhibisi COX-1 + efek anti-agregasi → risiko perdarahan GI bersama Warfarin"),
    ("int_CTMDiphenhydramine", "InteraksiModerate",
     chebi("3587"), chebi("4634"), iri("TanyaApoteker"), "A",
     "Interaksi Moderate: CTM + Diphenhydramine → duplikasi antihistamin H1 → sedasi berat"),
    ("int_CetirizineCTM", "InteraksiModerate",
     chebi("3561"), chebi("3587"), iri("Pantau"), "A",
     "Interaksi Moderate: Cetirizine + CTM → kehilangan keunggulan non-sedatif, penekanan SSP aditif"),
    ("int_CTMDextromethorphan", "InteraksiModerate",
     chebi("3587"), chebi("4480"), iri("Pantau"), "A",
     "Interaksi Moderate: CTM + DXM (dalam obat flu kombinasi) → depresan SSP aditif, mengantuk"),
    ("int_PseudoephedrineDigoxin", "InteraksiModerate",
     chebi("50346"), chebi("4551"), iri("TanyaApoteker"), "A",
     "Interaksi Moderate: Pseudoephedrine stimulasi adrenergik + Digoxin → risiko aritmia"),
    ("int_PhenylDigoxin", "InteraksiModerate",
     chebi("8093"), chebi("4551"), iri("TanyaApoteker"), "A",
     "Interaksi Moderate: Phenylephrine alfa-1 → aritmia pada jantung terdigitalisasi"),
    ("int_AlphaMangostinSimva", "InteraksiMajor",
     chebi("67547"), chebi("9150"), iri("SegeraKeDokter"), "B",
     "Interaksi Major: Alpha-Mangostin inhibisi CYP3A4 → akumulasi Simvastatin"),
    ("int_ParacetamolWarfarin", "InteraksiModerate",
     chebi("46195"), chebi("10033"), iri("Pantau"), "A",
     "Interaksi Moderate: Paracetamol dosis tinggi → peningkatan INR ringan pada pasien Warfarin"),
]

for lid, cls, zat_a, zat_b, tl_iri, bukti, label in interactions_abox:
    w(f'  <owl:NamedIndividual rdf:about="{iri(lid)}">')
    w(f'    <rdf:type rdf:resource="{iri(cls)}"/>')
    w(f'    <rdf:type rdf:resource="{iri("InteraksiObat")}"/>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(label)}</rdfs:label>')
    w(f'    <kbr:menghasilkanInteraksi rdf:resource="{iri(lid)}"/>')
    w(f'    <kbr:membutuhkanTindakLanjut rdf:resource="{tl_iri}"/>')
    w(f'    <kbr:tingkatBukti>{bukti}</kbr:tingkatBukti>')
    w(f'  </owl:NamedIndividual>')
    # Assert the interaction direction on zat_a → zat_b
    w(f'  <!-- memilikiInteraksiDengan: {zat_a.split("/")[-1]} ↔ {zat_b.split("/")[-1]} -->')
    w(f'  <rdf:Description rdf:about="{zat_a}">')
    w(f'    <kbr:memilikiInteraksiDengan rdf:resource="{zat_b}"/>')
    w(f'    <kbr:menghasilkanInteraksi rdf:resource="{iri(lid)}"/>')
    w(f'  </rdf:Description>')
    w('')

# ============================================================
#  SECTION H – ABox: Gejala Individual Annotations (bridged SYMP)
# ============================================================
w(f'  <!-- ======================================================= -->')
w(f'  <!-- H. ABOX – GEJALA INDIVIDUALS (annotation SYMP terms)   -->')
w(f'  <!-- ======================================================= -->')
w('')

gejala_list = [
    (symp("0000614"),  "Batuk",                        "cough",                   "GejalaIndikasi",    "Pantau"),
    (symp("0000025"),  "Batuk kering / tidak berdahak","dry cough",               "GejalaIndikasi",    "Pantau"),
    (symp("0020027"),  "Batuk berdahak / produktif",   "wet cough",               "GejalaIndikasi",    "Pantau"),
    (symp("0000869"),  "Hidung tersumbat",              "nasal congestion",        "GejalaIndikasi",    "Pantau"),
    (symp("0000372"),  "Pilek / hidung berair",         "rhinorrhea",              "GejalaIndikasi",    "Pantau"),
    (symp("0000139"),  "Bersin-bersin",                 "sneezing",                "GejalaIndikasi",    "Pantau"),
    (symp("0000505"),  "Sakit tenggorokan",             "throat pain",             "GejalaIndikasi",    "Pantau"),
    (symp("0000613"),  "Demam",                         "fever",                   "GejalaIndikasi",    "Pantau"),
    (symp("0000504"),  "Sakit kepala",                  "headache",                "GejalaIndikasi",    "Pantau"),
    (symp("0000024"),  "Mengantuk berat",               "drowsiness",              "GejalaEfekSamping", "TanyaApoteker"),
    (symp("0000610"),  "Pusing / melayang",             "dizziness",               "GejalaEfekSamping", "TanyaApoteker"),
    (symp("0000260"),  "Mulut kering",                  "dry mouth",               "GejalaEfekSamping", "Pantau"),
    (symp("0000557"),  "Sulit buang air kecil",         "urinary retention",       "GejalaEfekSamping", "TanyaApoteker"),
    (symp("0000530"),  "Jantung berdebar-debar",        "palpitation",             "GejalaEfekSamping", "TanyaApoteker"),
    (symp("0000529"),  "Denyut jantung terlalu cepat",  "tachycardia",             "GejalaEfekSamping", "TanyaApoteker"),
    (symp("0000458"),  "Mual / eneg",                   "nausea",                  "GejalaEfekSamping", "Pantau"),
    (symp("0019145"),  "Muntah",                        "vomiting",                "GejalaEfekSamping", "TanyaApoteker"),
    (symp("0019153"),  "Sesak napas",                   "dyspnea",                 "GejalaRedFlag",     "SegeraKeDokter"),
    (symp("0000604"),  "Napas berbunyi mengi",           "wheezing",                "GejalaRedFlag",     "SegeraKeDokter"),
    (symp("0000576"),  "Nyeri dada",                    "chest pain",              "GejalaRedFlag",     "SegeraKeDokter"),
    (symp("0000242"),  "Batuk berdarah",                "cough with bloody sputum","GejalaRedFlag",     "SegeraKeDokter"),
    (symp("0020043"),  "Urin berwarna gelap",           "dark urine",              "GejalaRedFlag",     "SegeraKeDokter"),
]

for siri, lbl_id, lbl_en, gejala_cls, tl in gejala_list:
    # Declare Class
    w(f'  <owl:Class rdf:about="{siri}">')
    w(f'    <rdfs:subClassOf rdf:resource="{iri(gejala_cls)}"/>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(lbl_id)}</rdfs:label>')
    w(f'    <rdfs:label xml:lang="en">{xml_safe(lbl_en)}</rdfs:label>')
    w(f'  </owl:Class>')
    
    # Declare Individual
    w(f'  <owl:NamedIndividual rdf:about="{siri}">')
    w(f'    <rdf:type rdf:resource="{iri(gejala_cls)}"/>')
    w(f'    <rdf:type rdf:resource="{siri}"/>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(lbl_id)}</rdfs:label>')
    w(f'    <rdfs:label xml:lang="en">{xml_safe(lbl_en)}</rdfs:label>')
    w(f'    <skos:altLabel xml:lang="id">{xml_safe(lbl_id)}</skos:altLabel>')
    tl_iri = iri(tl)
    w(f'    <kbr:membutuhkanTindakLanjut rdf:resource="{tl_iri}"/>')
    w(f'  </owl:NamedIndividual>')
    w('')

# ============================================================
#  SECTION I – TindakLanjut Individuals
# ============================================================
w(f'  <!-- ======================================================= -->')
w(f'  <!-- I. ABOX – TINDAK LANJUT INDIVIDUALS                    -->')
w(f'  <!-- ======================================================= -->')
w('')

tl_list = [
    ("SegeraKeDokter","Segera ke Dokter / IGD",        "Seek Immediate Medical Attention","Kontraindikasi berat atau gejala darurat; harus dirujuk ke fasilitas kesehatan segera."),
    ("TanyaApoteker", "Konsultasikan ke Apoteker",     "Consult Pharmacist",              "Interaksi moderate atau efek samping bermakna; diskusikan dengan apoteker."),
    ("Pantau",        "Pantau Mandiri (Self-Monitor)", "Self-monitor",                    "Risiko rendah; lanjutkan sambil memantau gejala secara mandiri."),
]
for lname, lid_lbl, len_lbl, cmt in tl_list:
    w(f'  <owl:NamedIndividual rdf:about="{iri(lname)}">')
    w(f'    <rdf:type rdf:resource="{iri(lname.replace(lname, lname))}"/>')
    w(f'    <rdf:type rdf:resource="{iri("TindakLanjut")}"/>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(lid_lbl)}</rdfs:label>')
    w(f'    <rdfs:label xml:lang="en">{xml_safe(len_lbl)}</rdfs:label>')
    w(f'    <rdfs:comment xml:lang="id">{xml_safe(cmt)}</rdfs:comment>')
    w(f'  </owl:NamedIndividual>')
    w('')

# ============================================================
#  SECTION J – GolonganObat & BentukSediaan Individuals
# ============================================================
w(f'  <!-- ======================================================= -->')
w(f'  <!-- J. ABOX – GOLONGAN & SEDIAAN INDIVIDUALS               -->')
w(f'  <!-- ======================================================= -->')
w('')

for lname, cls, lid_lbl, len_lbl in [
    ("ObatBebas",         "ObatBebas",         "Obat Bebas (Logo Lingkaran Hijau)",         "Over-the-Counter Drug (Green Circle)"),
    ("ObatBebasTerbatas", "ObatBebasTerbatas",  "Obat Bebas Terbatas (Logo Lingkaran Biru)", "Limited OTC Drug (Blue Circle)"),
    ("ObatHerbalJamu",    "ObatHerbalJamu",     "Obat Herbal / Jamu / Fitofarmaka",          "Herbal/Jamu/Phytopharmacy Product"),
    ("Sirup",             "Sirup",              "Sediaan Sirup / Suspensi Oral",             "Syrup / Oral Suspension"),
    ("Tablet",            "Tablet",             "Sediaan Tablet / Kaplet",                   "Tablet / Caplet"),
    ("Kapsul",            "Kapsul",             "Sediaan Kapsul",                            "Capsule"),
    ("Sachet",            "Sachet",             "Sediaan Sachet / Serbuk",                   "Sachet / Powder"),
]:
    w(f'  <owl:NamedIndividual rdf:about="{iri(lname)}">')
    w(f'    <rdf:type rdf:resource="{iri(cls)}"/>')
    w(f'    <rdfs:label xml:lang="id">{xml_safe(lid_lbl)}</rdfs:label>')
    w(f'    <rdfs:label xml:lang="en">{xml_safe(len_lbl)}</rdfs:label>')
    w(f'  </owl:NamedIndividual>')
    w('')

# ============================================================
#  CLOSE
# ============================================================
w('</rdf:RDF>')

content = "\n".join(lines)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(content)

size = os.path.getsize(OUT_PATH)
sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
print(f"[OK] kb_v1.owl ditulis ke: {OUT_PATH}")
print(f"     Ukuran file   : {size:,} bytes")
print(f"     SHA-256       : {sha256}")
print(f"     Jumlah baris  : {content.count(chr(10)):,}")
print(f"     Individu      : {len(individuals)} produk apotek + {len(zat_rows)+2} zat aktif")
print(f"     Interaksi ABox: {len(interactions_abox)} pasangan")
print(f"     Gejala ABox   : {len(gejala_list)} gejala")
print(f"     Kelas TBox    : {len(cls_hier)} kelas")
print(f"     Object Props  : {len(object_properties)}")
print(f"     Data Props    : {len(data_props)}")
