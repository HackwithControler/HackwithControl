#!/usr/bin/env python3
"""HackWithControler Blog 管理系統"""
import os, sys, re, json, http.server, socketserver, subprocess, html
from datetime import datetime
from pathlib import Path

try:
    import yaml, markdown
    from markdown.extensions import fenced_code, tables, codehilite, toc
except ImportError:
    print("請執行: pip3 install -r requirements.txt")
    sys.exit(1)

class BlogManager:
    def __init__(self):
        self.articles_dir = Path('articles')
        self.output_dir = Path('articles')
        self.index_file = Path('index.html')
        self.md = markdown.Markdown(extensions=['fenced_code','tables','codehilite','toc','nl2br','sane_lists'])

    def escape_html(self, text):
        """轉義 HTML 特殊字符，防止 XSS 攻擊"""
        return html.escape(str(text))

    def sanitize_filename(self, name):
        """清理檔案名稱，防止路徑遍歷攻擊"""
        # 移除危險字符，只保留字母、數字、空格、連字符
        name = re.sub(r'[^\w\s-]', '', name)
        # 限制長度為 100 字符
        name = name[:100]
        # 轉換為小寫並替換空格為底線
        return name.lower().replace(' ', '_').strip('_')
    
    def init_project(self):
        print("初始化專案...")
        self.articles_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self._create_template()
        self._create_example()
        print("完成! 執行: python3 blog.py new")
    
    def _create_template(self):
        template = """---
title: "HTB: Machine Name"
difficulty: Easy
date: {date}
tags: [HTB, Linux, Web]
featured: false
excerpt: "簡短描述..."
# type: writeup  # 可選：writeup (150字/分) 或 article (200字/分)
#                # 不指定時會根據標籤自動判斷（HTB/CTF → writeup）
# reading_speed: 150  # 可選：自訂閱讀速度（字元/分鐘）
---

## 機器資訊
- 平台: HTB
- 難度: Easy
- IP: 10.10.11.xxx

## 偵察
```bash
nmap -sC -sV 10.10.11.xxx
```

## Initial Access
...

## 權限提升
...

## Flags
```
user.txt: xxx
root.txt: xxx
```
""".format(date=datetime.now().strftime('%Y-%m-%d'))
        Path('article-template.md').write_text(template, encoding='utf-8')
    
    def _create_example(self):
        example = """---
title: "HTB: Example Machine"
difficulty: Medium
date: 2025-01-15
tags: [HTB, Linux, Web, SQLi]
featured: true
excerpt: "範例文章，展示如何使用 Markdown 撰寫 write-up"
---

## 機器資訊
- 平台: Hack The Box
- 難度: Medium
- IP: 10.10.11.200

## 偵察
```bash
nmap -sC -sV 10.10.11.200
```

## Initial Access
發現 SQL 注入漏洞。

## 權限提升
利用 SUID 文件提權。

## Flags
```
user.txt: xxx
root.txt: xxx
```
"""
        (self.articles_dir / 'example.md').write_text(example, encoding='utf-8')
    
    def new_article(self, title=None, difficulty=None, tags=None):
        print("\n新增文章")
        if not title:
            title = input("機器名稱: ").strip()
        if not difficulty:
            difficulty = input("難度 [Easy]: ").strip() or "Easy"
        if not tags:
            tags = input("標籤 [HTB,Linux]: ").strip() or "HTB,Linux"

        featured = input("Featured? (y/n) [n]: ").strip().lower() == 'y'

        # 🔒 安全：使用 sanitize_filename 清理檔案名稱
        safe_title = self.sanitize_filename(title)
        if not safe_title:
            print("❌ 錯誤：無效的文章標題")
            return

        filename = f"htb_{safe_title}.md"
        filepath = self.articles_dir / filename

        # 🔒 安全：驗證路徑在 articles 目錄內
        filepath = filepath.resolve()
        if not str(filepath).startswith(str(self.articles_dir.resolve())):
            print("❌ 錯誤：不安全的檔案路徑")
            return

        if filepath.exists():
            if input("文件存在，覆蓋? (y/n): ").lower() != 'y':
                return

        template = Path('article-template.md').read_text(encoding='utf-8')
        content = template.replace("Machine Name", title)
        content = content.replace("difficulty: Easy", f"difficulty: {difficulty}")
        content = content.replace("tags: [HTB, Linux, Web]", f"tags: [{tags}]")
        content = content.replace("featured: false", f"featured: {str(featured).lower()}")

        filepath.write_text(content, encoding='utf-8')
        print(f"已創建: {filepath}")

        # 🔒 安全：使用 subprocess.run 代替 os.system
        if input("立即編輯? (y/n): ").lower() == 'y':
            editor = os.environ.get('EDITOR', 'vim')
            try:
                subprocess.run([editor, str(filepath)])
            except Exception as e:
                print(f"❌ 編輯器啟動失敗: {e}")
        print("執行: python3 blog.py build")
    
    def parse_front_matter(self, content):
        """解析 Front Matter，帶有安全檢查"""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
        if match:
            try:
                yaml_content = match.group(1)

                # 🔒 安全：限制 YAML 大小（10KB）防止 YAML bomb
                if len(yaml_content) > 10240:
                    print("⚠️  警告：Front Matter 過大，使用預設值")
                    return {}, content

                # 使用 safe_load 防止任意代碼執行
                meta = yaml.safe_load(yaml_content)

                # 驗證返回類型
                if not isinstance(meta, dict):
                    print("⚠️  警告：Front Matter 格式錯誤")
                    return {}, content

                return meta, match.group(2)
            except yaml.YAMLError as e:
                print(f"⚠️  YAML 解析錯誤：{e}")
                return {}, content
        return {}, content

    def calculate_reading_time(self, markdown_content, meta):
        """
        智能計算閱讀時間
        - 支援 type 欄位 (writeup / article)
        - 支援自訂 reading_speed
        - 根據標籤自動判斷文章類型
        """
        # 1. 檢查是否有自訂閱讀速度
        if 'reading_speed' in meta:
            speed = meta['reading_speed']
            return max(1, round(len(markdown_content) / speed))

        # 2. 確定文章類型
        article_type = meta.get('type', None)

        # 如果沒有指定 type，根據標籤自動判斷
        if not article_type:
            tags = meta.get('tags', [])
            tags_lower = [str(t).lower() for t in tags]

            # 如果有 HTB, CTF 等標籤 → writeup
            if any(tag in tags_lower for tag in ['htb', 'thm', 'vulnhub', 'ctf', 'hackthebox']):
                article_type = 'writeup'
            else:
                article_type = 'article'

        # 3. 根據類型選擇閱讀速度
        reading_speeds = {
            'writeup': 150,   # Write-up / 打靶機（程式碼多，需要慢讀）
            'article': 200,   # 技術文章 / 教學 / 分析（正常速度）
        }

        speed = reading_speeds.get(article_type, 200)

        # 4. 計算閱讀時間
        read_time = max(1, round(len(markdown_content) / speed))

        return read_time
    
    def extract_toc(self, html_content):
        """從 HTML 內容中提取 H2 和 H3 標題生成 TOC"""
        # 🔒 安全：限制匹配長度，防止 ReDoS 攻擊
        headings = re.findall(
            r'<h([23])\s+id="([^"]{0,200})"[^>]{0,100}>(.*?)</h[23]>',
            html_content
        )
        toc_items = []
        for level, id_attr, text in headings:
            # 移除 HTML 標籤（限制長度）
            clean_text = re.sub(r'<[^>]+>', '', text[:500])
            toc_items.append({
                'level': int(level),
                'id': id_attr,
                'text': clean_text
            })
        return toc_items

    def generate_sidebar_articles(self, all_articles, current_file):
        """生成文章列表側邊欄 - 帶 HTML 轉義"""
        html = '<h3>📝 其他 Write-ups</h3><div class="sidebar-articles">'
        for article in all_articles:
            active_class = ' active' if article['filename'] == current_file else ''
            # 🔒 安全：轉義所有用戶輸入防止 XSS
            title = self.escape_html(article['title'])
            difficulty = self.escape_html(article['difficulty'].title())
            date = self.escape_html(article['date'])
            filename = self.escape_html(article['filename'])

            html += f'''
            <a href="{filename}.html" class="sidebar-article-item{active_class}">
                <div class="sidebar-article-title">{title}</div>
                <div class="sidebar-article-meta">
                    <span class="sidebar-difficulty {article['difficulty']}">{difficulty}</span>
                    <span>{date}</span>
                </div>
            </a>'''
        html += '</div>'
        return html

    def generate_toc_html(self, toc_items):
        """生成 TOC HTML - 帶 HTML 轉義"""
        if not toc_items:
            return ''

        html = '<h3>📑 目錄</h3><ul class="toc-list">'
        for item in toc_items:
            item_class = 'toc-item-h3' if item['level'] == 3 else 'toc-item-h2'
            # 🔒 安全：轉義 TOC 內容
            id_safe = self.escape_html(item['id'])
            text_safe = self.escape_html(item['text'])

            html += f'''
            <li class="toc-item {item_class}">
                <a href="#{id_safe}" class="toc-link">{text_safe}</a>
            </li>'''
        html += '</ul>'
        return html

    def generate_html(self, title, content, meta, markdown_content, all_articles=None, current_file=None):
        # 計算閱讀時間
        read_time = self.calculate_reading_time(markdown_content, meta)

        # 提取 TOC
        toc_items = self.extract_toc(content)
        toc_html = self.generate_toc_html(toc_items)

        # 生成文章列表側邊欄
        sidebar_articles_html = ''
        if all_articles:
            sidebar_articles_html = self.generate_sidebar_articles(all_articles, current_file)

        # 🔒 安全：轉義標籤內容防止 XSS
        tags_html = ''.join([f'<span class="article-tag">{self.escape_html(t)}</span>'
                            for t in meta.get('tags',[])])

        # 🔒 安全：轉義標題和其他 meta 資訊
        safe_title = self.escape_html(title)
        safe_difficulty = self.escape_html(meta.get('difficulty','Easy'))
        safe_date = self.escape_html(meta.get('date',datetime.now().strftime('%Y-%m-%d')))

        return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{safe_title} | HackwithControler</title>
<link rel="stylesheet" href="../static/css/main.css">
</head>
<body>
<header>
    <div class="container">
        <a href="../index.html" class="back">← 返回首頁</a>
    </div>
</header>

<div class="article-layout">
    <!-- Left Sidebar: Article List -->
    <aside class="sidebar-left">
        {sidebar_articles_html}
    </aside>

    <!-- Main Content -->
    <main class="article-main">
        <div class="article-header">
            <h1>{safe_title}</h1>
            <div class="article-meta">
                <span class="difficulty {meta.get('difficulty','easy').lower()}">{safe_difficulty}</span>
                <span>📅 {safe_date}</span>
                <span>⏱ {read_time} min read</span>
            </div>
            <div class="article-tags">{tags_html}</div>
        </div>
        <div class="article-content">{content}</div>
    </main>

    <!-- Right Sidebar: TOC -->
    <aside class="sidebar-right">
        {toc_html}
    </aside>
</div>

<footer>
    <div class="container">
        <p>&copy; 2024 HackwithControler. All rights reserved.</p>
    </div>
</footer>

<script src="../static/js/article.js"></script>
</body>
</html>"""
    
    def build_all(self):
        print("\n開始建置...")
        md_files = sorted(self.articles_dir.glob('*.md'), key=lambda x: x.stat().st_mtime, reverse=True)
        if not md_files:
            print("無文章")
            return

        # 第一階段：收集所有文章的 metadata
        all_articles_data = []
        articles_meta = {}

        for f in md_files:
            if f.name == 'article-template.md': continue

            content = f.read_text(encoding='utf-8')
            meta, md = self.parse_front_matter(content)

            meta.setdefault('title', f.stem.replace('_',' ').title())
            meta.setdefault('date', datetime.now().strftime('%Y-%m-%d'))
            meta.setdefault('difficulty', 'Easy')
            meta.setdefault('excerpt', re.sub(r'[#*`\[\]]','',md)[:150]+'...')
            meta.setdefault('tags', [])

            articles_meta[f.stem] = {
                'meta': meta,
                'md': md,
                'file': f
            }

            all_articles_data.append({
                'filename': f.stem,
                'title': meta['title'],
                'difficulty': meta['difficulty'].lower(),
                'date': meta['date']
            })

        # 第二階段：生成每篇文章的 HTML（包含完整的側邊欄）
        article_cards = []

        for article_info in all_articles_data:
            filename = article_info['filename']
            data = articles_meta[filename]
            meta = data['meta']
            md = data['md']
            f = data['file']

            print(f"處理: {f.name}")

            html = self.md.convert(md)
            self.md.reset()

            # 傳入所有文章資訊給 generate_html
            full_html = self.generate_html(
                meta['title'],
                html,
                meta,
                md,  # 傳入 markdown 內容用於計算閱讀時間
                all_articles=all_articles_data,
                current_file=filename
            )
            out = self.output_dir / f"{filename}.html"
            out.write_text(full_html, encoding='utf-8')

            # 生成首頁文章卡片 HTML
            read_time = self.calculate_reading_time(md, meta)
            # 🔒 安全：轉義所有用戶輸入
            tags_html = ''.join([f'<span class="card-tag">{self.escape_html(t)}</span>'
                                for t in meta.get('tags',[])])
            safe_card_title = self.escape_html(meta['title'])
            safe_card_date = self.escape_html(meta['date'])
            safe_card_diff = self.escape_html(meta['difficulty'])
            safe_card_excerpt = self.escape_html(meta['excerpt'])
            safe_filename = self.escape_html(filename)

            card_html = f"""
            <div class="article-card">
                <a href="articles/{safe_filename}.html">
                    <div class="card-content">
                        <h3 class="card-title">{safe_card_title}</h3>
                        <div class="card-meta">
                            <span class="card-date">{safe_card_date}</span>
                            <span class="card-difficulty {meta['difficulty'].lower()}">{safe_card_diff}</span>
                            <span class="card-read-time">{read_time} min read</span>
                        </div>
                        <p class="card-description">{safe_card_excerpt}</p>
                        <div class="card-tags">
                            {tags_html}
                        </div>
                    </div>
                </a>
            </div>
            """
            article_cards.append(card_html)

        # 更新 index.html
        self._update_index_html(article_cards)
        print(f"完成! {len(article_cards)} 篇文章")

    def _update_index_html(self, article_cards):
        """更新 index.html 的文章列表"""
        if not self.index_file.exists():
            print("警告: index.html 不存在")
            return

        content = self.index_file.read_text(encoding='utf-8')
        articles_html = '\n'.join(article_cards)

        # 替換 ARTICLE_LIST_START 和 ARTICLE_LIST_END 之間的內容
        pattern = r'(<!-- ARTICLE_LIST_START -->).*?(<!-- ARTICLE_LIST_END -->)'
        replacement = f'\\1\n{articles_html}\n            \\2'
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        self.index_file.write_text(new_content, encoding='utf-8')
        print("已更新 index.html")
    
    def list_articles(self):
        print("\n文章列表:")
        for i,f in enumerate(sorted(self.articles_dir.glob('*.md'), key=lambda x: x.stat().st_mtime, reverse=True), 1):
            if f.name == 'article-template.md': continue
            meta, _ = self.parse_front_matter(f.read_text(encoding='utf-8'))
            feat = '⭐' if meta.get('featured') else '  '
            print(f"{i:2d}. {feat} [{meta.get('difficulty','?'):6s}] {meta.get('title',f.name)}")
    
    def serve(self, port=8009):
        """啟動本地開發伺服器 - 帶安全限制"""
        # 🔒 安全：自訂 Handler，限制存取範圍
        class SecureHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=os.getcwd(), **kwargs)

            def do_GET(self):
                # 阻止存取敏感文件
                forbidden_patterns = [
                    '.git', '.env', '__pycache__', '.pyc',
                    'blog.py', 'deploy.sh', 'article-template.md',
                    'SECURITY_AUDIT.md', '.gitignore'
                ]
                if any(pattern in self.path for pattern in forbidden_patterns):
                    self.send_error(403, "Forbidden")
                    return
                super().do_GET()

            # 隱藏伺服器版本資訊
            def version_string(self):
                return "DevServer"

        print(f"🚀 啟動本地開發伺服器")
        print(f"📍 位址: http://localhost:{port}")
        print(f"⚠️  警告：此為開發伺服器，僅用於本地預覽")
        print(f"⚠️  不要暴露到公網！")
        print(f"按 Ctrl+C 停止")
        print()

        try:
            # 🔒 安全：只監聽 localhost (127.0.0.1)，不監聽所有介面
            with socketserver.TCPServer(("127.0.0.1", port), SecureHTTPRequestHandler) as httpd:
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✅ 伺服器已停止")
        except OSError as e:
            print(f"❌ 錯誤：{e}")
            print(f"💡 提示：端口 {port} 可能已被占用，請嘗試其他端口")

def main():
    if len(sys.argv) < 2:
        print("使用: python3 blog.py <command>")
        print("命令: init, new, build, list, serve")
        return
    
    cmd = sys.argv[1]
    m = BlogManager()
    
    if cmd == 'init': m.init_project()
    elif cmd == 'new':
        if len(sys.argv) >= 5:
            m.new_article(sys.argv[2], sys.argv[3], sys.argv[4])
        else:
            m.new_article()
    elif cmd == 'build': m.build_all()
    elif cmd == 'list': m.list_articles()
    elif cmd == 'serve': m.serve(int(sys.argv[2]) if len(sys.argv)>=3 else 8009)
    else: print(f"未知命令: {cmd}")

if __name__ == '__main__':
    main()
