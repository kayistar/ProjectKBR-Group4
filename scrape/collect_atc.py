
import requests
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timezone

# Folder output
output = Path("data/atc")
output.mkdir(parents=True, exist_ok=True)

# API klasifikasi ATC
url = "https://rxnav.nlm.nih.gov/REST/rxclass/allClasses.json"

response = requests.get(
    url,
    params={"classTypes": "ATC1-4"},
    timeout=60
)
response.raise_for_status()

data = response.json()

# Simpan respons asli
with open(output / "atc_raw.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Ambil daftar kelompok
classes = data.get("rxclassMinConceptList", {}).get(
    "rxclassMinConcept", []
)

if isinstance(classes, dict):
    classes = [classes]

df = pd.DataFrame(classes)

# Pastikan struktur sesuai
required = ["classId", "className", "classType"]
df = df[required].copy()

df = df.rename(columns={
    "classId": "atc_code",
    "className": "atc_name",
    "classType": "class_type"
})

# Hitung level dari panjang kode
levels = {1: 1, 3: 2, 4: 3, 5: 4}
df["atc_level"] = df["atc_code"].str.len().map(levels)

# Simpan seluruh kelompok
df.to_csv(
    output / "atc_all.csv",
    index=False,
    encoding="utf-8-sig"
)

# Filter kelompok respiratory system
respiratory = df[
    df["atc_code"].str.startswith("R")
].copy()

respiratory.to_csv(
    output / "atc_respiratory.csv",
    index=False,
    encoding="utf-8-sig"
)

# Metadata pengambilan
metadata = {
    "source": "NLM RxClass API",
    "url": response.url,
    "retrieved_at": datetime.now(timezone.utc).isoformat(),
    "scope": "ATC levels 1-4"
}

with open(output / "source_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print("Pengambilan data selesai!")
print("Total kelas:", len(df))
print("Kelas respiratory:", len(respiratory))
print(respiratory.head(10))
