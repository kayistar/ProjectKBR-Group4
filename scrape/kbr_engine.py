"""
kbr_engine.py
=============
Engine pendukung keputusan klinis berbasis KB v2 (Group 4 KBR) yang menjalankan
5 Task Final sesuai docs/RENCANA_KERJA.md:
  - T1: Rekomendasi terapi personal (produk + aturan pakai + peringatan + triase)
  - T2: Alternatif lebih murah (kandungan identik & perbandingan harga per unit)
  - T3: Skrining keranjang & obat rutin (dobel kandungan, dobel ATC-4, interaksi, kontraindikasi)
  - T4: Substitusi aman (ganti produk bermasalah untuk kondisi pasien)
  - T5: Kartu edukasi & explainability (markdown per produk dengan rantai bukti & batas bukti)

Path 100% relatif terhadap root repositori; hanya memakai Python standard library.
"""

import csv
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_csv(rel_path: str) -> list[dict]:
    full = os.path.join(ROOT, rel_path)
    with open(full, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


class KBRKnowledgeEngine:
    def __init__(self):
        self.zat_rows = load_csv("data/curation/sheet1_zat_aktif.csv")
        self.sinonim_rows = load_csv("data/curation/sinonim_zat.csv")
        self.aturan_map = {r["id_zat"].strip(): r for r in load_csv("data/curation/substansi_aturan_pakai.csv")}
        self.kontra_map = {r["id_zat"].strip(): r for r in load_csv("data/curation/substansi_kontraindikasi.csv")}
        self.alergi_map = {r["id_zat"].strip(): r for r in load_csv("data/curation/substansi_alergi.csv")}
        self.symp_map = {r["obo_id"].strip(): r for r in load_csv("data/symptoms/symptoms_selected.csv")}
        self.durasi_map = {r["obo_id"].strip(): r for r in load_csv("data/curation/aturan_durasi.csv")}
        self.sheet2_rows = load_csv("data/curation/sheet2_interaksi.csv")
        self.ddinter_rows = load_csv("data/interactions/ddinter_31zat_pairs.csv")
        self.evidence_rows = load_csv("data/curation/evidence_interaksi.csv")
        self.atc4_names = {
            r["atc_code"].strip(): r["atc_name"].strip()
            for r in load_csv("data/atc/atc_all.csv")
            if r["atc_level"].strip() == "4"
        }
        self.harga_map = {r["slug"].strip(): r for r in load_csv("data/apotek/harga_per_unit.csv")}
        self.excl_bad_slugs = {
            r["slug"].strip()
            for r in load_csv("data/apotek/dikecualikan.csv")
            if "komposisi_kosong" in r["alasan_pengecualian"] or "komposisi_html_korup" in r["alasan_pengecualian"]
        }

        self.zat_by_id = {r["id_zat"].strip(): r for r in self.zat_rows}
        self.zat_by_chebi = {r["chebi_id"].strip(): r["id_zat"].strip() for r in self.zat_rows}
        self.zat_by_name = {}
        for r in self.zat_rows:
            zid = r["id_zat"].strip()
            raw = r["nama_zat"].strip().lower()
            base = re.sub(r"\s*\(.*?\)", "", raw).strip()
            self.zat_by_name[raw] = zid
            self.zat_by_name[base] = zid

        # Compile synonym matchers from sinonim_zat.csv
        self.zat_patterns = []
        for s in self.sinonim_rows:
            tokens = [t.strip() for t in s["regex_komposisi"].split("|") if t.strip()]
            pat = re.compile("|".join(rf"\b{re.escape(t)}\b" for t in tokens), re.IGNORECASE)
            self.zat_patterns.append((pat, s["id_zat"].strip()))

        # Load clean cough/cold products (+ OTC antipyretic/NSAID like Ibuprofen from produk_detail.csv)
        self.products = {}
        otc_zids = {f"ZAT-{i:03d}" for i in range(1, 12)} | {"ZAT-030", "ZAT-031"}
        raw_sources = (
            load_csv("data/apotek/produk_batuk.csv")
            + load_csv("data/apotek/produk_pilek.csv")
            + load_csv("data/apotek/produk_detail.csv")
        )
        for r in raw_sources:
            slug = r["slug"].strip()
            if not slug or slug in self.excl_bad_slugs or slug in self.products:
                continue
            komp = (r.get("komposisi") or "").strip()
            zids = []
            for pat, zid in self.zat_patterns:
                if pat.search(komp) and zid not in zids:
                    zids.append(zid)
            if not zids or not any(z in otc_zids for z in zids):
                continue
            h = self.harga_map.get(slug, {})
            self.products[slug] = {
                "slug": slug,
                "nama": r["nama"].strip(),
                "komposisi": komp,
                "golongan": r.get("golongan", "").strip(),
                "pabrik": r.get("pabrik", "").strip(),
                "nie_bpom": r.get("nie_bpom", "").strip(),
                "kemasan": r.get("kemasan", "").strip(),
                "harga_rp": int(h["harga_rp"]) if str(h.get("harga_rp", "")).isdigit() else None,
                "harga_per_unit": float(h["harga_per_unit_rp"]) if h.get("harga_per_unit_rp") else None,
                "jumlah_unit": h.get("jumlah_unit", ""),
                "satuan_unit": h.get("satuan_unit", ""),
                "status_harga": h.get("status_parsing", ""),
                "zids": tuple(sorted(zids)),
                "indikasi": self._infer_product_indications(zids),
                "is_anak_product": bool(re.search(r"\b(anak|child|kids|pediatrik|baby|drop|sirup|syrup|syr)\b", r["nama"], re.IGNORECASE)),
            }

        # Index evidence by interaction id
        self.ev_by_int = defaultdict(list)
        for ev in self.evidence_rows:
            self.ev_by_int[ev["id_interaksi"].strip()].append(ev)

        # Index interactions (sheet2 curated takes precedence, then DDInter domain)
        self.interactions = {}
        for r in self.sheet2_rows:
            za = self.zat_by_chebi[r["chebi_a"].strip()]
            zb = self.zat_by_chebi[r["chebi_b"].strip()]
            key = tuple(sorted([za, zb]))
            self.interactions[key] = {
                "id": r["id"].strip(),
                "level": r["tingkat_keparahan"].strip(),
                "status": "kurasi_terverifikasi",
                "tindak_lanjut": r["tindak_lanjut"].strip(),
                "mekanisme": r["mekanisme_detail"].strip(),
                "efek": r["efek_klinis"].strip(),
                "rekomendasi": r["rekomendasi_klinis"].strip(),
                "sumber": r["sumber"].strip(),
                "tingkat_bukti": r["tingkat_bukti"].strip(),
                "bukti_records": self.ev_by_int.get(r["id"].strip(), []),
            }
        for r in self.ddinter_rows:
            key = tuple(sorted([r["id_zat_a"].strip(), r["id_zat_b"].strip()]))
            if key not in self.interactions:
                lvl = r["level_ddinter"].strip()
                self.interactions[key] = {
                    "id": f"DDINTER-{key[0]}-{key[1]}",
                    "level": lvl,
                    "status": r["status_data"].strip(),
                    "tindak_lanjut": "SegeraKeDokter" if lvl == "Major" else "TanyaApoteker",
                    "mekanisme": f"Tercatat di DDInter 2.0 ({r['sumber_file']}) dengan klasifikasi {lvl}.",
                    "efek": "Belum ada uraian mekanisme detail (tingkat keparahan dari DDInter)." if lvl != "Unknown" else "Tingkat keparahan Unknown di DDInter — jangan dianggap aman.",
                    "rekomendasi": "Konsultasikan ke apoteker/dokter sebelum digunakan bersama.",
                    "sumber": f"DDInter 2.0 ({r['sumber_file']})",
                    "tingkat_bukti": "DDInter bulk (Level only)",
                    "bukti_records": [],
                }

    def _infer_product_indications(self, zids: list[str]) -> set[str]:
        inds = set()
        for zid in zids:
            peran = (self.zat_by_id[zid].get("peran_farmakologis") or "").lower()
            if "antitusif" in peran:
                inds.update({"SYMP:0000614", "SYMP:0000025"})
            if "mukolitik" in peran or "ekspektoran" in peran:
                inds.update({"SYMP:0000614", "SYMP:0020027"})
            if "dekongestan" in peran:
                inds.add("SYMP:0000869")
            if "antihistamin" in peran:
                inds.update({"SYMP:0000372", "SYMP:0000139"})
            if "antipiretik" in peran or "analgesik" in peran:
                inds.update({"SYMP:0000613", "SYMP:0000504", "SYMP:0000505"})
        return inds

    def find_product(self, query: str) -> dict | None:
        q = query.strip().lower()
        if query in self.products:
            return self.products[query]
        for p in self.products.values():
            if q in p["nama"].lower() or q in p["slug"].lower():
                return p
        return None

    def check_pair_interaction(self, zid_a: str, zid_b: str) -> dict:
        if zid_a == zid_b:
            return {"level": "Duplikasi", "status": "duplikasi_zat"}
        key = tuple(sorted([zid_a, zid_b]))
        if key in self.interactions:
            return self.interactions[key]
        # Negative-test safety guarantee: NEVER claim "aman" when no data exists!
        return {
            "id": None,
            "level": "TidakDiketahui",
            "status": "tidak_diketahui",
            "tindak_lanjut": "TanyaApoteker",
            "mekanisme": "Pasangan belum terdapat di basis kurasi maupun DDInter.",
            "efek": "Data interaksi tidak diketahui (bukan berarti bebas risiko).",
            "rekomendasi": "Konsultasikan ke apoteker sebelum menggabungkan kedua zat.",
            "sumber": "Belum ada sumber terverifikasi",
            "tingkat_bukti": "Tidak diketahui",
            "bukti_records": [],
        }

    # ------------------------------------------------------------------
    # T1: Rekomendasi Terapi Personal
    # ------------------------------------------------------------------
    def recommend_t1(
        self,
        gejala_ids: list[str],
        durasi_hari: int = 1,
        umur_tahun: float = 25,
        kondisi: list[str] | None = None,
        obat_rutin: list[str] | None = None,
        alergi_keywords: list[str] | None = None,
        top_n: int = 3,
    ) -> dict:
        kondisi = list(kondisi or [])
        if umur_tahun < 2 and "anak_bawah_2_tahun" not in kondisi:
            kondisi.append("anak_bawah_2_tahun")
        if umur_tahun >= 65 and "lansia_65_plus" not in kondisi:
            kondisi.append("lansia_65_plus")

        rutin_zids = []
        for o in (obat_rutin or []):
            zid = o if o in self.zat_by_id else self.zat_by_name.get(o.lower())
            if zid:
                rutin_zids.append(zid)

        peringatan = []
        triase = "Pantau"

        # 1. Check red flags & duration thresholds
        for gid in gejala_ids:
            sym = self.symp_map.get(gid, {})
            dur = self.durasi_map.get(gid, {})
            if sym.get("kategori") == "GejalaRedFlag":
                triase = "SegeraKeDokter"
                peringatan.append(f"RED FLAG ({sym.get('label_id')}): {dur.get('alasan_rujuk', 'Rujuk segera ke dokter/IGD.')}")
            elif dur:
                batas = int(dur["batas_hari_swamedikasi"])
                if durasi_hari > batas:
                    aksi = dur["tindak_lanjut_jika_lewat_batas"]
                    if aksi == "SegeraKeDokter" or triase != "SegeraKeDokter":
                        triase = aksi
                    peringatan.append(f"Durasi {sym.get('label_id')} ({durasi_hari} hari) melewati batas swamedikasi ({batas} hari): {dur['alasan_rujuk']}")

        if umur_tahun < 2:
            triase = "SegeraKeDokter"
            peringatan.append("Pasien anak usia < 2 tahun: swamedikasi obat batuk-pilek bebas tidak dianjurkan; konsultasikan ke dokter.")
        if "hamil" in kondisi and triase == "Pantau":
            triase = "TanyaApoteker"
            peringatan.append("Pasien hamil: seluruh pilihan obat harus dikonfirmasi terlebih dahulu dengan dokter/apoteker.")

        # If red flag or age < 2 -> stop product recommendation and refer!
        if triase == "SegeraKeDokter":
            return {
                "triase": triase,
                "peringatan": peringatan,
                "rekomendasi_produk": [],
                "catatan": "Swamedikasi dihentikan karena terdeteksi tanda bahaya / batas durasi / usia berisiko tinggi.",
            }

        target_set = set(gejala_ids)
        candidates = []
        for p in self.products.values():
            if not target_set.issubset(p["indikasi"]):
                continue
            if umur_tahun < 12 and not p["is_anak_product"]:
                continue

            # Check contraindications, age floor, allergy, routine drug interactions
            blocked = False
            prod_warnings = []
            for zid in p["zids"]:
                kt = self.kontra_map.get(zid, {})
                at = self.aturan_map.get(zid, {})
                al = self.alergi_map.get(zid, {})

                # Check age minimum for self-medication
                umin = at.get("usia_min_swamedikasi_tahun", "")
                if umin.isdigit() and umur_tahun < float(umin):
                    blocked = True
                    break

                # Check conditions
                for k in kondisi:
                    st = kt.get(k, "AmanDenganBatas")
                    if st == "Kontraindikasi":
                        blocked = True
                        break
                    elif st == "PerluHatiHati_TanyaDokter":
                        prod_warnings.append(f"{self.zat_by_id[zid]['nama_zat']}: perlu kehati-hatian pada kondisi {k} (konsultasi dokter/apoteker).")
                if blocked:
                    break

                # Check allergies
                if alergi_keywords:
                    al_txt = f"{al.get('alergi_langsung','')} {al.get('pemicu_alergi_silang','')} {al.get('golongan_alergen','')}".lower()
                    for a_kw in alergi_keywords:
                        if a_kw.lower() in al_txt:
                            blocked = True
                            break
                if blocked:
                    break

                # Check routine drug interactions
                for rz in rutin_zids:
                    inter = self.check_pair_interaction(zid, rz)
                    if inter["level"] == "Major":
                        blocked = True
                        break
                    elif inter["level"] in ("Moderate", "Unknown"):
                        prod_warnings.append(f"Interaksi {self.zat_by_id[zid]['nama_zat']} + {self.zat_by_id[rz]['nama_zat']} ({inter['level']}): {inter['rekomendasi']}")

                if blocked:
                    break

                # Check sedative / decongestant side-effect warnings (R-03, R-04)
                if zid in ("ZAT-006", "ZAT-007", "ZAT-030", "ZAT-031"):
                    prod_warnings.append(f"[R-03] Mengandung {self.zat_by_id[zid]['nama_zat']}: menyebabkan mengantuk berat, jangan berkendara.")
                if zid in ("ZAT-004", "ZAT-005"):
                    prod_warnings.append(f"[R-04] Mengandung {self.zat_by_id[zid]['nama_zat']}: risiko palpitasi/jantung berdebar, hindari kafein berlebih.")

            if blocked:
                continue

            # Prefer mono/minimal ingredients, then cheaper unit price
            unit_p = p["harga_per_unit"] if p["harga_per_unit"] is not None else 999999.0
            aturan_list = [
                {
                    "zat": self.zat_by_id[z]["nama_zat"],
                    "dosis": self.aturan_map[z]["dosis_anak"] if umur_tahun < 12 else self.aturan_map[z]["dosis_dewasa"],
                    "frekuensi": self.aturan_map[z]["frekuensi"],
                    "waktu_minum": self.aturan_map[z]["waktu_minum_teks"],
                    "maks_hari": self.aturan_map[z]["maks_hari_swamedikasi"],
                    "sumber": self.aturan_map[z]["sumber"],
                }
                for z in p["zids"]
            ]
            candidates.append((len(p["zids"]), unit_p, p, aturan_list, list(dict.fromkeys(prod_warnings))))

        candidates.sort(key=lambda x: (x[0], x[1], x[2]["nama"]))
        picked = []
        for _, _, p, aturan_list, pwarn in candidates[:top_n]:
            picked.append({
                "slug": p["slug"],
                "nama": p["nama"],
                "komposisi": p["komposisi"],
                "harga_rp": p["harga_rp"],
                "harga_per_unit": p["harga_per_unit"],
                "satuan_unit": p["satuan_unit"],
                "aturan_pakai_per_zat": aturan_list,
                "peringatan_produk": pwarn or ["Ikuti aturan pakai kemasan; pantau gejala."],
            })

        if not picked:
            triase = "TanyaApoteker"
            peringatan.append("Tidak ditemukan produk swamedikasi yang memenuhi seluruh batasan kondisi pasien; konsultasikan ke apoteker/dokter.")
        elif any("Interaksi" in w or "kehati-hatian" in w for item in picked for w in item["peringatan_produk"]) and triase == "Pantau":
            triase = "TanyaApoteker"

        return {
            "triase": triase,
            "peringatan": peringatan,
            "rekomendasi_produk": picked,
        }

    # ------------------------------------------------------------------
    # T2: Alternatif Lebih Murah (Kandungan Identik & Satuan Sebanding)
    # ------------------------------------------------------------------
    def cheaper_alternatives_t2(self, product_query: str, limit: int = 5) -> dict:
        target = self.find_product(product_query)
        if not target:
            return {"error": f"Produk '{product_query}' tidak ditemukan di katalog bersih."}

        alts = []
        for p in self.products.values():
            if p["slug"] == target["slug"]:
                continue
            if p["zids"] != target["zids"]:
                continue
            if p["satuan_unit"] != target["satuan_unit"]:
                continue
            if p["status_harga"] != "ok" or p["harga_per_unit"] is None:
                continue
            if target["harga_per_unit"] is not None and p["harga_per_unit"] >= target["harga_per_unit"]:
                continue
            selisih = round(target["harga_per_unit"] - p["harga_per_unit"], 2) if target["harga_per_unit"] else None
            alts.append({
                "slug": p["slug"],
                "nama": p["nama"],
                "harga_rp": p["harga_rp"],
                "kemasan": p["kemasan"],
                "harga_per_unit": p["harga_per_unit"],
                "satuan_unit": p["satuan_unit"],
                "hemat_per_unit_rp": selisih,
            })

        alts.sort(key=lambda x: x["harga_per_unit"])

        # (b) Alternatif mono-kandungan lebih murah yang menutupi minimal 1 gejala target
        mono_alts = []
        if len(target["zids"]) > 1:
            for p in self.products.values():
                if len(p["zids"]) != 1 or p["zids"][0] not in target["zids"]:
                    continue
                if p["status_harga"] != "ok" or p["harga_per_unit"] is None:
                    continue
                if target["harga_per_unit"] is not None and p["satuan_unit"] == target["satuan_unit"] and p["harga_per_unit"] >= target["harga_per_unit"]:
                    continue
                mono_alts.append({
                    "slug": p["slug"],
                    "nama": p["nama"],
                    "zat_tunggal": self.zat_by_id[p["zids"][0]]["nama_zat"],
                    "harga_rp": p["harga_rp"],
                    "kemasan": p["kemasan"],
                    "harga_per_unit": p["harga_per_unit"],
                    "satuan_unit": p["satuan_unit"],
                    "gejala_tercakup": [self.symp_map[g]["label_id"] for g in sorted(p["indikasi"] & target["indikasi"])],
                })
            mono_alts.sort(key=lambda x: x["harga_per_unit"])

        return {
            "produk_awal": {
                "nama": target["nama"],
                "zids": [self.zat_by_id[z]["nama_zat"] for z in target["zids"]],
                "harga_rp": target["harga_rp"],
                "harga_per_unit": target["harga_per_unit"],
                "satuan_unit": target["satuan_unit"],
                "kemasan": target["kemasan"],
            },
            "alternatif_lebih_murah": alts[:limit],
            "alternatif_mono_kandungan": mono_alts[:limit],
        }

    # ------------------------------------------------------------------
    # T3: Skrining Keranjang & Obat Rutin
    # ------------------------------------------------------------------
    def screen_cart_t3(
        self,
        product_queries: list[str],
        obat_rutin: list[str] | None = None,
        kondisi: list[str] | None = None,
    ) -> dict:
        kondisi = kondisi or []
        items = []
        all_zids_sources = defaultdict(list)  # zid -> list of source names
        atc4_sources = defaultdict(list)      # atc4 -> list of (zid, source)

        for pq in product_queries:
            p = self.find_product(pq)
            if p:
                items.append(p["nama"])
                for z in p["zids"]:
                    all_zids_sources[z].append(p["nama"])
                    a4 = self.zat_by_id[z]["kode_atc"][:5]
                    atc4_sources[a4].append((z, p["nama"]))

        for o in (obat_rutin or []):
            zid = o if o in self.zat_by_id else self.zat_by_name.get(o.lower())
            if zid:
                lbl = f"Obat Rutin: {self.zat_by_id[zid]['nama_zat']}"
                items.append(lbl)
                all_zids_sources[zid].append(lbl)
                a4 = self.zat_by_id[zid]["kode_atc"][:5]
                atc4_sources[a4].append((zid, lbl))

        masalah = []
        triase = "Pantau"

        # 1. Dobel kandungan zat aktif (DuplikasiKandungan)
        for zid, srcs in all_zids_sources.items():
            if len(srcs) > 1:
                zname = self.zat_by_id[zid]["nama_zat"]
                msg = f"Dobel kandungan {zname} pada: {', '.join(srcs)} (risiko overdosis / duplikasi dosis)."
                masalah.append({"jenis": "DuplikasiKandungan", "detail": msg, "aksi": "TanyaApoteker", "sumber": "Aturan DuplikasiKandungan + PIONAS"})
                if triase == "Pantau":
                    triase = "TanyaApoteker"

        # 2. Dobel kelas terapi ATC Level-4 (DuplikasiKelasATC)
        for a4, entries in atc4_sources.items():
            distinct_zids = sorted({z for z, _ in entries})
            if len(distinct_zids) > 1:
                znames = [self.zat_by_id[z]["nama_zat"] for z in distinct_zids]
                aname = self.atc4_names.get(a4, a4)
                masalah.append({
                    "jenis": "DuplikasiKelasATC",
                    "detail": f"Dobel kelas terapi ATC-4 {a4} ({aname}): {' + '.join(znames)}.",
                    "aksi": "TanyaApoteker",
                    "sumber": "data/atc/atc_all.csv + WHO ATC",
                })
                if triase == "Pantau":
                    triase = "TanyaApoteker"

        # 3. Interaksi berpasangan
        uniq_zids = sorted(all_zids_sources.keys())
        for i in range(len(uniq_zids)):
            for j in range(i + 1, len(uniq_zids)):
                za, zb = uniq_zids[i], uniq_zids[j]
                inter = self.check_pair_interaction(za, zb)
                if inter["level"] in ("Major", "Moderate", "Minor", "Unknown"):
                    masalah.append({
                        "jenis": f"Interaksi{inter['level']}",
                        "pasangan": f"{self.zat_by_id[za]['nama_zat']} + {self.zat_by_id[zb]['nama_zat']}",
                        "detail": inter["efek"],
                        "rekomendasi": inter["rekomendasi"],
                        "aksi": inter["tindak_lanjut"],
                        "sumber": inter["sumber"],
                        "status_data": inter["status"],
                    })
                    if inter["tindak_lanjut"] == "SegeraKeDokter":
                        triase = "SegeraKeDokter"
                    elif triase == "Pantau" and inter["tindak_lanjut"] == "TanyaApoteker":
                        triase = "TanyaApoteker"

        # 4. Konflik jadwal makan (SebelumMakan vs SesudahMakan)
        sebelum = [self.zat_by_id[z]["nama_zat"] for z in uniq_zids if self.aturan_map[z]["kode_hubungan_makan"] == "SebelumMakan"]
        sesudah = [self.zat_by_id[z]["nama_zat"] for z in uniq_zids if self.aturan_map[z]["kode_hubungan_makan"] == "SesudahMakan"]
        if sebelum and sesudah:
            masalah.append({
                "jenis": "KonflikJadwalMakan",
                "detail": f"Jangan ditelan bersamaan: {', '.join(sebelum)} (wajib perut kosong sebelum makan) vs {', '.join(sesudah)} (wajib sesudah makan).",
                "aksi": "TanyaApoteker",
                "sumber": "substansi_aturan_pakai.csv (PIONAS BPOM)",
            })
            if triase == "Pantau":
                triase = "TanyaApoteker"

        # 5. Kontraindikasi kondisi pasien
        for zid in uniq_zids:
            kt = self.kontra_map.get(zid, {})
            for k in kondisi:
                st = kt.get(k, "AmanDenganBatas")
                if st == "Kontraindikasi":
                    masalah.append({
                        "jenis": "KontraindikasiKondisi",
                        "detail": f"{self.zat_by_id[zid]['nama_zat']} KONTRAINDIKASI untuk kondisi {k}.",
                        "aksi": "SegeraKeDokter",
                        "sumber": kt.get("sumber_rujukan", "PIONAS BPOM"),
                    })
                    triase = "SegeraKeDokter"
                elif st == "PerluHatiHati_TanyaDokter":
                    masalah.append({
                        "jenis": "PeringatanKondisi",
                        "detail": f"{self.zat_by_id[zid]['nama_zat']} perlu kehati-hatian pada kondisi {k}.",
                        "aksi": "TanyaApoteker",
                        "sumber": kt.get("sumber_rujukan", "PIONAS BPOM"),
                    })
                    if triase == "Pantau":
                        triase = "TanyaApoteker"

        return {"keranjang": items, "triase_akhir": triase, "jumlah_masalah": len(masalah), "masalah": masalah}

    # ------------------------------------------------------------------
    # T4: Substitusi Aman
    # ------------------------------------------------------------------
    def safe_substitution_t4(self, product_query: str, kondisi_pasien: str, limit: int = 3) -> dict:
        orig = self.find_product(product_query)
        if not orig:
            return {"error": f"Produk '{product_query}' tidak ditemukan."}

        offending = []
        for zid in orig["zids"]:
            st = self.kontra_map.get(zid, {}).get(kondisi_pasien, "AmanDenganBatas")
            if st in ("Kontraindikasi", "PerluHatiHati_TanyaDokter"):
                offending.append((self.zat_by_id[zid]["nama_zat"], st))

        # Target symptoms from original product (excluding symptom covered ONLY by the offending drug if unavoidable)
        target_inds = orig["indikasi"]
        substitutes = []
        for p in self.products.values():
            if p["slug"] == orig["slug"]:
                continue
            # Must not trigger Kontraindikasi or PerluHatiHati for kondisi_pasien
            safe = True
            for zid in p["zids"]:
                if self.kontra_map.get(zid, {}).get(kondisi_pasien, "AmanDenganBatas") in ("Kontraindikasi", "PerluHatiHati_TanyaDokter"):
                    safe = False
                    break
            if not safe:
                continue
            overlap = len(p["indikasi"] & target_inds)
            if overlap == 0:
                continue
            unit_p = p["harga_per_unit"] if p["harga_per_unit"] is not None else 999999.0
            substitutes.append((-overlap, len(p["zids"]), unit_p, p))

        substitutes.sort(key=lambda x: (x[0], x[1], x[2], x[3]["nama"]))
        return {
            "produk_awal": orig["nama"],
            "kondisi_pasien": kondisi_pasien,
            "alasan_penolakan": [f"{z} berstatus {st} pada kondisi {kondisi_pasien}" for z, st in offending],
            "alternatif_aman": [
                {
                    "nama": p["nama"],
                    "komposisi": p["komposisi"],
                    "harga_rp": p["harga_rp"],
                    "harga_per_unit": p["harga_per_unit"],
                    "satuan_unit": p["satuan_unit"],
                    "gejala_tercakup": [self.symp_map[g]["label_id"] for g in sorted(p["indikasi"] & target_inds)],
                }
                for _, _, _, p in substitutes[:limit]
            ],
        }

    # ------------------------------------------------------------------
    # T5: Kartu Edukasi & Explainability (Markdown)
    # ------------------------------------------------------------------
    def generate_education_card_t5(self, product_query: str) -> str:
        p = self.find_product(product_query)
        if not p:
            raise ValueError(f"Produk '{product_query}' tidak ditemukan.")

        md = [
            f"# Kartu Edukasi Obat: {p['nama']}",
            "",
            f"- **Golongan BPOM:** {p['golongan'] or 'Tidak tercantum'}",
            f"- **NIE BPOM:** {p['nie_bpom'] or 'Belum tercantum di katalog'}",
            f"- **Produsen:** {p['pabrik'] or 'Tidak tercantum'}",
            f"- **Kemasan & Harga Katalog:** {p['kemasan']} | Rp{p['harga_rp']:,}" if p["harga_rp"] else f"- **Kemasan:** {p['kemasan']} (Harga belum tercantum)",
            f"- **Komposisi Kemasan:** {p['komposisi']}",
            "",
            "## 1. Untuk Keluhan Apa (Bahasa Awam — *Kesimpulan dari Aturan Properti*)",
        ]
        for gid in sorted(p["indikasi"]):
            s = self.symp_map[gid]
            md.append(f"- **{s['label_id']}** (*{s['label_en']}*): {s['deskripsi']}")

        md.append("\n## 2. Cara Pakai & Batas Aman (Per Zat Aktif — *Data Kurasi PIONAS*)")
        for zid in p["zids"]:
            z = self.zat_by_id[zid]
            at = self.aturan_map[zid]
            md.append(f"### {z['nama_zat']} (`{z['kode_atc']}` / `{z['chebi_id']}`)")
            md.append(f"- **Dosis Dewasa:** {at['dosis_dewasa']} ({at['frekuensi']})")
            md.append(f"- **Dosis Anak:** {at['dosis_anak']} | **Usia min:** {at['usia_min_swamedikasi_tahun']} th | **BB min:** {at['bb_min_swamedikasi_kg']} kg")
            md.append(f"- **Waktu Minum:** {at['waktu_minum_teks']}")
            md.append(f"- **Batas Hari Swamedikasi:** {at['maks_hari_swamedikasi']} | **Maks Harian Dewasa:** {at['maks_dosis_harian_dewasa']}")
            md.append(f"- **Pantangan Makanan/Minuman:** {self.kontra_map[zid]['pantangan_makanan_minuman']}")
            md.append(f"- **Sumber:** {at['sumber']}")

        md.append("\n## 3. Peringatan Efek Samping, Kondisi Khusus, & Alergi")
        for zid in p["zids"]:
            zname = self.zat_by_id[zid]["nama_zat"]
            if zid in ("ZAT-006", "ZAT-007", "ZAT-030", "ZAT-031"):
                md.append(f"- **[Kesimpulan Aturan R-03]** Mengandung **{zname}** $\\rightarrow$ efek samping **Mengantuk berat** (dilarang berkendara/mengoperasikan mesin).")
            if zid in ("ZAT-004", "ZAT-005"):
                md.append(f"- **[Kesimpulan Aturan R-04 & R-08]** Mengandung **{zname}** $\\rightarrow$ risiko **Palpitasi** & **Kontraindikasi Hipertensi Tidak Terkontrol**.")
            al = self.alergi_map[zid]
            md.append(f"- **[Alergi Silang — {al['status_sumber']}]** {zname}: waspada alergi silang dengan *{al['pemicu_alergi_silang']}* ([Sumber]({al['url_sumber']})).")

        md.append("\n## 4. Rantai Interaksi Obat Penting & Bukti (*Explainability*)")
        found_int = False
        for zid in p["zids"]:
            for (za, zb), inter in sorted(self.interactions.items()):
                if zid in (za, zb) and inter["level"] in ("Major", "Moderate") and inter["status"] == "kurasi_terverifikasi":
                    other = zb if za == zid else za
                    found_int = True
                    md.append(f"- **{self.zat_by_id[zid]['nama_zat']} + {self.zat_by_id[other]['nama_zat']}** (`{inter['level']}` $\\rightarrow$ **{inter['tindak_lanjut']}**)")
                    md.append(f"  - *Alasan:* {inter['mekanisme']}")
                    md.append(f"  - *Rekomendasi:* {inter['rekomendasi']}")
                    md.append(f"  - *Sumber:* {inter['sumber']} (Tingkat bukti: {inter['tingkat_bukti']})")
        if not found_int:
            md.append("- Tidak ada interaksi Major/Moderate terkurasi khusus untuk zat tunggal ini; **status kombinasi lain yang tidak tercantum adalah `tidak_diketahui` (bukan otomatis aman)** — selalu konsultasikan ke apoteker jika sedang mengonsumsi obat rutin.")

        md.append("\n## 5. Kapan Harus Berhenti & Segera ke Dokter")
        md.append("- Hentikan penggunaan dan **Segera ke Dokter / IGD** jika muncul tanda bahaya (*Red Flag*): **sesak napas, napas mengi, nyeri dada, batuk berdarah, urin gelap pekat**, atau reaksi alergi berat (bengkak bibir/wajah, biduran luas).")
        md.append("- Rujuk ke dokter bila demam tidak turun $>3$ hari atau batuk menetap $>5$–$7$ hari.")
        md.append("\n> *Disclaimer (KB v2.0): Kartu edukasi ini adalah alat bantu keputusan berbasis pengetahuan (KBR), bukan resep maupun pengganti penilaian dokter/apoteker.*")
        return "\n".join(md)


def export_demo_cards():
    eng = KBRKnowledgeEngine()
    out_dir = os.path.join(ROOT, "out", "kartu_edukasi")
    os.makedirs(out_dir, exist_ok=True)
    targets = [
        ("kartu_01_actifed_merah.md", "ACTIFED-PLUS-COUGH-SUPPRESS-SYR-MERAH-60ML-275"),
        ("kartu_02_komix_jeruk_nipis.md", "KOMIX-JERUK-NIPIS-7ML-SACH-30S-8909"),
        ("kartu_03_sanmol_forte.md", "SANMOL-F-650MG-TAB-4S-STRIP-25S-17789"),
        ("kartu_04_ob_combi_att.md", "OB-COMBI-ATT-MENTHOL-SYR-60ML-34066"),
        ("kartu_05_siladex_cough_n_cold.md", "SILADEX-COUGH-N-COLD-SYR-100ML-9753"),
    ]
    for fname, slug in targets:
        text = eng.generate_education_card_t5(slug)
        with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
            f.write(text)
    print(f"[OK] 5 kartu edukasi T5 disimpan di: {out_dir}")


if __name__ == "__main__":
    export_demo_cards()
