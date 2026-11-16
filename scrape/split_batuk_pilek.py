"""
Memisahkan dataset produk apotek menjadi dua file CSV terpisah di data/apotek/:
1. produk_batuk.csv : Produk dengan indikasi batuk (antitusif, ekspektoran, mukolitik, batuk kering/berdahak)
2. produk_pilek.csv : Produk dengan indikasi pilek/flu (dekongestan, antihistamin, rinitis, bersin, hidung tersumbat)

Catatan: Produk kombinasi flu & batuk (multi-komposisi) akan masuk ke kedua file secara sah
karena memiliki indikasi dan zat aktif ganda untuk batuk sekaligus pilek.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APOTEK_DIR = PROJECT_ROOT / "data" / "apotek"
INPUT_CSV = APOTEK_DIR / "produk_detail.csv"

# Kata kunci & zat aktif indikasi BATUK
BATUK_PATTERNS = [
    r"\bbatuk\b", r"\bcough\b", r"\bantitusif\b", r"\bekspektoran\b", r"\bmukolitik\b",
    r"\bdextromethorphan\b", r"\bbromhexine\b", r"\bguaifenesin\b", r"\bgliseril\s+guaiakolat\b",
    r"\bgg\b", r"\bsiladex\b", r"\bbisolvon\b", r"\bwoods\b", r"\bkomix\b", r"\bobh\b",
    r"\bvicks\b", r"\bhufagripp\s+(?:bp|flu)\b", r"\blasal\b", r"\bmucos\b", r"\bepexol\b",
    r"\bambroxol\b", r"\bacetylcysteine\b"
]

# Kata kunci & zat aktif indikasi PILEK / FLU / RINITIS / HIDUNG TERSUMBAT
PILEK_PATTERNS = [
    r"\bpilek\b", r"\bflu\b", r"\bcold\b", r"\brhinitis\b", r"\brinitis\b", r"\bhidung\b",
    r"\bbersin\b", r"\bsinus\b", r"\bcongestion\b", r"\bdekongestan\b", r"\bdecongestant\b",
    r"\bpseudoephedrine\b", r"\bphenylephrine\b", r"\bchlorpheniramine\b", r"\bctm\b",
    r"\bdiphenhydramine\b", r"\bcetirizine\b", r"\bloratadine\b", r"\bactifed\b", r"\brhinos\b",
    r"\bneozep\b", r"\bdecolgen\b", r"\bmixagrip\b", r"\bprocold\b", r"\bparatusin\b",
    r"\bultraflu\b", r"\bdemacolin\b", r"\bhufagripp\s+(?:pilek|flu)\b", r"\bpanadol\s+cold\b",
    r"\bbodrex\s+flu\b", r"\bnalgestan\b"
]

RE_BATUK = re.compile("|".join(BATUK_PATTERNS), re.IGNORECASE)
RE_PILEK = re.compile("|".join(PILEK_PATTERNS), re.IGNORECASE)


def matches(text: str, regex: re.Pattern) -> bool:
    return bool(regex.search(text))


def main() -> None:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"File {INPUT_CSV} tidak ditemukan.")

    with INPUT_CSV.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        all_products = list(reader)

    produk_batuk = []
    produk_pilek = []
    produk_kombinasi = []

    for row in all_products:
        # Gabungkan teks pencarian: nama + komposisi + keywords + slug
        search_blob = f"{row.get('nama', '')} {row.get('komposisi', '')} {row.get('keywords', '')} {row.get('slug', '')}"

        is_batuk = matches(search_blob, RE_BATUK)
        is_pilek = matches(search_blob, RE_PILEK)

        if is_batuk:
            # Beri tag kategori batuk
            row_copy = dict(row)
            row_copy["tipe_kategori"] = "Batuk & Kombinasi" if is_pilek else "Batuk Murni"
            produk_batuk.append(row_copy)

        if is_pilek:
            # Beri tag kategori pilek
            row_copy = dict(row)
            row_copy["tipe_kategori"] = "Pilek/Flu & Kombinasi" if is_batuk else "Pilek/Flu Murni"
            produk_pilek.append(row_copy)

        if is_batuk and is_pilek:
            produk_kombinasi.append(row)

    # Simpan produk_batuk.csv
    batuk_csv = APOTEK_DIR / "produk_batuk.csv"
    fieldnames = list(all_products[0].keys()) + ["tipe_kategori"]
    with batuk_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(produk_batuk)

    # Simpan produk_pilek.csv
    pilek_csv = APOTEK_DIR / "produk_pilek.csv"
    with pilek_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(produk_pilek)

    # Simpan metadata
    metadata = {
        "source_file": str(INPUT_CSV.name),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_produk_input": len(all_products),
        "total_produk_batuk": len(produk_batuk),
        "total_produk_pilek": len(produk_pilek),
        "total_produk_kombinasi_flu_batuk": len(produk_kombinasi),
        "files_generated": [
            str(batuk_csv.name),
            str(pilek_csv.name),
        ],
    }
    meta_json = APOTEK_DIR / "metadata_split_batuk_pilek.json"
    meta_json.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=========================================================")
    print("   PEMISAHAN PRODUK BATUK & PILEK APOTEK INDONESIA       ")
    print("=========================================================")
    print(f"Total produk input             : {len(all_products):,} produk")
    print(f"Produk terdeteksi BATUK        : {len(produk_batuk):,} produk -> {batuk_csv}")
    print(f"Produk terdeteksi PILEK / FLU  : {len(produk_pilek):,} produk -> {pilek_csv}")
    print(f"Kombinasi Batuk + Pilek (Irisan): {len(produk_kombinasi):,} produk (termasuk di kedua file)")
    print("=========================================================")


if __name__ == "__main__":
    main()
