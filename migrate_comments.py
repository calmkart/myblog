#!/usr/bin/env python3
"""
从 WordPress 导出 XML 中提取评论，追加到对应的 Hugo Markdown 文件末尾。
用法：python3 migrate_comments.py export.xml content/posts/
"""

import xml.etree.ElementTree as ET
import os
import sys
import glob
import re
from urllib.parse import unquote
from datetime import datetime
from html import unescape

WP_NS = "{http://wordpress.org/export/1.2/}"


def parse_posts_with_comments(xml_path):
    """解析 XML，返回有评论的文章列表"""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    channel = root.find("channel")

    results = []

    for item in channel.findall("item"):
        post_type = item.find(f"{WP_NS}post_type")
        if post_type is None or post_type.text != "post":
            continue

        status = item.find(f"{WP_NS}status")
        if status is not None and status.text != "publish":
            continue

        title = item.find("title").text or ""
        slug = item.find(f"{WP_NS}post_name").text or ""
        slug_decoded = unquote(slug)
        post_date = item.find(f"{WP_NS}post_date").text or ""

        comments = []
        for comment in item.findall(f"{WP_NS}comment"):
            approved = comment.find(f"{WP_NS}comment_approved")
            if approved is None or approved.text != "1":
                continue

            comment_type = comment.find(f"{WP_NS}comment_type")
            if comment_type is not None and comment_type.text in ("pingback", "trackback"):
                continue

            author = comment.find(f"{WP_NS}comment_author").text or "匿名"
            date_str = comment.find(f"{WP_NS}comment_date").text or ""
            content = comment.find(f"{WP_NS}comment_content").text or ""
            comment_id = comment.find(f"{WP_NS}comment_id").text or "0"
            parent_id = comment.find(f"{WP_NS}comment_parent").text or "0"

            content = unescape(content).strip()
            if not content:
                continue

            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                date_formatted = date_obj.strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                date_formatted = date_str

            comments.append({
                "id": comment_id,
                "parent": parent_id,
                "author": author,
                "date": date_formatted,
                "content": content,
            })

        if comments:
            results.append({
                "title": title,
                "slug": slug_decoded,
                "post_date": post_date,
                "comments": comments,
            })

    return results


def build_comment_tree(comments):
    """构建树状评论结构"""
    by_id = {c["id"]: c for c in comments}
    roots = []
    children_map = {}

    for c in comments:
        parent = c["parent"]
        if parent == "0" or parent not in by_id:
            roots.append(c)
        else:
            children_map.setdefault(parent, []).append(c)

    roots.sort(key=lambda x: x["date"])
    return roots, children_map


def render_comment(comment, children_map, depth=0):
    """渲染单条评论"""
    indent = "  " * depth
    prefix = "↳ " if depth > 0 else ""

    lines = []
    lines.append(f"{indent}> {prefix}**{comment['author']}** ({comment['date']})")
    lines.append(f"{indent}>")

    for line in comment["content"].split("\n"):
        line = line.strip()
        if line:
            lines.append(f"{indent}> {line}")
        else:
            lines.append(f"{indent}>")

    lines.append("")

    for child in children_map.get(comment["id"], []):
        lines.extend(render_comment(child, children_map, depth + 1))

    return lines


def render_comments_section(comments):
    """渲染评论区 Markdown"""
    roots, children_map = build_comment_tree(comments)

    lines = []
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"## 历史评论 ({len(comments)} 条)")
    lines.append("")
    lines.append("*以下评论来自原 WordPress 站点，仅作存档展示。*")
    lines.append("")

    for root in roots:
        lines.extend(render_comment(root, children_map))

    return "\n".join(lines)


def normalize(s):
    """标准化字符串用于模糊匹配：转小写、去空格和特殊字符"""
    s = s.lower()
    s = re.sub(r'[_\-\s　]+', '', s)
    s = re.sub(r'[《》（）()【】\[\]{}]', '', s)
    return s


def find_markdown_file(posts_dir, post):
    """根据文章信息查找对应的 Markdown 文件"""
    slug = post["slug"]
    title = post["title"]
    post_date = post["post_date"]

    all_md_files = glob.glob(os.path.join(posts_dir, "**", "index.md"), recursive=True)

    # 尝试从 post_date 提取日期前缀 (YYYY-MM-DD)
    date_prefix = ""
    if post_date:
        try:
            dt = datetime.strptime(post_date, "%Y-%m-%d %H:%M:%S")
            date_prefix = dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            pass

    # 策略1: slug 精确匹配目录名的一部分
    norm_slug = normalize(slug)
    for md_path in all_md_files:
        dir_name = os.path.basename(os.path.dirname(md_path))
        if norm_slug and norm_slug in normalize(dir_name):
            return md_path

    # 策略2: 标题匹配目录名
    norm_title = normalize(title)
    if norm_title and len(norm_title) > 2:
        for md_path in all_md_files:
            dir_name = os.path.basename(os.path.dirname(md_path))
            if norm_title in normalize(dir_name):
                return md_path

    # 策略3: 日期 + 部分标题
    if date_prefix and norm_title:
        for md_path in all_md_files:
            dir_name = os.path.basename(os.path.dirname(md_path))
            if date_prefix in dir_name and norm_title[:6] in normalize(dir_name):
                return md_path

    return None


def main():
    if len(sys.argv) < 3:
        print("用法: python3 migrate_comments.py <export.xml> <content/posts/>")
        sys.exit(1)

    xml_path = sys.argv[1]
    posts_dir = sys.argv[2]

    print(f"解析 WordPress XML: {xml_path}")
    posts = parse_posts_with_comments(xml_path)
    print(f"找到 {len(posts)} 篇有评论的文章\n")

    matched = 0
    unmatched = []
    total_comments = 0

    for post in posts:
        md_path = find_markdown_file(posts_dir, post)

        if md_path is None:
            unmatched.append(post)
            continue

        comments_md = render_comments_section(post["comments"])

        with open(md_path, "a", encoding="utf-8") as f:
            f.write(comments_md)

        matched += 1
        total_comments += len(post["comments"])
        print(f"  [OK] {os.path.relpath(md_path)} ({len(post['comments'])} 条评论)")

    print(f"\n===== 结果 =====")
    print(f"成功: {matched} 篇文章，共 {total_comments} 条评论")

    if unmatched:
        print(f"\n未匹配: {len(unmatched)} 篇（需手动处理）")
        for post in unmatched:
            print(f"  标题: {post['title']}")
            print(f"  slug: {post['slug']}")
            print(f"  日期: {post['post_date']}")
            print(f"  评论数: {len(post['comments'])}")
            print()


if __name__ == "__main__":
    main()
