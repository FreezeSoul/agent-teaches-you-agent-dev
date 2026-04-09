#!/usr/bin/env python3
"""
生成文章地图 (Article Map)
- 按发布时间倒序排列
- 包含目录位置和创建时间
- 输出到仓库根目录 ARTICLES_MAP.md
"""

import subprocess
import os
from datetime import datetime

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(REPO_DIR, "ARTICLES_MAP.md")

def get_git_date(filepath: str) -> str:
    """获取文件首次提交的日期（创建时间）"""
    try:
        result = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%ai", "--", filepath],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            # 格式: 2026-04-09 04:08:04 +0800
            dt_str = result.stdout.strip().split()[0]
            return dt_str
    except Exception:
        pass
    return "unknown"

def extract_title(filepath: str) -> str:
    """从文章中提取标题（第一个 # 开头的内容）"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
    except Exception:
        pass
    return os.path.basename(filepath).replace(".md", "")

def get_all_articles():
    """遍历 articles/ 目录获取所有 .md 文件"""
    articles_dir = os.path.join(REPO_DIR, "articles")
    if not os.path.exists(articles_dir):
        return []

    articles = []
    for root, _, files in os.walk(articles_dir):
        for filename in sorted(files):
            if filename.endswith(".md"):
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, REPO_DIR)
                title = extract_title(filepath)
                date = get_git_date(rel_path)
                category = rel_path.split(os.sep)[1] if os.sep in rel_path else "root"
                articles.append({
                    "title": title,
                    "path": rel_path,
                    "category": category,
                    "date": date
                })
    return articles

def sort_key(article):
    """排序：日期倒序，未知日期排最后"""
    date_str = article["date"]
    if date_str == "unknown":
        return (1, "9999-99-99")
    return (0, date_str)

def generate_map():
    """生成文章地图 Markdown"""
    articles = get_all_articles()
    articles.sort(key=sort_key, reverse=True)

    lines = [
        "# 📚 Article Map\n",
        f"> Auto-generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"> Total articles: {len(articles)}\n",
        "---\n",
        "",
        "| # | Title | Category | Created | Path |",
        "|---|-------|----------|---------|------|",
    ]

    for i, art in enumerate(articles, 1):
        title = art["title"]
        category = art["category"]
        date = art["date"]
        path = art["path"]
        lines.append(f"| {i} | {title} | {category} | {date} | `{path}` |")

    return "\n".join(lines)

def main():
    print(f"📊 Generating article map for: {REPO_DIR}")
    content = generate_map()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Article map generated: {OUTPUT_FILE}")

    # 统计各类别数量
    articles = get_all_articles()
    categories = {}
    for art in articles:
        cat = art["category"]
        categories[cat] = categories.get(cat, 0) + 1

    print("\n📂 Category breakdown:")
    for cat, count in sorted(categories.items()):
        print(f"   {cat}: {count}")

if __name__ == "__main__":
    main()
