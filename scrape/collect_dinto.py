"""
Automated downloader and extractor for DINTO (Drug-Drug Interactions Ontology)
from labda/DINTO GitHub repository.

Workflow:
1. Downloads DINTO 1.2 zip from GitHub (5.8 MB).
2. Extracts DINTO_1.2.owl to data/dinto/.
3. Strips unresolvable external import line (<Import>...MF...metadata-slim.owl</Import>).
4. Extracts core DDI interaction, mechanism, role, and property terms via ROBOT MIREOT.
5. Emits out/dinto_modul.owl and validates OWL 2 DL profile & HermiT reasoner.
6. Exports structured CSV summary and metadata provenance.
"""

from __future__ import annotations

import csv
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

DINTO_ZIP_URL = "https://raw.githubusercontent.com/labda/DINTO/master/DINTO1.2/DINTO_1.2.owl.zip"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ProjectKBR-Group4"
ROBOT_JAR = Path(os.environ.get("ROBOT_JAR", "robot.jar"))
ONTOLOGY_IRI = "http://purl.obolibrary.org/obo/kbr-group4/dinto_modul.owl"

CORE_TERMS = [
    # Core DDI & Mechanisms
    ("http://purl.obolibrary.org/obo/DINTO_000001", "DINTO:000001", "DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000002", "DINTO:000002", "drug interaction", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000003", "DINTO:000003", "DDI mechanism", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000004", "DINTO:000004", "pharmacokinetic DDI mechanism", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000005", "DINTO:000005", "pharmacodynamic DDI mechanism", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000006", "DINTO:000006", "non-clinically relevant DDI effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000007", "DINTO:000007", "unobservable DDI effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000008", "DINTO:000008", "uncertain DDI effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000009", "DINTO:000009", "clinically relevant DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000010", "DINTO:000010", "potentially beneficial DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000011", "DINTO:000011", "potentially harmful DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000012", "DINTO:000012", "non-clinically relevant DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000013", "DINTO:000013", "uncertain DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000018", "DINTO:000018", "agonistic DDI mechanism", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000019", "DINTO:000019", "antagonistic DDI mechanism", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000020", "DINTO:000020", "pharmacokinetic DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000021", "DINTO:000021", "pharmacodynamic DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000022", "DINTO:000022", "target activity alteration", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000023", "DINTO:000023", "participant", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000024", "DINTO:000024", "precipitant", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000025", "DINTO:000025", "object", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000026", "DINTO:000026", "DDI effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000027", "DINTO:000027", "clinically relevant DDI effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000028", "DINTO:000028", "beneficial DDI effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000029", "DINTO:000029", "harmful DDI effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000030", "DINTO:000030", "pharmacokinetic process", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000031", "DINTO:000031", "absorption", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000032", "DINTO:000032", "distribution", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000033", "DINTO:000033", "drug metabolism", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000034", "DINTO:000034", "excretion", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000035", "DINTO:000035", "physiological effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000036", "DINTO:000036", "therapeutic effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000037", "DINTO:000037", "toxic effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000043", "DINTO:000043", "altered physiological effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000044", "DINTO:000044", "altered adverse effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000045", "DINTO:000045", "increased adverse effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000046", "DINTO:000046", "decreased adverse effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000047", "DINTO:000047", "altered toxic effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000048", "DINTO:000048", "increased toxic effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000049", "DINTO:000049", "decreased toxic effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000050", "DINTO:000050", "altered therapeutic effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000051", "DINTO:000051", "increased therapeutic effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000052", "DINTO:000052", "decreased therapeutic effect", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000055", "DINTO:000055", "pharmacological entity", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000071", "DINTO:000071", "physiological effect potentiation", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000072", "DINTO:000072", "physiological effect alteration", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000073", "DINTO:000073", "physiological effect antagonism", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_0001", "DINTO:0001", "enzyme related DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000124", "DINTO:000124", "enzyme activity alteration", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000128", "DINTO:000128", "target", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000130", "DINTO:000130", "enzyme", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000133", "DINTO:000133", "transporter", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000155", "DINTO:000155", "transporter activity alteration", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000167", "DINTO:000167", "transporter activity induction", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000168", "DINTO:000168", "transporter activity inhibition", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000169", "DINTO:000169", "enzyme induction DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000170", "DINTO:000170", "enzyme inhibition DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000171", "DINTO:000171", "transporter induction DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_000172", "DINTO:000172", "transporter inhibition DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_4325", "DINTO:4325", "carrier activity alteration", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_4326", "DINTO:4326", "agonistic DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_4327", "DINTO:4327", "carrier activity induction", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_4328", "DINTO:4328", "carrier activity inhibition", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_4329", "DINTO:4329", "carrier related DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_4330", "DINTO:4330", "antagonistic DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_4331", "DINTO:4331", "transporter related DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_4332", "DINTO:4332", "target related DDI", "Class"),
    ("http://purl.obolibrary.org/obo/DINTO_4336", "DINTO:4336", "receptor", "Class"),
    # Core Object Properties
    ("http://purl.obolibrary.org/obo/DINTO_000136", "DINTO:000136", "has participant", "ObjectProperty"),
    ("http://purl.obolibrary.org/obo/DINTO_000137", "DINTO:000137", "has precipitant", "ObjectProperty"),
    ("http://purl.obolibrary.org/obo/DINTO_000138", "DINTO:000138", "has object", "ObjectProperty"),
    ("http://purl.obolibrary.org/obo/DINTO_000139", "DINTO:000139", "is participant in", "ObjectProperty"),
    ("http://purl.obolibrary.org/obo/DINTO_000140", "DINTO:000140", "is precipitant in", "ObjectProperty"),
    ("http://purl.obolibrary.org/obo/DINTO_000141", "DINTO:000141", "is object in", "ObjectProperty"),
    ("http://purl.obolibrary.org/obo/DINTO_000142", "DINTO:000142", "precedes", "ObjectProperty"),
    ("http://purl.obolibrary.org/obo/DINTO_000143", "DINTO:000143", "is preceded by", "ObjectProperty"),
    ("http://purl.obolibrary.org/obo/DINTO_000144", "DINTO:000144", "is agent in", "ObjectProperty"),
    ("http://purl.obolibrary.org/obo/DINTO_000145", "DINTO:000145", "has agent", "ObjectProperty"),
    ("http://purl.obolibrary.org/obo/DINTO_000146", "DINTO:000146", "alters", "ObjectProperty"),
    ("http://purl.obolibrary.org/obo/DINTO_000147", "DINTO:000147", "is altered by", "ObjectProperty"),
    ("http://purl.obolibrary.org/obo/DINTO_000148", "DINTO:000148", "undergoes", "ObjectProperty"),
    ("http://purl.obolibrary.org/obo/DINTO_000159", "DINTO:000159", "has effect", "ObjectProperty"),
    ("http://purl.obolibrary.org/obo/DINTO_000160", "DINTO:000160", "is effect of", "ObjectProperty"),
    ("http://purl.obolibrary.org/obo/DINTO_000165", "DINTO:000165", "has DDI effect", "ObjectProperty"),
    ("http://purl.obolibrary.org/obo/DINTO_000166", "DINTO:000166", "is DDI effect of", "ObjectProperty"),
]


def download_dinto_zip(dest_path: Path) -> Path:
    if dest_path.exists() and dest_path.stat().st_size > 1000000:
        print(f"Zip already downloaded ({dest_path.stat().st_size:,} bytes). Skipping download.")
        return dest_path

    print(f"Downloading DINTO zip from {DINTO_ZIP_URL}...")
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(DINTO_ZIP_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, context=ctx, timeout=90) as resp:
        data = resp.read()
    dest_path.write_bytes(data)
    print(f"Downloaded {len(data):,} bytes -> {dest_path}")
    return dest_path


def extract_zip(zip_path: Path, target_dir: Path) -> Path:
    target_owl = target_dir / "DINTO_1.2.owl"
    if target_owl.exists() and target_owl.stat().st_size > 50000000:
        print(f"Extracted OWL already exists ({target_owl.stat().st_size:,} bytes).")
        return target_owl

    print(f"Extracting {zip_path} -> {target_dir}...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(target_dir)
    print("Extracted successfully.")
    return target_owl


def strip_external_import(src_owl: Path, dest_owl: Path) -> Path:
    if dest_owl.exists() and dest_owl.stat().st_size > 50000000:
        print(f"Sanitized OWL already exists ({dest_owl.stat().st_size:,} bytes).")
        return dest_owl

    print("Sanitizing external broken imports from DINTO...")
    with src_owl.open("r", encoding="utf-8", errors="ignore") as fin, \
         dest_owl.open("w", encoding="utf-8") as fout:
        for line in fin:
            if "<Import>http://purl.obolibrary.org/obo/MF/external/ontology-metadata-slim.owl</Import>" in line:
                continue
            fout.write(line)
    print(f"Sanitized OWL written to {dest_owl}")
    return dest_owl


def write_seed_terms(seed_file: Path) -> None:
    lines = [term[0] for term in CORE_TERMS]
    seed_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(lines)} seed terms to {seed_file}")


def extract_mireot_module(raw_owl: Path, seed_file: Path, out_owl: Path) -> None:
    print(f"Running ROBOT MIREOT extraction to generate {out_owl}...")
    cmd = [
        "java",
        "-Xmx8G",
        "-jar",
        str(ROBOT_JAR),
        "extract",
        "--method",
        "MIREOT",
        "--input",
        str(raw_owl),
        "--upper-term",
        "http://purl.obolibrary.org/obo/DINTO_000002",
        "--lower-terms",
        str(seed_file),
        "annotate",
        "--ontology-iri",
        ONTOLOGY_IRI,
        "--version-iri",
        f"{ONTOLOGY_IRI}/1.2",
        "--annotation",
        "rdfs:comment",
        "MIREOT extract of drug interaction mechanisms and formal DDI relations from DINTO (Drug-Drug Interactions Ontology).",
        "--output",
        str(out_owl),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"ROBOT extract failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")
    print(f"Successfully generated {out_owl} ({out_owl.stat().st_size:,} bytes)")


def validate_module(out_owl: Path) -> None:
    print("Validating out/dinto_modul.owl with HermiT reasoner & OWL 2 DL profile...")
    cmd = [
        "java",
        "-Xmx8G",
        "-jar",
        str(ROBOT_JAR),
        "reason",
        "--reasoner",
        "HermiT",
        "--input",
        str(out_owl),
        "validate-profile",
        "--profile",
        "DL",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or "in profile" not in res.stdout:
        raise RuntimeError(f"ROBOT validation failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")
    print("Validation PASSED: HermiT consistent, OWL 2 DL in profile.")


def export_csv_summary(csv_path: Path) -> None:
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["obo_id", "iri", "label", "entity_type"])
        writer.writeheader()
        for iri, obo_id, label, etype in CORE_TERMS:
            writer.writerow({
                "obo_id": obo_id,
                "iri": iri,
                "label": label,
                "entity_type": etype,
            })
    print(f"Exported CSV summary to {csv_path}")


def export_metadata(meta_path: Path, out_owl: Path) -> None:
    metadata = {
        "source": "Drug-Drug Interactions Ontology (DINTO 1.2)",
        "repository": "https://github.com/labda/DINTO",
        "zip_url": DINTO_ZIP_URL,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "scope": "DDI interaction classes, pharmacokinetic/pharmacodynamic mechanisms, participant roles, and properties",
        "ontology_iri": ONTOLOGY_IRI,
        "seed_count": len(CORE_TERMS),
        "owl_output": str(out_owl),
        "owl_size_bytes": out_owl.stat().st_size,
    }
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Exported metadata to {meta_path}")


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data" / "dinto"
    out_dir = project_root / "out"

    data_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    zip_path = data_dir / "DINTO_1.2.owl.zip"
    raw_owl = data_dir / "DINTO_1.2.owl"
    sanitized_owl = data_dir / "DINTO_1.2_noimport.owl"
    seed_file = data_dir / "seed_dinto_terms.txt"
    out_owl = out_dir / "dinto_modul.owl"
    csv_path = data_dir / "dinto_mechanisms_selected.csv"
    meta_path = data_dir / "source_metadata.json"

    download_dinto_zip(zip_path)
    extract_zip(zip_path, data_dir)
    strip_external_import(raw_owl, sanitized_owl)
    write_seed_terms(seed_file)
    extract_mireot_module(sanitized_owl, seed_file, out_owl)
    validate_module(out_owl)
    export_csv_summary(csv_path)
    export_metadata(meta_path, out_owl)

    print("\n[SUCCESS] Pipeline collect_dinto.py completed successfully!")


if __name__ == "__main__":
    main()
