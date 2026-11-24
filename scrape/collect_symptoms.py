"""
Automated extractor and annotator for Symptom Ontology (SYMP) from KB/symp.owl.

Produces out/symptom_modul.owl containing 22 curated symptoms for the cough & cold domain:
- Indications (Cough, Dry cough, Wet cough, Nasal congestion, Rhinorrhea, Sneezing, Sore throat, Fever, Headache)
- Adverse Effects (Drowsiness, Dizziness, Dry mouth, Urinary retention, Palpitation, Tachycardia, Nausea, Vomiting)
- Red Flags (Dyspnea/Sesak napas, Wheezing/Mengi, Chest pain, Hemoptysis, Dark urine)

Annotates with Indonesian layperson terms (skos:altLabel), category, and triage recommendations
(Pantau, TanyaApoteker, SegeraKeDokter). Validates with HermiT & OWL 2 DL.
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

ROBOT_JAR = Path(os.environ.get("ROBOT_JAR", "robot.jar"))
ONTOLOGY_IRI = "http://purl.obolibrary.org/obo/kbr-group4/symptom_modul.owl"

PILOT_SYMPTOM_IDS = {
    "SYMP:0000025", "SYMP:0020027", "SYMP:0000869", "SYMP:0000372",
    "SYMP:0000139", "SYMP:0000505", "SYMP:0000613", "SYMP:0000024",
    "SYMP:0000610", "SYMP:0000530", "SYMP:0019153", "SYMP:0000604",
    "SYMP:0000576", "SYMP:0000242", "SYMP:0020043",
}

LAY_SYMPTOM_SYNONYMS = {
    "SYMP:0000614": ["batuk-batuk"],
    "SYMP:0000025": ["batuk kering", "batuk tidak berdahak"],
    "SYMP:0020027": ["batuk berdahak", "batuk berlendir"],
    "SYMP:0000869": ["hidung mampet", "hidung buntu"],
    "SYMP:0000372": ["hidung meler", "ingusan"],
    "SYMP:0000139": ["bersin"],
    "SYMP:0000505": ["tenggorokan sakit", "sakit saat menelan"],
    "SYMP:0000613": ["panas", "badan panas"],
    "SYMP:0000504": ["kepala sakit"],
    "SYMP:0000024": ["ngantuk", "mengantuk"],
    "SYMP:0000610": ["pusing", "kepala terasa ringan"],
    "SYMP:0000260": ["mulut terasa kering", "haus"],
    "SYMP:0000557": ["susah kencing", "sulit kencing"],
    "SYMP:0000530": ["deg-degan", "jantung terasa berdebar"],
    "SYMP:0000529": ["denyut jantung cepat", "jantung berdetak cepat"],
    "SYMP:0000458": ["mual", "eneg"],
    "SYMP:0019145": ["muntah-muntah"],
    "SYMP:0019153": ["sulit bernapas", "napas sesak"],
    "SYMP:0000604": ["mengi", "napas ngik-ngik"],
    "SYMP:0000576": ["dada sakit", "dada terasa tertekan"],
    "SYMP:0000242": ["batuk darah", "dahak berdarah"],
    "SYMP:0020043": ["air kencing gelap", "kencing seperti teh"],
}

CURATED_SYMPTOMS = [
    # --- INDIKASI BATUK & PILEK ---
    {
        "obo_id": "SYMP:0000614",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000614",
        "label_en": "cough",
        "label_id": "Batuk",
        "kategori": "GejalaIndikasi",
        "tindak_lanjut": "Pantau",
        "deskripsi": "Refleks pertahanan saluran napas untuk membersihkan sekret atau iritan.",
    },
    {
        "obo_id": "SYMP:0000025",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000025",
        "label_en": "dry cough",
        "label_id": "Batuk kering / tidak berdahak",
        "kategori": "GejalaIndikasi",
        "tindak_lanjut": "Pantau",
        "deskripsi": "Batuk tanpa produksi dahak/mukus, sering teriritasi di tenggorokan (indikasi antitusif).",
    },
    {
        "obo_id": "SYMP:0020027",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0020027",
        "label_en": "wet cough",
        "label_id": "Batuk berdahak / produktif",
        "kategori": "GejalaIndikasi",
        "tindak_lanjut": "Pantau",
        "deskripsi": "Batuk disertai dahak kental pada saluran napas (indikasi ekspektoran/mukolitik).",
    },
    {
        "obo_id": "SYMP:0000869",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000869",
        "label_en": "nasal congestion",
        "label_id": "Hidung tersumbat",
        "kategori": "GejalaIndikasi",
        "tindak_lanjut": "Pantau",
        "deskripsi": "Penyumbatan rongga hidung akibat pembengkakan mukosa vaskular (indikasi dekongestan).",
    },
    {
        "obo_id": "SYMP:0000372",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000372",
        "label_en": "rhinorrhea",
        "label_id": "Pilek / hidung berair",
        "kategori": "GejalaIndikasi",
        "tindak_lanjut": "Pantau",
        "deskripsi": "Keluarnya cairan lendir encer dari rongga hidung (indikasi antihistamin).",
    },
    {
        "obo_id": "SYMP:0000139",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000139",
        "label_en": "sneezing",
        "label_id": "Bersin-bersin",
        "kategori": "GejalaIndikasi",
        "tindak_lanjut": "Pantau",
        "deskripsi": "Refleks pengeluaran udara tiba-tiba akibat stimulasi saraf sensorik mukosa hidung.",
    },
    {
        "obo_id": "SYMP:0000505",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000505",
        "label_en": "throat pain",
        "label_id": "Sakit tenggorokan / nyeri menelan",
        "kategori": "GejalaIndikasi",
        "tindak_lanjut": "Pantau",
        "deskripsi": "Rasa nyeri atau iritasi pada faring/laring yang sering menyertai infeksi flu saluran napas atas.",
    },
    {
        "obo_id": "SYMP:0000613",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000613",
        "label_en": "fever",
        "label_id": "Demam / suhu tubuh meningkat",
        "kategori": "GejalaIndikasi",
        "tindak_lanjut": "Pantau",
        "deskripsi": "Peningkatan suhu tubuh di atas normal akibat respon sitokin pirogen (indikasi antipiretik).",
    },
    {
        "obo_id": "SYMP:0000504",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000504",
        "label_en": "headache",
        "label_id": "Sakit kepala / pening",
        "kategori": "GejalaIndikasi",
        "tindak_lanjut": "Pantau",
        "deskripsi": "Nyeri tumpul atau berdenyut pada area kepala yang menyertai sindrom influenza/ISPA.",
    },
    # --- EFEK SAMPING OBAT BATUK-PILEK ---
    {
        "obo_id": "SYMP:0000024",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000024",
        "label_en": "drowsiness",
        "label_id": "Mengantuk / rasa kantuk berat",
        "kategori": "GejalaEfekSamping",
        "tindak_lanjut": "TanyaApoteker",
        "deskripsi": "Efek penekanan SSP dari antihistamin generasi pertama (CTM, Diphenhydramine); jangan menyetir.",
    },
    {
        "obo_id": "SYMP:0000610",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000610",
        "label_en": "dizziness",
        "label_id": "Pusing / melayang",
        "kategori": "GejalaEfekSamping",
        "tindak_lanjut": "TanyaApoteker",
        "deskripsi": "Sensasi ketidakseimbangan atau kepala ringan akibat efek vaskular atau sedasi obat flu.",
    },
    {
        "obo_id": "SYMP:0000260",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000260",
        "label_en": "dry mouth",
        "label_id": "Mulut kering / haus",
        "kategori": "GejalaEfekSamping",
        "tindak_lanjut": "Pantau",
        "deskripsi": "Penurunan sekresi saliva akibat blokade reseptor muskarinik perifer oleh antihistamin.",
    },
    {
        "obo_id": "SYMP:0000557",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000557",
        "label_en": "urinary retention",
        "label_id": "Sulit buang air kecil / retensi urin",
        "kategori": "GejalaEfekSamping",
        "tindak_lanjut": "TanyaApoteker",
        "deskripsi": "Hambatan pengosongan kandung kemih karena efek antikolinergik (waspada pasien BPH/prostat).",
    },
    {
        "obo_id": "SYMP:0000530",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000530",
        "label_en": "palpitation",
        "label_id": "Jantung berdebar-debar",
        "kategori": "GejalaEfekSamping",
        "tindak_lanjut": "TanyaApoteker",
        "deskripsi": "Sensasi denyut jantung cepat/kuat akibat stimulasi adrenergik alfa/beta dari dekongestan.",
    },
    {
        "obo_id": "SYMP:0000529",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000529",
        "label_en": "tachycardia",
        "label_id": "Denyut jantung terlalu cepat",
        "kategori": "GejalaEfekSamping",
        "tindak_lanjut": "TanyaApoteker",
        "deskripsi": "Frekuensi nadi istirahat >100 bpm; risiko meningkat bila dekongestan dikombinasikan dengan kafein.",
    },
    {
        "obo_id": "SYMP:0000458",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000458",
        "label_en": "nausea",
        "label_id": "Mual / eneg di ulu hati",
        "kategori": "GejalaEfekSamping",
        "tindak_lanjut": "Pantau",
        "deskripsi": "Iritasi mukosa lambung akibat obat ekspektoran (Guaifenesin) atau analgesik (Ibuprofen).",
    },
    {
        "obo_id": "SYMP:0019145",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0019145",
        "label_en": "vomiting",
        "label_id": "Muntah",
        "kategori": "GejalaEfekSamping",
        "tindak_lanjut": "TanyaApoteker",
        "deskripsi": "Pengeluaran isi lambung paksa; bila berulang hentikan konsumsi obat dan konsultasi apoteker.",
    },
    # --- RED FLAGS / TANDA BAHAYA (SEGERA KE DOKTER) ---
    {
        "obo_id": "SYMP:0019153",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0019153",
        "label_en": "dyspnea",
        "label_id": "Sesak napas / kesulitan bernapas",
        "kategori": "GejalaRedFlag",
        "tindak_lanjut": "SegeraKeDokter",
        "deskripsi": "Tanda bahaya gawat darurat infeksi saluran napas bawah (pneumonia/asma berat); rujuk segera.",
    },
    {
        "obo_id": "SYMP:0000604",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000604",
        "label_en": "wheezing",
        "label_id": "Napas berbunyi mengi / ngik-ngik",
        "kategori": "GejalaRedFlag",
        "tindak_lanjut": "SegeraKeDokter",
        "deskripsi": "Suara napas berfrekuensi tinggi akibat penyempitan lumen bronkus; butuh evaluasi medis.",
    },
    {
        "obo_id": "SYMP:0000576",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000576",
        "label_en": "chest pain",
        "label_id": "Nyeri dada / dada terasa tertekan",
        "kategori": "GejalaRedFlag",
        "tindak_lanjut": "SegeraKeDokter",
        "deskripsi": "Nyeri atau rasa sesak berat di dada; perlu disingkirkan komplikasi kardiovaskular/pleuritis.",
    },
    {
        "obo_id": "SYMP:0000242",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0000242",
        "label_en": "cough with bloody sputum",
        "label_id": "Batuk berdarah / dahak bercampur darah",
        "kategori": "GejalaRedFlag",
        "tindak_lanjut": "SegeraKeDokter",
        "deskripsi": "Hemoptisis; indikasi infeksi parenkim paru serius (mis. TBC, pneumonia berat) bukan batuk biasa.",
    },
    {
        "obo_id": "SYMP:0020043",
        "iri": "http://purl.obolibrary.org/obo/SYMP_0020043",
        "label_en": "dark urine",
        "label_id": "Urin berwarna gelap pekat seperti teh",
        "kategori": "GejalaRedFlag",
        "tindak_lanjut": "SegeraKeDokter",
        "deskripsi": "Tanda toksisitas mioglobinuria/rhabdomyolysis atau hepatotoksisitas berat akibat interaksi obat.",
    },
]


def write_seed_file(seed_path: Path) -> list[str]:
    iris = [item["iri"] for item in CURATED_SYMPTOMS]
    seed_path.write_text("\n".join(iris) + "\n", encoding="utf-8")
    print(f"Wrote {len(iris)} seeds to {seed_path}")
    return iris


def extract_symp_mireot(input_symp: Path, seed_file: Path, raw_extracted_owl: Path) -> None:
    print(f"Extracting MIREOT module from {input_symp}...")
    cmd = [
        "java", "-Xmx8G", "-jar", str(ROBOT_JAR),
        "extract",
        "--method", "MIREOT",
        "--input", str(input_symp),
        "--upper-term", "http://purl.obolibrary.org/obo/SYMP_0000462",
        "--lower-terms", str(seed_file),
        "--output", str(raw_extracted_owl)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"ROBOT extract failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")
    print(f"Successfully extracted {raw_extracted_owl} ({raw_extracted_owl.stat().st_size:,} bytes)")


def enrich_and_format_owl(raw_owl: Path, final_owl: Path) -> None:
    print(f"Enriching annotations into {final_owl}...")
    tree = ET.parse(raw_owl)
    root = tree.getroot()

    ns = {
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "owl": "http://www.w3.org/2002/07/owl#",
        "obo": "http://purl.obolibrary.org/obo/",
        "oboInOwl": "http://www.geneontology.org/formats/oboInOwl#",
        "skos": "http://www.w3.org/2004/02/skos/core#",
    }
    ET.register_namespace("skos", "http://www.w3.org/2004/02/skos/core#")
    ET.register_namespace("obo", "http://purl.obolibrary.org/obo/")
    ET.register_namespace("oboInOwl", "http://www.geneontology.org/formats/oboInOwl#")

    # Update ontology IRI
    ont_elem = root.find("owl:Ontology", ns)
    if ont_elem is not None:
        ont_elem.attrib[f"{{{ns['rdf']}}}about"] = ONTOLOGY_IRI
        # Add comment
        comment = ET.SubElement(ont_elem, f"{{{ns['rdfs']}}}comment")
        comment.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = "en"
        comment.text = "MIREOT extract of symptoms for cough & cold clinical decision support from Symptom Ontology (SYMP)."

    # Annotation properties declarations
    for property_name in ("altLabel", "note"):
        annotation_property = ET.Element(f"{{{ns['owl']}}}AnnotationProperty")
        annotation_property.attrib[f"{{{ns['rdf']}}}about"] = f"http://www.w3.org/2004/02/skos/core#{property_name}"
        root.append(annotation_property)

    symptom_map = {item["iri"]: item for item in CURATED_SYMPTOMS}

    for cls in root.findall(".//owl:Class", ns):
        about = cls.attrib.get(f"{{{ns['rdf']}}}about", "")
        if about in symptom_map:
            info = symptom_map[about]
            for label in [info["label_id"], *LAY_SYMPTOM_SYNONYMS[info["obo_id"]]]:
                alt_lbl = ET.SubElement(cls, f"{{{ns['skos']}}}altLabel")
                alt_lbl.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = "id"
                alt_lbl.text = label

            # Add comment with category, triage, and description
            desc_comment = ET.SubElement(cls, f"{{{ns['rdfs']}}}comment")
            desc_comment.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = "id"
            desc_comment.text = f"[{info['kategori']}] Rekomendasi: {info['tindak_lanjut']}. {info['deskripsi']}"
            note = ET.SubElement(cls, f"{{{ns['skos']}}}note")
            note.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = "id"
            note.text = "Sinonim awam adalah draf dan perlu validasi apoteker."

    tree.write(final_owl, encoding="utf-8", xml_declaration=True)
    print(f"Final annotated OWL written to {final_owl} ({final_owl.stat().st_size:,} bytes)")


def validate_owl(final_owl: Path) -> None:
    print(f"Validating {final_owl} with HermiT reasoner & OWL 2 DL profile...")
    cmd = [
        "java", "-Xmx8G", "-jar", str(ROBOT_JAR),
        "reason",
        "--reasoner", "HermiT",
        "--input", str(final_owl),
        "validate-profile",
        "--profile", "DL"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or "in profile" not in res.stdout:
        raise RuntimeError(f"Validation failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")
    print("Validation PASSED: HermiT consistent, OWL 2 DL profile verified.")


def export_csv(csv_path: Path) -> None:
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "obo_id", "iri", "label_en", "label_id", "kategori", "tindak_lanjut",
                "deskripsi", "cakupan_v1", "sinonim_awam", "status_sinonim",
            ]
        )
        writer.writeheader()
        for item in CURATED_SYMPTOMS:
            row = dict(item)
            row["cakupan_v1"] = "pilot" if item["obo_id"] in PILOT_SYMPTOM_IDS else "tambahan"
            row["sinonim_awam"] = "|".join(LAY_SYMPTOM_SYNONYMS[item["obo_id"]])
            row["status_sinonim"] = "draf_perlu_validasi_apoteker"
            writer.writerow(row)
    print(f"Exported CSV summary to {csv_path}")


def export_metadata(meta_path: Path, final_owl: Path) -> None:
    metadata = {
        "source": "Symptom Ontology (SYMP) - releases/2026-07-30",
        "input_file": "KB/symp.owl",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "scope": "22 curated symptoms; 15 selected for pilot v1. Lay synonyms are drafts pending pharmacist validation.",
        "categories": {
            "GejalaIndikasi": 9,
            "GejalaEfekSamping": 8,
            "GejalaRedFlag": 5,
        },
        "pilot_v1_count": len(PILOT_SYMPTOM_IDS),
        "triage_actions": {
            "Pantau": 11,
            "TanyaApoteker": 6,
            "SegeraKeDokter": 5,
        },
        "ontology_iri": ONTOLOGY_IRI,
        "owl_output": str(final_owl.relative_to(final_owl.parent.parent)).replace("\\", "/"),
        "owl_size_bytes": final_owl.stat().st_size,
    }
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Exported metadata to {meta_path}")


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    kb_symp = project_root / "KB" / "symp.owl"
    data_dir = project_root / "data" / "symptoms"
    out_dir = project_root / "out"

    data_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    seed_file = data_dir / "seed_symptom_terms.txt"
    raw_extracted = data_dir / "symptom_raw_mireot.owl"
    final_owl = out_dir / "symptom_modul.owl"
    csv_path = data_dir / "symptoms_selected.csv"
    meta_path = data_dir / "source_metadata.json"

    write_seed_file(seed_file)
    extract_symp_mireot(kb_symp, seed_file, raw_extracted)
    enrich_and_format_owl(raw_extracted, final_owl)
    validate_owl(final_owl)
    export_csv(csv_path)
    export_metadata(meta_path, final_owl)

    # Clean temporary files
    if raw_extracted.exists():
        raw_extracted.unlink()

    print("\n[SUCCESS] Pipeline collect_symptoms.py completed successfully!")


if __name__ == "__main__":
    main()
