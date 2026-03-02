#!/usr/bin/env python3
"""
Batch beautify blog posts migrated from WordPress.
- Add description to frontmatter
- Fix code block language identifiers
- Clean up WordPress image links
- Fix unnecessary backslash escaping
- Add <!--more--> where missing
- Beautify archived comments with HTML wrapper
- Fill in missing categories/tags
"""

import os
import re
import glob
import yaml

POSTS_DIR = "/Users/calmp/myblog/content/posts"


def parse_frontmatter(content):
    """Parse YAML frontmatter and body from markdown file."""
    if not content.startswith("---"):
        return {}, content
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    fm_str = content[3:end].strip()
    body = content[end + 3:].strip()
    try:
        fm = yaml.safe_load(fm_str) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, body


def serialize_frontmatter(fm):
    """Serialize frontmatter dict back to YAML string."""
    lines = ["---"]
    # Keep a consistent field order
    order = ["title", "date", "description", "categories", "tags", "image"]
    written = set()
    for key in order:
        if key in fm:
            lines.append(dump_field(key, fm[key]))
            written.add(key)
    for key in fm:
        if key not in written:
            lines.append(dump_field(key, fm[key]))
    lines.append("---")
    return "\n".join(lines)


def dump_field(key, value):
    """Dump a single frontmatter field."""
    if isinstance(value, list):
        result = f"{key}: "
        if not value:
            return result
        items = []
        for item in value:
            items.append(f'\n  - "{item}"')
        return result + "".join(items)
    elif isinstance(value, str):
        # Escape backslashes and quotes for YAML
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'{key}: "{escaped}"'
    elif isinstance(value, bool):
        return f'{key}: {str(value).lower()}'
    else:
        return f'{key}: {value}'


def extract_description(body):
    """Extract a description from post body text."""
    # Remove the archived comments section
    text = re.split(r'<div class="archived-comments">', body)[0]
    text = re.split(r'## 历史评论', text)[0]

    # Get text before <!--more--> if present
    more_match = re.split(r'<!--\s*more\s*-->', text)
    if len(more_match) > 1:
        text = more_match[0]

    # Strip markdown formatting
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # images
    text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)  # links
    text = re.sub(r'```[\s\S]*?```', '', text)  # code blocks
    text = re.sub(r'`[^`]*`', '', text)  # inline code
    text = re.sub(r'#{1,6}\s+', '', text)  # headers
    text = re.sub(r'\*\*([^*]*)\*\*', r'\1', text)  # bold
    text = re.sub(r'\*([^*]*)\*', r'\1', text)  # italic
    text = re.sub(r'>\s*', '', text)  # blockquotes
    text = re.sub(r'[-*+]\s+', '', text)  # list markers
    text = re.sub(r'\\([_\[\]*#~`>|{}()!.+\-])', r'\1', text)  # backslash escapes
    text = re.sub(r'\n+', ' ', text)  # newlines
    text = text.strip()

    # Truncate to ~120 chars at word boundary
    if len(text) > 120:
        text = text[:120]
        # Try to cut at last Chinese char or space
        last_space = text.rfind(' ')
        last_comma = max(text.rfind('，'), text.rfind(','), text.rfind('。'), text.rfind('.'))
        cut_point = max(last_space, last_comma)
        if cut_point > 60:
            text = text[:cut_point]
        text = text.rstrip('，,。. ') + "..."
    return text


def guess_code_language(code_content):
    """Guess programming language from code block content."""
    lines = code_content.strip().split('\n')
    first_lines = '\n'.join(lines[:10]).lower()
    full = code_content.strip()

    # Shebang detection
    if full.startswith('#!/bin/bash') or full.startswith('#!/bin/sh'):
        return 'bash'
    if full.startswith('#!/usr/bin/env python') or full.startswith('#!/usr/bin/python'):
        return 'python'

    # YAML
    if re.search(r'^(apiVersion|kind|metadata|spec|name):', full, re.MULTILINE):
        return 'yaml'
    if re.search(r'^---\s*$', full, re.MULTILINE) and ':' in first_lines:
        return 'yaml'

    # Nginx config
    if re.search(r'\b(server\s*\{|location\s+|upstream\s+|proxy_pass|listen\s+\d)', full):
        return 'nginx'
    if re.search(r'(worker_processes|http\s*\{|events\s*\{|server_name)', full):
        return 'nginx'

    # Python
    if re.search(r'^(from\s+\w+\s+import|import\s+\w+|def\s+\w+|class\s+\w+)', full, re.MULTILINE):
        return 'python'
    if re.search(r'(print\(|if __name__|\.objects\.|\.filter\(|\.get\()', full):
        return 'python'

    # Go
    if re.search(r'^(package\s+\w+|func\s+\w+|import\s+\()', full, re.MULTILINE):
        return 'go'

    # JavaScript/JSX
    if re.search(r'(const\s+\w+|let\s+\w+|var\s+\w+|=>\s*\{|require\(|module\.exports)', full):
        return 'javascript'
    if re.search(r'(React\.|render\(|<\w+\s|import.*from\s+[\'"])', full):
        return 'jsx'

    # Shell commands
    if re.search(r'^(\$\s|#\s*(yum|apt|pip|npm|curl|wget|docker|kubectl|helm|git|cd|ls|cat|echo|mkdir|chmod|chown))', full, re.MULTILINE):
        return 'bash'
    if re.search(r'(sudo\s|yum\s|apt-get|pip\s+install|docker\s|kubectl\s|helm\s)', full):
        return 'bash'
    if re.search(r'^[a-z_]+\s+(install|start|stop|restart|enable|status)', full, re.MULTILINE):
        return 'bash'

    # SQL
    if re.search(r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE TABLE|ALTER TABLE|DROP)\b', full):
        return 'sql'

    # HTML
    if re.search(r'<(!DOCTYPE|html|head|body|div|span|script|style)\b', full, re.IGNORECASE):
        return 'html'

    # CSS
    if re.search(r'(\{[^}]*:\s*[^}]*;[^}]*\}|\.[\w-]+\s*\{|#[\w-]+\s*\{)', full):
        return 'css'

    # INI/TOML config
    if re.search(r'^\[[\w\s-]+\]\s*$', full, re.MULTILINE) and '=' in full:
        return 'ini'

    # JSON
    if full.strip().startswith('{') and full.strip().endswith('}'):
        return 'json'

    # Dockerfile
    if re.search(r'^(FROM|RUN|CMD|COPY|ADD|EXPOSE|ENV|ENTRYPOINT)\s', full, re.MULTILINE):
        return 'dockerfile'

    # Makefile
    if re.search(r'^[\w-]+:.*$', full, re.MULTILINE) and '\t' in full:
        return 'makefile'

    # C
    if re.search(r'(#include\s*<|int\s+main\(|printf\(|void\s+\w+\()', full):
        return 'c'

    # Generic config with key=value
    if re.search(r'^[\w_]+=', full, re.MULTILINE) and not re.search(r'[{}()]', full):
        return 'bash'

    return ''


def fix_code_blocks(body):
    """Add language identifiers to code blocks that don't have them."""
    def replace_block(match):
        lang = match.group(1) or ''
        content = match.group(2)
        if lang.strip():
            return match.group(0)  # Already has language
        guessed = guess_code_language(content)
        return f'```{guessed}\n{content}```'

    # Match code blocks: ```lang\ncontent```
    pattern = r'```(\w*)\n([\s\S]*?)```'
    return re.sub(pattern, replace_block, body)


def fix_wp_image_links(body):
    """Clean up WordPress image links.
    Convert [![](images/xxx.png)](http://www.calmkart.com/...) to ![](images/xxx.png)
    """
    # Pattern: [![](images/FILE)](http://www.calmkart.com/wp-content/uploads/...)
    pattern = r'\[!\[([^\]]*)\]\((images/[^)]+)\)\]\(http://www\.calmkart\.com/wp-content/uploads/[^)]+\)'
    replacement = r'![\1](\2)'
    return re.sub(pattern, replacement, body)


def fix_escape_sequences(body):
    """Remove unnecessary backslash escaping of underscores in text.
    Be careful not to modify URLs or code blocks.
    """
    # Only fix \_ that's NOT inside a URL (http...) or code block
    # Split by code blocks first
    parts = re.split(r'(```[\s\S]*?```|`[^`]+`)', body)
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 1:  # Inside code block
            result.append(part)
        else:
            # Fix \_ in plain text but not in URLs
            # Split by markdown links [text](url)
            link_parts = re.split(r'(\[[^\]]*\]\([^\)]*\))', part)
            fixed = []
            for j, lp in enumerate(link_parts):
                if j % 2 == 1:  # Inside a markdown link
                    # Fix \_ in display text but not in URL
                    link_match = re.match(r'\[([^\]]*)\]\(([^\)]*)\)', lp)
                    if link_match:
                        text = link_match.group(1).replace('\\_', '_')
                        url = link_match.group(2).replace('\\_', '_')
                        fixed.append(f'[{text}]({url})')
                    else:
                        fixed.append(lp)
                else:
                    fixed.append(lp.replace('\\_', '_'))
            result.append(''.join(fixed))
    return ''.join(result)


def add_more_tag(body):
    """Add <!--more--> after the first paragraph if missing."""
    if '<!--more-->' in body or '<!-- more -->' in body:
        return body

    lines = body.split('\n')
    # Find end of first non-empty paragraph
    in_paragraph = False
    insert_pos = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            if in_paragraph:
                insert_pos = i
                break
            continue
        if stripped.startswith('#'):
            # Skip headers, look for next paragraph
            continue
        if stripped.startswith('```'):
            # Don't insert in code blocks
            break
        in_paragraph = True

    if insert_pos > 0:
        lines.insert(insert_pos, '\n<!--more-->')
        return '\n'.join(lines)
    return body


def beautify_archived_comments(body):
    """Wrap archived comments in HTML div for custom styling."""
    # Check if already wrapped
    if '<div class="archived-comments">' in body:
        return body

    # Find the archived comments section
    pattern = r'(---\s*\n\s*## 历史评论.*?)$'
    match = re.search(pattern, body, re.DOTALL)
    if not match:
        return body

    comments_section = match.group(1)
    before = body[:match.start()]

    # Parse the comments
    lines = comments_section.split('\n')
    html_lines = ['<div class="archived-comments">', '', '<h2>历史评论</h2>']

    # Extract comment count from header
    header_match = re.search(r'## 历史评论 \((\d+) 条\)', comments_section)
    if header_match:
        html_lines[2] = f'<h2>历史评论 ({header_match.group(1)} 条)</h2>'

    html_lines.append('<p class="comment-notice">以下评论来自原 WordPress 站点，仅作存档展示。</p>')

    # Parse individual comments
    i = 0
    while i < len(lines):
        line = lines[i]

        # Match a reply (indented with ↳)
        reply_match = re.match(r'\s*>\s*↳\s*\*\*(.+?)\*\*\s*\((.+?)\)', line)
        if reply_match:
            author = reply_match.group(1)
            date = reply_match.group(2)
            # Collect reply body
            reply_body_lines = []
            i += 1
            while i < len(lines):
                if lines[i].strip().startswith('>'):
                    content = re.sub(r'^\s*>\s*', '', lines[i])
                    if content.strip():
                        reply_body_lines.append(content.strip())
                    i += 1
                else:
                    break
            reply_body = ' '.join(reply_body_lines)
            html_lines.append(f'<div class="comment-item comment-reply">')
            html_lines.append(f'<div class="comment-meta"><strong>{author}</strong> ({date})</div>')
            html_lines.append(f'<div class="comment-body">{reply_body}</div>')
            html_lines.append('</div>')
            continue

        # Match a top-level comment
        comment_match = re.match(r'>\s*\*\*(.+?)\*\*\s*\((.+?)\)', line)
        if comment_match:
            author = comment_match.group(1)
            date = comment_match.group(2)
            # Collect comment body
            body_lines = []
            i += 1
            while i < len(lines):
                stripped = lines[i].strip()
                if stripped.startswith('>') and not stripped.startswith('> ↳'):
                    content = re.sub(r'^>\s*', '', stripped)
                    if content.strip():
                        body_lines.append(content.strip())
                    i += 1
                elif stripped.startswith('> ↳') or re.match(r'\s*>\s*↳', lines[i]):
                    break  # Next is a reply
                else:
                    break
            comment_body = ' '.join(body_lines)
            html_lines.append(f'<div class="comment-item">')
            html_lines.append(f'<div class="comment-meta"><strong>{author}</strong> ({date})</div>')
            html_lines.append(f'<div class="comment-body">{comment_body}</div>')
            html_lines.append('</div>')
            continue

        i += 1

    html_lines.append('</div>')

    return before.rstrip() + '\n\n' + '\n'.join(html_lines) + '\n'


# Posts that need categories/tags filled in
MISSING_METADATA = {
    "在阿里巴巴，我们如何先于用户发现和定位 Kubernetes 集群问题？": {
        "categories": ["计算机"],
        "tags": ["kubernetes", "k8s", "云原生", "SRE"],
    },
    "kuberhealthy详解": {
        "categories": ["计算机"],
        "tags": ["kubernetes", "k8s", "云原生", "监控"],
    },
}


def process_post(filepath):
    """Process a single post file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    fm, body = parse_frontmatter(content)
    if not fm:
        print(f"  SKIP (no frontmatter): {filepath}")
        return False

    changed = False

    # 1. Add description if missing
    if 'description' not in fm or not fm.get('description'):
        desc = extract_description(body)
        if desc and len(desc) > 10:
            fm['description'] = desc
            changed = True

    # 2. Fill missing categories/tags
    title = fm.get('title', '')
    if title in MISSING_METADATA:
        meta = MISSING_METADATA[title]
        if 'categories' not in fm or not fm.get('categories'):
            fm['categories'] = meta['categories']
            changed = True
        if 'tags' not in fm or not fm.get('tags'):
            fm['tags'] = meta['tags']
            changed = True

    # 3. Fix code blocks
    new_body = fix_code_blocks(body)
    if new_body != body:
        body = new_body
        changed = True

    # 4. Fix WordPress image links
    new_body = fix_wp_image_links(body)
    if new_body != body:
        body = new_body
        changed = True

    # 5. Fix escape sequences
    new_body = fix_escape_sequences(body)
    if new_body != body:
        body = new_body
        changed = True

    # 6. Add <!--more--> if missing
    new_body = add_more_tag(body)
    if new_body != body:
        body = new_body
        changed = True

    # 7. Beautify archived comments
    new_body = beautify_archived_comments(body)
    if new_body != body:
        body = new_body
        changed = True

    if changed:
        new_content = serialize_frontmatter(fm) + "\n\n" + body.strip() + "\n"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


def main():
    posts = glob.glob(os.path.join(POSTS_DIR, "**", "index.md"), recursive=True)
    posts.sort()

    print(f"Found {len(posts)} posts to process\n")

    modified = 0
    for filepath in posts:
        rel = os.path.relpath(filepath, POSTS_DIR)
        result = process_post(filepath)
        if result:
            print(f"  MODIFIED: {rel}")
            modified += 1
        else:
            print(f"  unchanged: {rel}")

    print(f"\nDone! Modified {modified}/{len(posts)} posts.")


if __name__ == "__main__":
    main()
