"""
Script Scraper Obat Apotek Indonesia (K24Klik) - Versi Diperbarui
Tujuan: Mengambil data nama obat/produk komersial yang dijual di Apotek K-24 (K24Klik),
        menghindari tautan troli/keranjang, dan mengekstrak nama merk dagang nyata.
"""

import urllib.request
import urllib.parse
import re
import csv
import time

KEYWORDS = [
    "amlodipine", "captopril", "simvastatin", "metformin", "glimepiride",
    "omeprazole", "paracetamol", "ibuprofen", "ciprofloxacin", "amoxicillin",
    "warfarin", "digoxin", "kulit manggis", "curcumin", "jahe"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
}

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleaned = re.sub(cleanr, ' ', raw_html)
    return ' '.join(cleaned.split()).strip()

def slug_to_title(slug):
    # Hapus kode angka ID di akhir slug (misal: -34322)
    slug_clean = re.sub(r'-\d+$', '', slug)
    parts = slug_clean.split('-')
    words = []
    for w in parts:
        if re.match(r'^\d+[a-zA-Z]+$', w):
            words.append(w.upper())
        elif w.lower() in ["kf", "ogb", "if", "dexa", "pt"]:
            words.append(w.upper())
        else:
            words.append(w.capitalize())
    return ' '.join(words)

def scrape_k24(keyword):
    print(f"[*] Mencari obat di Apotek K-24 untuk: '{keyword}'...")
    encoded_kw = urllib.parse.quote(keyword)
    url = f"https://www.k24klik.com/cariObat/{encoded_kw}"
    
    req = urllib.request.Request(url, headers=HEADERS)
    results = []
    
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # K24Klik menyimpan URL detail produk dengan format: /p/nama-produk-id
            # Pola 1: Mencari tautan /p/... lengkap dengan title attribute atau inner text
            raw_links = re.findall(
                r'<a[^>]+href=[\'"](?:https://www\.k24klik\.com)?/p/([^/\"\'\?]+)[\'"]([^>]*)>(.*?)</a>',
                html, re.DOTALL | re.IGNORECASE
            )
            
            seen_slugs = set()
            count = 0
            
            for slug, attrs, inner in raw_links:
                slug_lower = slug.lower().strip()
                if not slug_lower or slug_lower in seen_slugs:
                    continue
                
                # Filter kata-kata tombol sistem navigasi
                if any(x in slug_lower for x in ["troli", "cart", "keranjang", "login", "register", "bantuan", "artikel"]):
                    continue
                
                seen_slugs.add(slug_lower)
                
                # Coba cari nama produk dari title attribute di dalam <a>
                title_match = re.search(r'title=[\'"]([^\'"]+)[\'"]', attrs, re.IGNORECASE)
                product_name = ""
                
                if title_match:
                    candidate = title_match.group(1).strip()
                    if candidate and "lihat" not in candidate.lower() and "keranjang" not in candidate.lower():
                        product_name = candidate
                
                # Jika tidak ada di title, coba bersihkan dari inner text
                if not product_name:
                    inner_clean = clean_html(inner)
                    # Pastikan bukan teks keranjang / beli
                    if inner_clean and len(inner_clean) > 3 and not any(x in inner_clean.lower() for x in ["keranjang", "beli", "troli", "rp", "lihat"]):
                        product_name = inner_clean
                
                # Jika masih kosong, ubah slug URL menjadi nama resmi obat
                if not product_name:
                    product_name = slug_to_title(slug)
                    
                full_url = f"https://www.k24klik.com/p/{slug}"
                
                results.append({
                    "keyword_pencarian": keyword,
                    "nama_produk_apotek": product_name,
                    "zat_aktif_terkait": keyword.title(),
                    "url_produk": full_url,
                    "sumber": "Apotek K-24 (K24Klik)"
                })
                count += 1
                if count >= 6: # Ambil 6 produk terpopuler per zat aktif
                    break
                    
            print(f"    -> Berhasil mengekstrak {len(results)} produk riil untuk '{keyword}'.")
            
    except Exception as e:
        print(f"    Gagal mengambil data untuk {keyword}: {e}")
        
    return results

def main():
    all_data = []
    print("=========================================================")
    print("   SCRAPER DATASET OBAT APOTEK INDONESIA (K24Klik v2)    ")
    print("=========================================================")
    
    for kw in KEYWORDS:
        items = scrape_k24(kw)
        all_data.extend(items)
        time.sleep(1.2)
        
    output_file = "dataset_obat_apotek_indonesia.csv"
    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = ["keyword_pencarian", "nama_produk_apotek", "zat_aktif_terkait", "url_produk", "sumber"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)
        
    print("\n=========================================================")
    print(f"[SUKSES] Total {len(all_data)} produk obat apotek berhasil dikumpulkan!")
    print(f"[FILE] Tersimpan di: {output_file}")
    print("=========================================================")

if __name__ == "__main__":
    main()
