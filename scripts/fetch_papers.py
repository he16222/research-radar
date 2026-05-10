"""
fetch_papers.py
从 OpenAlex 按关键词 + 期刊 ISSN 抓取 AIAA / ASME 论文。
"""

import time
import hashlib
import logging
import requests
from config import KEYWORDS, TARGET_JOURNALS, MAX_PAPERS_PER_QUERY, FETCH_FROM_YEAR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

OPENALEX_API = "https://api.openalex.org/works"
# polite pool：加邮箱后速率限制从 10/s 升至更宽松
POLITE_EMAIL = "research@example.com"


def paper_id(title: str) -> str:
    return hashlib.md5(title.strip().lower().encode()).hexdigest()[:12]


def reconstruct_abstract(inv: dict) -> str:
    """把 OpenAlex 的倒排索引还原为摘要文本"""
    if not inv:
        return ""
    pairs = [(pos, word) for word, positions in inv.items() for pos in positions]
    return " ".join(word for _, word in sorted(pairs))


def extract_affiliations(authorships: list[dict]) -> list[str]:
    """Extract institution and raw affiliation strings from OpenAlex authorships."""
    affiliations: list[str] = []
    seen: set[str] = set()
    for authorship in authorships:
        for inst in authorship.get("institutions", []) or []:
            name = (inst.get("display_name") or "").strip()
            if name and name.lower() not in seen:
                seen.add(name.lower())
                affiliations.append(name)
        raw_values = authorship.get("raw_affiliation_strings") or []
        raw_single = authorship.get("raw_affiliation_string")
        if raw_single:
            raw_values.append(raw_single)
        for raw in raw_values:
            text = str(raw).strip()
            if text and text.lower() not in seen:
                seen.add(text.lower())
                affiliations.append(text)
    return affiliations


def fetch_openalex(keyword: str, issn: str, journal_name: str,
                   max_results: int = 25) -> list[dict]:
    params = {
        "search":   keyword,
        "filter":   f"primary_location.source.issn:{issn},"
                    f"from_publication_date:{FETCH_FROM_YEAR}-01-01",
        "per-page": max_results,
        "sort":     "publication_date:desc",
        "select":   "title,abstract_inverted_index,authorships,"
                    "publication_date,doi,primary_location",
        "mailto":   POLITE_EMAIL,
    }

    try:
        resp = requests.get(OPENALEX_API, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        log.warning(f"OpenAlex 请求失败 [{journal_name} / {keyword}]: {e}")
        return []

    papers = []
    for item in data.get("results", []):
        title = (item.get("title") or "").strip()
        if not title:
            continue

        abstract = reconstruct_abstract(item.get("abstract_inverted_index"))
        if not abstract:
            continue

        authorships = item.get("authorships", []) or []
        authors = [
            a["author"]["display_name"]
            for a in authorships
            if a.get("author", {}).get("display_name")
        ]
        affiliations = extract_affiliations(authorships)

        doi  = item.get("doi") or ""
        url  = f"https://doi.org/{doi.replace('https://doi.org/', '')}" if doi else ""
        date = item.get("publication_date") or ""

        venue = (
            (item.get("primary_location") or {})
            .get("source", {})
            .get("display_name", "") or journal_name
        )

        papers.append({
            "id":       paper_id(title),
            "title":    title,
            "abstract": abstract,
            "authors":  authors,
            "affiliations": affiliations,
            "date":     date,
            "url":      url,
            "venue":    venue,
            "source":   "OpenAlex",
        })

    log.info(f"OpenAlex [{journal_name} / {keyword}] → {len(papers)} 篇")
    return papers


UNPAYWALL_API = "https://api.unpaywall.org/v2"
UNPAYWALL_EMAIL = "research@example.com"

def lookup_pdf_url(doi: str) -> str:
    """通过 Unpaywall 查找开放获取 PDF 链接，找不到返回空字符串"""
    if not doi:
        return ""
    clean_doi = doi.replace("https://doi.org/", "")
    try:
        resp = requests.get(
            f"{UNPAYWALL_API}/{clean_doi}",
            params={"email": UNPAYWALL_EMAIL},
            timeout=10,
        )
        if resp.status_code != 200:
            return ""
        data = resp.json()
        loc = data.get("best_oa_location") or {}
        return loc.get("url_for_pdf") or ""
    except Exception:
        return ""


def fetch_all_papers(keywords=None) -> list[dict]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    kw_list = keywords if keywords is not None else KEYWORDS
    tasks = [
        (kw, journal["issn"], journal["name"])
        for journal in TARGET_JOURNALS
        for kw in kw_list
    ]
    log.info(f"并发抓取：{len(tasks)} 个查询（{len(kw_list)} 关键词 × {len(TARGET_JOURNALS)} 期刊）")

    all_papers: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(fetch_openalex, kw, issn, name, MAX_PAPERS_PER_QUERY): (name, kw)
            for kw, issn, name in tasks
        }
        for future in as_completed(futures):
            for p in future.result():
                all_papers[p["id"]] = p

    result = list(all_papers.values())
    log.info(f"去重后：共 {len(result)} 篇，开始并发查询开放获取 PDF…")

    def _lookup(p: dict) -> bool:
        if p.get("pdf_url"):
            return False
        pdf_url = lookup_pdf_url(p.get("url", ""))
        p["pdf_url"] = pdf_url
        return bool(pdf_url)

    with ThreadPoolExecutor(max_workers=10) as executor:
        found = sum(executor.map(_lookup, result))

    log.info(f"找到开放获取 PDF：{found}/{len(result)} 篇")
    return result


if __name__ == "__main__":
    import json
    papers = fetch_all_papers()
    print(json.dumps(papers[:2], ensure_ascii=False, indent=2))
