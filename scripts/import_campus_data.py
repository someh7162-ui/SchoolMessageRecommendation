"""Import campus information from JSON/NDJSON/CSV/PDF into contents.

The PDF mode intentionally keeps the source document as a searchable record so
that historical summaries remain traceable even when individual article URLs
are unavailable.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import engine, contents, jt, now
from sqlalchemy import select

TYPES = {
    "竞赛": "competition", "挑战杯": "competition", "大赛": "competition",
    "就业": "employment", "招聘": "employment", "双选会": "employment",
    "讲座": "lecture", "学术": "academic", "奖学金": "scholarship",
    "志愿": "volunteer", "社团": "club", "选课": "teaching", "教务": "teaching",
    "考试": "teaching", "课程": "teaching", "毕业": "graduate", "活动": "activity",
}

def classify(text: str) -> str:
    for key, typ in TYPES.items():
        if key in text: return typ
    return "notice"

def clean(v) -> str:
    return re.sub(r"\s+", " ", str(v or "")).strip()

def pdf_record(path: Path) -> list[dict]:
    from pypdf import PdfReader
    out=[]
    for n,p in enumerate(PdfReader(str(path)).pages,1):
        text = clean(p.extract_text() or "")
        if not text: continue
        out.append({"title": f"{path.stem}（第{n}页）", "body": text, "summary": text[:500],
            "content_type": classify(text), "tags": ["新疆工程学院", "公开信息", "校园新闻", "通知公告"],
            "source_url": "", "source_site": "新疆工程学院", "source_department": "新疆工程学院",
            "source_id": f"{path.name}#page={n}"})
    return out

def load(path: Path):
    if path.suffix.lower() == ".pdf": return pdf_record(path)
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as f: return list(csv.DictReader(f))
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".ndjson", ".jsonl"): return [json.loads(x) for x in raw.splitlines() if x.strip()]
    obj = json.loads(raw); return obj if isinstance(obj, list) else obj.get("items", [obj])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("input"); args = ap.parse_args(); rows = load(Path(args.input))
    added = duplicate = failed = 0
    with engine.begin() as c:
        existing = {r[0] for r in c.execute(select(contents.c.source_url).where(contents.c.source_url.is_not(None)))}
        hashes = {r[0] for r in c.execute(select(contents.c.content_hash).where(contents.c.content_hash.is_not(None)))}
        for row in rows:
            try:
                title, body = clean(row.get("title")), clean(row.get("body") or row.get("content") or row.get("text"))
                if not title or not body: raise ValueError("title/body required")
                h = hashlib.sha256((title + "\n" + body).encode("utf-8")).hexdigest(); url = clean(row.get("source_url") or row.get("article_url") or row.get("source_page_url"))
                if h in hashes or (url and url in existing): duplicate += 1; continue
                tags = row.get("tags", []); tags = tags if isinstance(tags, list) else [x for x in re.split(r"[,，、]", str(tags)) if x]
                typ = row.get("content_type") or classify(title + body)
                c.execute(contents.insert().values(title=title, body=body, summary=clean(row.get("summary")) or body[:500], content_type=typ, tags=jt(tags), target_roles=jt(row.get("target_roles", [])), target_colleges=jt(row.get("target_colleges", [])), target_majors=jt(row.get("target_majors", [])), target_grades=jt(row.get("target_grades", [])), source_url=url, source_site=clean(row.get("source_site") or "新疆工程学院"), source_department=clean(row.get("source_department") or "新疆工程学院"), source_id=clean(row.get("source_id")), content_hash=h, crawl_time=now(), updated_at=now(), publish_time=row.get("publish_time") or row.get("date") or now(), end_time=row.get("end_time"), status="published"))
                hashes.add(h); existing.add(url); added += 1
            except Exception as ex: print(f"skip: {ex}", file=sys.stderr); failed += 1
    print(json.dumps({"total": len(rows), "added": added, "duplicate": duplicate, "failed": failed}, ensure_ascii=False))

if __name__ == "__main__": main()
