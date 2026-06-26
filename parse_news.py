#!/usr/bin/env python3
"""解析 last30days 的 *-raw-v3.md -> news-data.json + news-data.js"""
import re, json, sys, argparse
from pathlib import Path

CATEGORY_MAP = {
    "artificial-intelligence": "AI", "artificial": "AI",
    "agent": "量化", "agent量化": "量化", "quant": "量化",
    "finance": "财经", "tech": "科技",
    "media": "自媒体", "self-media": "自媒体",
}

TOPIC_KEYWORDS = {
    "财经": "财经", "股市": "财经", "经济": "财经", "金融": "财经",
    "科技": "科技", "芯片": "科技", "新能源": "科技", "半导体": "科技",
    "自媒体": "自媒体", "短视频": "自媒体", "AI创作": "自媒体", "内容创作": "自媒体",
    "人工智能": "AI", "大模型": "AI",
    "量化": "量化", "agent": "量化", "quant": "量化",
}

def infer_category(filepath):
    name = Path(filepath).stem.lower()
    for key, cat in CATEGORY_MAP.items():
        if key in name:
            return cat
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
        for kw, cat in TOPIC_KEYWORDS.items():
            if kw.lower() in first_line.lower():
                return cat
    except:
        pass
    return "AI"

def clean_text(text):
    text = text.replace("&#39;", "'").replace("&#32;", " ")
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_raw_v3(filepath):
    category = infer_category(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    articles = []
    seen_urls = set()

    # Method 1: Ranked Evidence Clusters
    cp = re.compile(
        r'###\s+\d+\.\s+(.+?)\s+\(score\s+[\d.]+,.*?\)\n'
        r'\d+\.\s+\[(\w+)\]\s+(.+?)\n'
        r'\s+-?\s*(\d{4}-\d{2}-\d{2})\s*\|', re.MULTILINE
    )
    for m in cp.finditer(content):
        title = clean_text(m.group(1))
        src = m.group(2); item_title = clean_text(m.group(3)); date_str = m.group(4)
        chunk = content[m.end():m.end()+600]
        um = re.search(r'URL:\s*(https?://[^\s\n]+)', chunk)
        em = re.search(r'Evidence:\s*(.+?)(?:\n\n|\n###|\n\d+\.\s+\[|\Z)', chunk, re.DOTALL)
        url = um.group(1) if um else ""
        evidence = clean_text(em.group(1)) if em else title
        if url and url not in seen_urls:
            seen_urls.add(url)
            articles.append({"date": date_str, "title": title if len(title)>10 else item_title,
                "summary": evidence[:300], "source": src.capitalize() if src!="hackernews" else "Hacker News",
                "sourceUrl": url, "category": category})

    # Method 2: All Items by Source
    ap = re.compile(
        r'\*\*([\w\d]+)\*\*\s+\(score:\d+\)\s+.*?\((\d{4}-\d{2}-\d{2})\).*?\n'
        r'\s+(.+?)\n\s+(https?://[^\s\n]+)', re.MULTILINE
    )
    for m in ap.finditer(content):
        item_id = m.group(1); date_str = m.group(2); title = clean_text(m.group(3)); url = m.group(4)
        chunk = content[m.end():m.end()+500]
        em = re.search(r'^\s*\*(\w+)\*\s*\n\s*(.+?)(?:\n\n|\n\*\*|\Z)', chunk, re.DOTALL)
        evidence = clean_text(em.group(2)) if em else title
        if url and url not in seen_urls:
            seen_urls.add(url)
            articles.append({"date": date_str, "title": title, "summary": evidence[:300],
                "source": "Hacker News" if item_id.isdigit() else "Reddit",
                "sourceUrl": url, "category": category})
    return articles

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", default=r"D:\Last30Days")
    p.add_argument("--output", default=r"D:\NewsDaily\news-data.json")
    args = p.parse_args()
    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"ERROR: {input_dir} not found"); sys.exit(1)

    all_articles = []
    all_files = list(input_dir.glob("*-raw-v3*.md")) + list(input_dir.glob("*-synthesis-*.md"))
        cat = infer_category(str(f))
        arts = parse_raw_v3(str(f))
        print(f"  {f.name} -> [{cat}] {len(arts)} articles")
        all_articles.extend(arts)

    all_articles.sort(key=lambda a: a["date"], reverse=True)
    seen = set(); unique = []
    for a in all_articles:
        if a["sourceUrl"] not in seen:
            seen.add(a["sourceUrl"]); unique.append(a)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    js_path = out.parent / "news-data.js"
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write("window.NEWS_DATA = " + json.dumps(unique, ensure_ascii=False, indent=2) + ";\n")

    cats = {}; days = set()
    for a in unique:
        cats[a["category"]] = cats.get(a["category"], 0) + 1
        days.add(a["date"])
    print(f"Done: {len(unique)} articles, {len(days)} days, cats: {cats}")
    print(f"Outp