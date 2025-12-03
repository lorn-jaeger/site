import json
import os
from datetime import datetime
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).parent
CONTENT_DIR = ROOT / "content" / "posts"
OUT_DIR = ROOT / "generated"
OUT_DIR.mkdir(parents=True, exist_ok=True)

md = markdown.Markdown(extensions=["fenced_code", "tables", "codehilite"])


def parse_post(path: Path):
    text = path.read_text(encoding="utf-8")
    meta = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            _, front, body = parts
            meta = yaml.safe_load(front) or {}
    html = md.convert(body)
    md.reset()  # allow reuse
    title = meta.get("title", path.stem)
    raw_date = meta.get("date", "1970-01-01")
    date_str = raw_date if isinstance(raw_date, str) else str(raw_date)
    try:
        dt = datetime.fromisoformat(date_str)
    except (ValueError, TypeError):
        dt = datetime(1970, 1, 1)
    tags = meta.get("tags") or []
    summary = meta.get("summary", "")
    return {
        "title": title,
        "date": date_str,
        "date_obj": dt,
        "tags": tags,
        "summary": summary,
        "slug": path.stem,
        "html": html,
    }


def render_post(post):
    parts = []
    parts.append('<article class="post-card">')
    parts.append(f"  <h3>{post['title']}</h3>")
    parts.append(f"  <p class=\"post-meta\">{post['date']}</p>")
    if post["summary"]:
        parts.append(f"  <p>{post['summary']}</p>")
    parts.append(f"  {post['html']}")
    parts.append("</article>")
    return "\n".join(parts)


def main():
    posts = [parse_post(p) for p in sorted(CONTENT_DIR.glob("*.md"))]
    posts.sort(key=lambda p: p["date_obj"], reverse=True)

    posts_html = "\n\n".join(render_post(p) for p in posts)
    (OUT_DIR / "posts.html").write_text(posts_html, encoding="utf-8")

    meta_out = [
        {"title": p["title"], "date": p["date"], "tags": p["tags"], "slug": p["slug"], "summary": p["summary"]}
        for p in posts
    ]
    (OUT_DIR / "posts.json").write_text(json.dumps(meta_out, indent=2), encoding="utf-8")
    print(f"Wrote {len(posts)} posts to {OUT_DIR}/posts.html")


if __name__ == "__main__":
    main()
