"""
Collect human CYP450 drug-metabolizing enzyme terms from Protein Ontology (PRO)
via EMBL-EBI OLS4 REST API and Ontobee RDF endpoint, then emit a clean OWL 2 DL
MIREOT module at out/enzim_modul.owl without downloading the full pr.owl.
"""

from __future__ import annotations

import csv
import json
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

OLS4_TERM_ENDPOINT = "https://www.ebi.ac.uk/ols4/api/ontologies/pr/terms"
OLS4_SEARCH_ENDPOINT = "https://www.ebi.ac.uk/ols4/api/search"
ONTOBEE_RDF_ENDPOINT = "https://ontobee.org/ontology/rdf/PR"

USER_AGENT = "ProjectKBR-Group4-EnzymeCollector/1.0"
ONTOLOGY_IRI = "http://purl.obolibrary.org/obo/kbr-group4/enzim_modul.owl"

# Verified human CYP450 UniProt-backed PRO classes
TARGET_ENZYMES = [
    {
        "obo_id": "PR:P08684",
        "iri": "http://purl.obolibrary.org/obo/PR_P08684",
        "uniprot": "P08684",
        "gene_symbol": "CYP3A4",
    },
    {
        "obo_id": "PR:P10635",
        "iri": "http://purl.obolibrary.org/obo/PR_P10635",
        "uniprot": "P10635",
        "gene_symbol": "CYP2D6",
    },
    {
        "obo_id": "PR:P33261",
        "iri": "http://purl.obolibrary.org/obo/PR_P33261",
        "uniprot": "P33261",
        "gene_symbol": "CYP2C19",
    },
    {
        "obo_id": "PR:P11712",
        "iri": "http://purl.obolibrary.org/obo/PR_P11712",
        "uniprot": "P11712",
        "gene_symbol": "CYP2C9",
    },
]


def http_get_text(url: str, accept: str = "application/json", timeout: int = 30) -> tuple[str, str]:
    """Perform an HTTP GET request and return (final_url, response_text)."""
    req = urllib.request.Request(
        url,
        headers={
            "Accept": accept,
            "User-Agent": USER_AGENT,
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.geturl(), resp.read().decode(charset, errors="replace")


def fetch_ols4_term(iri: str) -> tuple[dict | None, str]:
    """Fetch a term object from OLS4 by IRI; returns (term_dict, url)."""
    query = urllib.parse.urlencode({"iri": iri})
    url = f"{OLS4_TERM_ENDPOINT}?{query}"
    final_url, raw = http_get_text(url, accept="application/json")
    payload = json.loads(raw)
    terms = payload.get("_embedded", {}).get("terms", [])
    if not terms:
        return None, final_url
    return terms[0], final_url


def fetch_ols4_parents(term: dict) -> list[dict]:
    """Follow OLS4 _links.parents if available to retrieve direct parent classes."""
    parents_href = term.get("_links", {}).get("parents", {}).get("href")
    if not parents_href:
        return []
    try:
        _, raw = http_get_text(parents_href, accept="application/json")
        payload = json.loads(raw)
        return payload.get("_embedded", {}).get("terms", [])
    except (urllib.error.URLError, json.JSONDecodeError):
        return []


def fetch_ols4_search_fallback(gene_symbol: str) -> tuple[dict | None, str]:
    """Fallback search in OLS4 PR ontology if direct IRI lookup returns empty."""
    query = urllib.parse.urlencode(
        {"q": gene_symbol, "ontology": "pr", "rows": 5}
    )
    url = f"{OLS4_SEARCH_ENDPOINT}?{query}"
    final_url, raw = http_get_text(url, accept="application/json")
    payload = json.loads(raw)
    docs = payload.get("response", {}).get("docs", [])
    for doc in docs:
        iri = doc.get("iri", "")
        label = (doc.get("label") or "").lower()
        if "(human)" in label or iri.startswith("http://purl.obolibrary.org/obo/PR_P"):
            term, term_url = fetch_ols4_term(iri)
            if term:
                return term, term_url
    return None, final_url


def fetch_ontobee_rdf(iri: str) -> tuple[str, str]:
    """Fetch per-term RDF/XML from Ontobee for provenance and cross-checking."""
    query = urllib.parse.urlencode({"iri": iri})
    url = f"{ONTOBEE_RDF_ENDPOINT}?{query}"
    return http_get_text(url, accept="application/rdf+xml")


def parse_ontobee_labels_and_parents(rdf_xml: str, target_iri: str) -> dict:
    """Extract label, IAO_0000115 definition, and subClassOf IRIs from Ontobee RDF/XML."""
    ns = {
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "owl": "http://www.w3.org/2002/07/owl#",
        "obo": "http://purl.obolibrary.org/obo/",
    }
    root = ET.fromstring(rdf_xml)
    result = {"label": "", "definition": "", "parent_iris": []}
    for cls in root.findall(".//owl:Class", ns):
        about = cls.attrib.get(f"{{{ns['rdf']}}}about", "")
        if about != target_iri:
            continue
        lbl = cls.find("rdfs:label", ns)
        if lbl is not None and lbl.text:
            result["label"] = lbl.text.strip()
        defn = cls.find("obo:IAO_0000115", ns)
        if defn is not None and defn.text:
            result["definition"] = defn.text.strip()
        for sub in cls.findall("rdfs:subClassOf", ns):
            res = sub.attrib.get(f"{{{ns['rdf']}}}resource")
            if res and res.startswith("http"):
                result["parent_iris"].append(res)
    return result


def build_owl_module(records: list[dict], parents_by_iri: dict[str, dict]) -> str:
    """Serialize fetched enzyme terms and direct parent classes into a clean OWL 2 DL RDF/XML module."""
    lines = [
        '<?xml version="1.0"?>',
        '<rdf:RDF xmlns="http://purl.obolibrary.org/obo/kbr-group4/enzim_modul.owl#"',
        '     xml:base="http://purl.obolibrary.org/obo/kbr-group4/enzim_modul.owl"',
        '     xmlns:obo="http://purl.obolibrary.org/obo/"',
        '     xmlns:owl="http://www.w3.org/2002/07/owl#"',
        '     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"',
        '     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"',
        '     xmlns:oboInOwl="http://www.geneontology.org/formats/oboInOwl#"',
        '     xmlns:xsd="http://www.w3.org/2001/XMLSchema#">',
        f'    <owl:Ontology rdf:about="{escape(ONTOLOGY_IRI)}">',
        '        <rdfs:comment xml:lang="en">MIREOT extract of human CYP450 drug-metabolizing enzymes from Protein Ontology (PRO) via EMBL-EBI OLS4 API / Ontobee.</rdfs:comment>',
        '    </owl:Ontology>',
        "",
        "    <!-- Annotation Properties -->",
        '    <owl:AnnotationProperty rdf:about="http://purl.obolibrary.org/obo/IAO_0000115">',
        '        <rdfs:label xml:lang="en">definition</rdfs:label>',
        '    </owl:AnnotationProperty>',
        '    <owl:AnnotationProperty rdf:about="http://www.geneontology.org/formats/oboInOwl#hasOBONamespace">',
        '        <rdfs:label>has_obo_namespace</rdfs:label>',
        '    </owl:AnnotationProperty>',
        '    <owl:AnnotationProperty rdf:about="http://www.geneontology.org/formats/oboInOwl#id">',
        '        <rdfs:label>id</rdfs:label>',
        '    </owl:AnnotationProperty>',
        "",
        "    <!-- Parent Classes -->",
    ]

    for p_iri in sorted(parents_by_iri):
        p_info = parents_by_iri[p_iri]
        p_label = p_info.get("label") or p_iri.rsplit("/", 1)[-1]
        p_obo_id = p_info.get("obo_id") or ""
        p_def = p_info.get("definition") or ""
        lines.append(f'    <owl:Class rdf:about="{escape(p_iri)}">')
        lines.append(f'        <rdfs:label xml:lang="en">{escape(p_label)}</rdfs:label>')
        if p_obo_id:
            lines.append(f'        <oboInOwl:id rdf:datatype="http://www.w3.org/2001/XMLSchema#string">{escape(p_obo_id)}</oboInOwl:id>')
        if p_def:
            lines.append(f'        <obo:IAO_0000115 xml:lang="en">{escape(p_def)}</obo:IAO_0000115>')
        lines.append('        <oboInOwl:hasOBONamespace rdf:datatype="http://www.w3.org/2001/XMLSchema#string">protein</oboInOwl:hasOBONamespace>')
        lines.append('    </owl:Class>')

    lines.append("")
    lines.append("    <!-- Target Human CYP450 Enzyme Classes -->")
    for rec in records:
        lines.append(f'    <owl:Class rdf:about="{escape(rec["iri"])}">')
        lines.append(f'        <rdfs:label xml:lang="en">{escape(rec["label"])}</rdfs:label>')
        lines.append(f'        <oboInOwl:id rdf:datatype="http://www.w3.org/2001/XMLSchema#string">{escape(rec["obo_id"])}</oboInOwl:id>')
        if rec["definition"]:
            lines.append(f'        <obo:IAO_0000115 xml:lang="en">{escape(rec["definition"])}</obo:IAO_0000115>')
        for p_iri in rec["parent_iris"]:
            lines.append(f'        <rdfs:subClassOf rdf:resource="{escape(p_iri)}"/>')
        lines.append('        <oboInOwl:hasOBONamespace rdf:datatype="http://www.w3.org/2001/XMLSchema#string">protein</oboInOwl:hasOBONamespace>')
        lines.append('    </owl:Class>')

    lines.append("</rdf:RDF>")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data" / "enzymes"
    ontobee_dir = data_dir / "ontobee"
    out_owl = project_root / "out" / "enzim_modul.owl"

    data_dir.mkdir(parents=True, exist_ok=True)
    ontobee_dir.mkdir(parents=True, exist_ok=True)
    out_owl.parent.mkdir(parents=True, exist_ok=True)

    raw_ols4 = {}
    records = []
    parents_by_iri: dict[str, dict] = {}
    urls_used = []

    for spec in TARGET_ENZYMES:
        iri = spec["iri"]
        obo_id = spec["obo_id"]
        gene = spec["gene_symbol"]
        print(f"Fetching {obo_id} ({gene}) from OLS4...")

        term, url_used = fetch_ols4_term(iri)
        if term is None:
            print(f"  Direct IRI lookup empty, falling back to OLS4 search for {gene}...")
            term, url_used = fetch_ols4_search_fallback(gene)
        if term is None:
            raise RuntimeError(f"Failed to resolve PRO term for {obo_id} ({gene}) via OLS4 API.")

        urls_used.append(url_used)
        raw_ols4[obo_id] = term

        resolved_iri = term.get("iri") or iri
        resolved_obo_id = term.get("obo_id") or obo_id
        label = term.get("label") or ""
        desc_list = term.get("description") or []
        definition = desc_list[0] if desc_list else ""

        parent_terms = fetch_ols4_parents(term)
        parent_iris = []
        parent_labels = []
        for pt in parent_terms:
            p_iri = pt.get("iri")
            if not p_iri:
                continue
            parent_iris.append(p_iri)
            p_label = pt.get("label") or p_iri.rsplit("/", 1)[-1]
            parent_labels.append(p_label)
            p_desc = pt.get("description") or []
            parents_by_iri[p_iri] = {
                "iri": p_iri,
                "obo_id": pt.get("obo_id") or "",
                "label": p_label,
                "definition": p_desc[0] if p_desc else "",
            }

        # Cross-check with Ontobee RDF endpoint (non-fatal if Ontobee is temporarily unavailable)
        ontobee_url = ""
        try:
            ob_url, rdf_xml = fetch_ontobee_rdf(resolved_iri)
            ontobee_url = ob_url
            urls_used.append(ob_url)
            short_name = resolved_iri.rsplit("/", 1)[-1]
            (ontobee_dir / f"{short_name}.owl").write_text(rdf_xml, encoding="utf-8")
            parsed_ob = parse_ontobee_labels_and_parents(rdf_xml, resolved_iri)
            if not label and parsed_ob["label"]:
                label = parsed_ob["label"]
            if not definition and parsed_ob["definition"]:
                definition = parsed_ob["definition"]
            if not parent_iris and parsed_ob["parent_iris"]:
                parent_iris = parsed_ob["parent_iris"]
                for p_iri in parent_iris:
                    parents_by_iri.setdefault(
                        p_iri,
                        {"iri": p_iri, "obo_id": "", "label": p_iri.rsplit("/", 1)[-1], "definition": ""},
                    )
        except Exception as exc:
            print(f"  Note: Ontobee RDF cross-check skipped for {obo_id}: {exc}")

        records.append(
            {
                "obo_id": resolved_obo_id,
                "iri": resolved_iri,
                "gene_symbol": gene,
                "uniprot": spec["uniprot"],
                "label": label,
                "definition": definition,
                "parent_iris": parent_iris,
                "parent_labels": parent_labels,
                "ols4_url": url_used,
                "ontobee_url": ontobee_url,
            }
        )
        print(f"  OK: {resolved_obo_id} -> {label}")

    # Save raw OLS4 JSON
    ols4_json_path = data_dir / "enzymes_ols4.json"
    ols4_json_path.write_text(json.dumps(raw_ols4, indent=2, ensure_ascii=False), encoding="utf-8")

    # Save structured CSV summary
    csv_path = data_dir / "enzymes_selected.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "obo_id",
                "iri",
                "gene_symbol",
                "uniprot",
                "label",
                "parent_iris",
                "parent_labels",
                "definition",
            ],
        )
        writer.writeheader()
        for rec in records:
            writer.writerow(
                {
                    "obo_id": rec["obo_id"],
                    "iri": rec["iri"],
                    "gene_symbol": rec["gene_symbol"],
                    "uniprot": rec["uniprot"],
                    "label": rec["label"],
                    "parent_iris": "|".join(rec["parent_iris"]),
                    "parent_labels": "|".join(rec["parent_labels"]),
                    "definition": rec["definition"],
                }
            )

    # Save source provenance metadata
    metadata = {
        "source": "Protein Ontology (PRO) via EMBL-EBI OLS4 API & Ontobee RDF",
        "urls": sorted(set(urls_used)),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "scope": "4 human CYP450 drug-metabolizing enzymes (CYP3A4, CYP2D6, CYP2C19, CYP2C9)",
        "count": len(records),
        "owl_output": str(out_owl.relative_to(project_root)).replace("\\", "/"),
    }
    (data_dir / "source_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Generate OWL 2 DL MIREOT module
    owl_xml = build_owl_module(records, parents_by_iri)
    out_owl.write_text(owl_xml, encoding="utf-8")

    print(f"\nSaved OLS4 JSON   : {ols4_json_path}")
    print(f"Saved CSV summary : {csv_path}")
    print(f"Saved metadata    : {data_dir / 'source_metadata.json'}")
    print(f"Saved OWL module  : {out_owl}")


if __name__ == "__main__":
    main()
