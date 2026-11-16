"""
Scraper menyeluruh katalog obat apotek Indonesia dari K24Klik.

Tahap 1 (listing): untuk setiap kata kunci zat aktif/merk, telusuri ?page=1,2,3...
                   sampai tidak ada produk baru. Hasil: data/apotek/listing.csv
Tahap 2 (detail) : buka halaman detail tiap produk untuk komposisi, golongan, pabrik,
                   NIE (nomor izin edar BPOM), kemasan, harga. Hasil: data/apotek/produk_detail.csv

Fitur: resumable (cache di data/apotek/cache/), paralel terbatas, jeda sopan, retry.
Tidak melewati captcha / anti-bot apa pun; jika diblokir, skrip berhenti dan melapor.

Contoh:
  python scrape/scrape_apotek_full.py --stage listing
  python scrape/scrape_apotek_full.py --stage detail --workers 4
  python scrape/scrape_apotek_full.py --stage listing --keywords paracetamol ibuprofen --max-pages 3
"""

from __future__ import annotations

import argparse
import csv
import html as htmllib
import json
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://www.k24klik.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "id-ID,id;q=0.9,en;q=0.7",
}
CTX = ssl.create_default_context()

# Zat aktif (generik) + merk/kategori batuk-pilek & herbal. Tambah sendiri di sini bila perlu.
DEFAULT_KEYWORDS = [
    # batuk-pilek & pereda gejala
    "paracetamol", "ibuprofen", "dextromethorphan", "pseudoephedrine", "phenylephrine",
    "chlorpheniramine", "diphenhydramine", "cetirizine", "loratadine", "bromhexine",
    "ambroxol", "guaifenesin", "acetylcysteine", "salbutamol", "OBH", "batuk", "flu", "pilek",
    "actifed", "siladex", "bisolvon", "panadol", "bodrex", "mixagrip", "decolgen", "komix",
    # variasi agar melewati batas ~66 hasil/kata kunci
    "sirup batuk", "sirup flu", "obat batuk berdahak", "obat batuk kering", "obat flu",
    "paracetamol sirup", "paracetamol tablet", "ibuprofen sirup", "vicks", "woods", "hufagrip",
    "procold", "paratusin", "decolsin", "rhinos", "neozep", "oskadon", "ultraflu", "lasal",
    "thrombophob", "mucos", "epexol", "sanmol", "tempra", "termorex", "demacolin",
    # obat kronis / pembanding interaksi
    "amlodipine", "captopril", "simvastatin", "atorvastatin", "metformin", "glimepiride",
    "warfarin", "clopidogrel", "digoxin", "omeprazole", "ciprofloxacin", "amoxicillin",
    "itraconazole", "ketoconazole", "fluconazole",
    # herbal
    "kulit manggis", "kunyit", "curcuma", "jahe", "tolak angin", "antangin",
]

FIELDS_LISTING = ["keyword", "slug", "nama_dari_slug", "url", "halaman"]
FIELDS_DETAIL = ["slug", "nama", "komposisi", "golongan", "pabrik", "nie_bpom", "kemasan",
                 "harga_rp", "url", "keywords", "status"]


class EndOfResults(Exception):
    """Halaman di luar batas hasil pencarian (HTTP 404) - bukan error."""


def fetch(url: str, timeout: int = 60, retries: int = 2) -> str:
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise EndOfResults(url) from e
            if e.code in (403, 429):
                raise RuntimeError(f"DIBLOKIR HTTP {e.code} di {url} - berhenti, jangan dipaksa.") from e
            last = e
        except Exception as e:  # timeout / koneksi
            last = e
        time.sleep(2 + attempt * 3)
    raise RuntimeError(f"gagal {url}: {last}")


def slug_to_title(slug: str) -> str:
    s = re.sub(r"-\d+$", "", slug)
    return " ".join(w.capitalize() for w in s.split("-"))


BAD = ("troli", "cart", "keranjang", "login", "register", "bantuan", "artikel")


def listing_slugs(html: str) -> list[str]:
    seen, out = set(), []
    for slug in re.findall(r'/p/([^/"\'?\s<>]+)', html):
        k = slug.lower()
        if k in seen or any(b in k for b in BAD):
            continue
        seen.add(k)
        out.append(slug)
    return out


def crawl_keyword(keyword: str, max_pages: int, delay: float, cache_dir: Path) -> list[dict]:
    rows, known = [], set()
    for page in range(1, max_pages + 1):
        cache = cache_dir / f"list_{re.sub(r'[^a-z0-9]+', '_', keyword.lower())}_{page}.json"
        if cache.exists():
            slugs = json.loads(cache.read_text(encoding="utf-8"))
        else:
            url = f"{BASE}/cariObat/{urllib.parse.quote(keyword)}" + (f"?page={page}" if page > 1 else "")
            try:
                page_html = fetch(url)
            except EndOfResults:
                break
            slugs = listing_slugs(page_html)
            if not slugs and page == 1 and "obat keras" in page_html.lower():
                print(f"  [{keyword}] disembunyikan sumber (obat keras/resep, Permenkes) -> 0 produk", flush=True)
            cache.write_text(json.dumps(slugs), encoding="utf-8")
            time.sleep(delay)
        new = [s for s in slugs if s.lower() not in known]
        if not new:
            break
        for s in new:
            known.add(s.lower())
            rows.append({"keyword": keyword, "slug": s, "nama_dari_slug": slug_to_title(s),
                         "url": f"{BASE}/p/{s}", "halaman": page})
        print(f"  [{keyword}] hal {page}: +{len(new)} (total {len(rows)})", flush=True)
    return rows


def run_listing(keywords, max_pages, delay, out_dir: Path) -> None:
    cache_dir = out_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    all_rows = []
    for kw in keywords:
        print(f"[*] listing: {kw}", flush=True)
        try:
            all_rows.extend(crawl_keyword(kw, max_pages, delay, cache_dir))
        except RuntimeError as e:
            print(f"  ! {e}", flush=True)
            if "DIBLOKIR" in str(e):
                break
    path = out_dir / "listing.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS_LISTING)
        w.writeheader()
        w.writerows(all_rows)
    uniq = len({r["slug"].lower() for r in all_rows})
    print(f"[OK] listing: {len(all_rows)} baris, {uniq} produk unik -> {path}")


def text_after(html: str, label: str, span: int = 400) -> str:
    m = re.search(re.escape(label), html)
    if not m:
        return ""
    chunk = html[m.end(): m.end() + span]
    img = re.search(r'alt="([^"]+)"', chunk[:200]) if label.startswith("Golongan") else None
    if img:
        return htmllib.unescape(img.group(1)).strip()
    chunk = re.sub(r"<[^>]+>", "\n", chunk)
    for line in chunk.splitlines():
        line = htmllib.unescape(line).strip(" :\t\r")
        if line:
            return line
    return ""


def parse_detail(slug: str, html: str) -> dict:
    og = re.search(r'property="og:title" content="([^"]+)"', html)
    title = htmllib.unescape(og.group(1)).strip() if og else slug_to_title(slug)
    harga = re.search(r"Harga Rp\s?([\d\.]+)", html)
    return {
        "slug": slug,
        "nama": title,
        "komposisi": text_after(html, "Komposisi:"),
        "golongan": text_after(html, "Golongan Obat:"),
        "pabrik": text_after(html, "Pabrik:"),
        "nie_bpom": text_after(html, "Nomor Izin Edar:"),
        "kemasan": text_after(html, "Kemasan:"),
        "harga_rp": harga.group(1).replace(".", "") if harga else "",
        "url": f"{BASE}/p/{slug}",
    }


def detail_one(slug: str, cache_dir: Path, delay: float) -> dict:
    cache = cache_dir / f"detail_{slug[:150]}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    row = parse_detail(slug, fetch(f"{BASE}/p/{slug}", timeout=90))
    row["status"] = "ok"
    cache.write_text(json.dumps(row, ensure_ascii=False), encoding="utf-8")
    time.sleep(delay)
    return row


def run_detail(workers: int, delay: float, limit: int | None, out_dir: Path) -> None:
    cache_dir = out_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    listing = out_dir / "listing.csv"
    if not listing.exists():
        sys.exit("listing.csv belum ada. Jalankan --stage listing dulu.")
    kw_by_slug: dict[str, set[str]] = {}
    with listing.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            kw_by_slug.setdefault(r["slug"], set()).add(r["keyword"])
    slugs = list(kw_by_slug)[: limit or None]
    print(f"[*] detail: {len(slugs)} produk, {workers} worker", flush=True)

    rows, done, blocked = [], 0, False
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(detail_one, s, cache_dir, delay): s for s in slugs}
        for fut in as_completed(futs):
            s = futs[fut]
            try:
                row = fut.result()
            except Exception as e:
                row = {"slug": s, "url": f"{BASE}/p/{s}", "status": f"gagal: {e}"}
                if "DIBLOKIR" in str(e):
                    blocked = True
                    for pending in futs:
                        pending.cancel()
            row["keywords"] = "|".join(sorted(kw_by_slug[s]))
            rows.append(row)
            done += 1
            if done % 25 == 0:
                print(f"  {done}/{len(slugs)}", flush=True)
            if blocked:
                break

    path = out_dir / "produk_detail.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS_DETAIL, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    ok = sum(1 for r in rows if r.get("status") == "ok")
    meta = {"source": "K24Klik (www.k24klik.com)", "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "produk_total": len(rows), "produk_ok": ok, "diblokir": blocked}
    (out_dir / "source_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[OK] detail: {ok}/{len(rows)} berhasil -> {path}" + ("  (BERHENTI: diblokir)" if blocked else ""))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["listing", "detail"], required=True)
    ap.add_argument("--keywords", nargs="*", default=None)
    ap.add_argument("--max-pages", type=int, default=30)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--limit", type=int, default=None, help="batasi jumlah produk (uji coba)")
    a = ap.parse_args()

    out_dir = Path(__file__).resolve().parent.parent / "data" / "apotek"
    out_dir.mkdir(parents=True, exist_ok=True)
    if a.stage == "listing":
        run_listing(a.keywords or DEFAULT_KEYWORDS, a.max_pages, a.delay, out_dir)
    else:
        run_detail(a.workers, a.delay, a.limit, out_dir)


if __name__ == "__main__":
    main()
