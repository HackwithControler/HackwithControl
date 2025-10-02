# 🔒 安全性檢查報告

**檢查日期：** 2025-01-03
**檢查範圍：** HackwithControler Blog 全部程式碼
**嚴重程度分級：** 🔴 高危 | 🟠 中危 | 🟡 低危 | ✅ 安全

---

## 📋 執行摘要

**總體評估：** ⚠️ **存在中度風險**

發現的問題：
- 🔴 高危：1 個
- 🟠 中危：2 個
- 🟡 低危：3 個
- ✅ 安全：多項檢查通過

**建議採取行動：** 立即修復高危和中危問題

---

## 🔴 高危問題

### 1. 命令注入風險 (blog.py Line 127)

**問題代碼：**
```python
os.system(f"{os.environ.get('EDITOR','vim')} {filepath}")
```

**風險描述：**
- 使用 `os.system()` 執行外部命令
- 如果 `EDITOR` 環境變數被惡意設置，可能導致任意命令執行
- 檔案路徑 `filepath` 未經適當轉義

**攻擊場景：**
```bash
# 攻擊者設置惡意環境變數
export EDITOR='vim; rm -rf /'
python3 blog.py new
```

**影響範圍：** 本地開發環境

**修復建議：**
```python
# 使用 subprocess 並進行適當轉義
import subprocess
import shlex

# 方法 1: 使用 list 參數（推薦）
editor = os.environ.get('EDITOR', 'vim')
subprocess.run([editor, str(filepath)])

# 方法 2: 使用 shlex.quote 轉義
editor = os.environ.get('EDITOR', 'vim')
subprocess.run(f"{shlex.quote(editor)} {shlex.quote(str(filepath))}", shell=True)
```

**優先級：** 🔴 高 - 立即修復

---

## 🟠 中危問題

### 2. XSS 風險 - HTML 注入 (blog.py Multiple Lines)

**問題代碼：**
```python
# Line 236
tags_html = ''.join([f'<span class="article-tag">{t}</span>' for t in meta.get('tags',[])])

# Line 354
tags_html = ''.join([f'<span class="card-tag">{t}</span>' for t in meta.get('tags',[])])

# Line 198, 243, 359 等多處
html += f'''<div class="sidebar-article-title">{article['title']}</div>'''
```

**風險描述：**
- 用戶輸入（title, tags）直接插入 HTML，未經轉義
- 如果 Markdown Front Matter 包含惡意 HTML/JavaScript，會被直接渲染

**攻擊場景：**
```yaml
---
title: "HTB: Test<script>alert('XSS')</script>"
tags: [HTB, "<img src=x onerror='alert(1)'>"]
---
```

**影響範圍：** 生成的 HTML 文件

**修復建議：**
```python
import html

# 方法 1: 使用 html.escape
def escape_html(text):
    """轉義 HTML 特殊字符"""
    return html.escape(str(text))

# 使用範例
tags_html = ''.join([f'<span class="article-tag">{escape_html(t)}</span>'
                     for t in meta.get('tags',[])])

html += f'''<div class="sidebar-article-title">{escape_html(article['title'])}</div>'''
```

**優先級：** 🟠 中 - 儘快修復

---

### 3. ReDoS 風險 - 正則表達式拒絕服務 (blog.py Line 179)

**問題代碼：**
```python
headings = re.findall(r'<h([23])\s+id="([^"]*)"[^>]*>(.*?)</h[23]>', html_content)
```

**風險描述：**
- `[^>]*` 和 `(.*?)` 組合可能導致回溯爆炸
- 處理超大 HTML 文件時可能導致 CPU 100% 卡死

**攻擊場景：**
```markdown
# 超大標題
## <h2 id="test">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>...（數萬個字符）
```

**修復建議：**
```python
import re

# 使用更嚴格的模式，避免過度回溯
headings = re.findall(
    r'<h([23])\s+id="([^"]{0,200})"[^>]{0,100}>(.*?)</h[23]>',
    html_content,
    re.DOTALL
)

# 或使用 timeout（Python 3.11+）
try:
    headings = re.findall(
        pattern,
        html_content,
        timeout=1.0  # 1 秒超時
    )
except TimeoutError:
    print("正則表達式處理超時")
    headings = []
```

**優先級：** 🟠 中 - 建議修復

---

## 🟡 低危問題

### 4. 路徑遍歷風險 (blog.py Line 110)

**問題代碼：**
```python
filename = f"htb_{title.lower().replace(' ','_')}.md"
filepath = self.articles_dir / filename
```

**風險描述：**
- 用戶輸入的 `title` 可能包含 `../` 導致路徑遍歷
- 雖然使用 `Path` 可以部分緩解，但仍不夠安全

**攻擊場景：**
```bash
python3 blog.py new "../../../etc/passwd" "Easy" "HTB"
```

**修復建議：**
```python
import re

def sanitize_filename(name):
    """清理檔案名稱，移除危險字符"""
    # 移除路徑分隔符和其他危險字符
    name = re.sub(r'[^\w\s-]', '', name)
    # 限制長度
    name = name[:100]
    # 轉換為小寫並替換空格
    return name.lower().replace(' ', '_')

filename = f"htb_{sanitize_filename(title)}.md"
filepath = self.articles_dir / filename

# 額外驗證：確保路徑在 articles 目錄內
filepath = filepath.resolve()
if not str(filepath).startswith(str(self.articles_dir.resolve())):
    raise ValueError("不安全的檔案路徑")
```

**優先級：** 🟡 低 - 建議修復

---

### 5. YAML 反序列化風險 (blog.py Line 134)

**問題代碼：**
```python
return yaml.safe_load(match.group(1)), match.group(2)
```

**風險描述：**
- 使用 `yaml.safe_load` 已經是安全的選擇
- 但仍需注意 YAML bomb 攻擊（超大物件）

**攻擊場景：**
```yaml
---
tags: &ref [*ref, *ref, *ref, ...]  # 指數級增長
---
```

**修復建議：**
```python
# 限制 YAML 大小和深度
def parse_front_matter(self, content):
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if match:
        try:
            yaml_content = match.group(1)

            # 限制 YAML 大小（例如 10KB）
            if len(yaml_content) > 10240:
                print("警告：Front Matter 過大，略過")
                return {}, content

            # 使用 safe_load 並捕獲異常
            meta = yaml.safe_load(yaml_content)

            # 驗證返回類型
            if not isinstance(meta, dict):
                return {}, content

            return meta, match.group(2)
        except yaml.YAMLError as e:
            print(f"YAML 解析錯誤：{e}")
            return {}, content
    return {}, content
```

**優先級：** 🟡 低 - 可選修復

---

### 6. HTTP 伺服器安全性 (blog.py Line 407)

**問題代碼：**
```python
with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
    httpd.serve_forever()
```

**風險描述：**
- `SimpleHTTPRequestHandler` 會暴露整個當前目錄
- 監聽 `""` (0.0.0.0) 表示所有網路介面，可能被外部訪問
- 缺少存取控制

**攻擊場景：**
```bash
# 在本地執行 serve
python3 blog.py serve

# 攻擊者可以訪問：
http://your-ip:8009/blog.py  # 下載原始碼
http://your-ip:8009/.git/    # 如果存在
http://your-ip:8009/.env     # 敏感資料
```

**修復建議：**
```python
def serve(self, port=8009):
    import http.server
    import socketserver
    import os

    # 自訂 Handler，限制存取範圍
    class RestrictedHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            # 限制存取路徑
            super().__init__(*args, directory=os.getcwd(), **kwargs)

        def do_GET(self):
            # 阻止存取敏感文件
            forbidden = ['.git', '.env', 'blog.py', 'deploy.sh', '__pycache__']
            if any(forbidden_path in self.path for forbidden_path in forbidden):
                self.send_error(403, "Forbidden")
                return
            super().do_GET()

    print(f"啟動伺服器: http://localhost:{port}")
    print("⚠️  警告：此為開發伺服器，僅用於本地預覽")
    print("⚠️  不要暴露到公網")

    try:
        # 只監聽 localhost，不監聽所有介面
        with socketserver.TCPServer(("127.0.0.1", port), RestrictedHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
```

**優先級：** 🟡 低 - 建議修復

---

## ✅ 通過的安全檢查

### 1. ✅ SQL 注入
- **狀態：** 無風險
- **原因：** 不使用資料庫

### 2. ✅ YAML 注入
- **狀態：** 低風險
- **原因：** 使用 `yaml.safe_load()` 而非 `yaml.load()`

### 3. ✅ 檔案上傳
- **狀態：** 無風險
- **原因：** 不涉及檔案上傳功能

### 4. ✅ CSRF
- **狀態：** 無風險
- **原因：** 靜態網站，無表單提交

### 5. ✅ 敏感資訊洩露
- **狀態：** 低風險
- **原因：** `.gitignore` 已配置排除敏感文件

### 6. ✅ 依賴套件安全
- **狀態：** 需定期檢查
- **建議：** 定期執行 `pip audit` 或 `safety check`

---

## 🔐 JavaScript 安全性檢查

### home.js

**檢查項目：**

1. ✅ **DOM XSS** - 安全
   - 使用 `textContent` 而非 `innerHTML`
   - 標籤雲使用 `dataset` API

2. ✅ **事件處理** - 安全
   - 適當使用事件委派
   - 無 `eval()` 或 `Function()` 構造器

3. ⚠️ **潛在問題：** 標籤過濾 (Line 156+)
   ```javascript
   // 如果用戶可以控制標籤內容，可能有 XSS 風險
   tagElement.textContent = tag;  // ✅ 安全，使用 textContent
   ```

**總體評估：** ✅ JavaScript 代碼安全

---

## 📊 GitHub Actions 安全性

### .github/workflows/deploy.yml

**檢查項目：**

1. ✅ **權限最小化**
   ```yaml
   permissions:
     contents: read      # ✅ 只讀
     pages: write       # 必要權限
     id-token: write    # 必要權限
   ```

2. ✅ **固定版本**
   ```yaml
   uses: actions/checkout@v4           # ✅ 固定主版本
   uses: actions/setup-python@v5       # ✅ 固定主版本
   ```

3. ⚠️ **建議改進：** 使用 SHA 固定版本
   ```yaml
   # 更安全的做法
   uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
   ```

4. ✅ **無密鑰硬編碼**

5. ✅ **依賴快取**
   ```yaml
   cache: 'pip'  # ✅ 加速建置
   ```

**總體評估：** ✅ GitHub Actions 配置安全

---

## 🛡️ 立即修復建議

### 優先修復清單

1. **🔴 高優先級 - 立即修復**
   - [ ] 修復命令注入風險 (blog.py Line 127)

2. **🟠 中優先級 - 本週修復**
   - [ ] 修復 XSS 風險 - 添加 HTML 轉義
   - [ ] 修復 ReDoS 風險 - 優化正則表達式

3. **🟡 低優先級 - 下次更新時修復**
   - [ ] 加強檔案名稱驗證
   - [ ] 限制 YAML 大小
   - [ ] 限制 HTTP 伺服器存取範圍

---

## 🔧 修復後的安全代碼

完整修復的 `blog.py` 關鍵部分：

```python
import html
import subprocess
import shlex
import re

class BlogManager:
    # ... 其他代碼 ...

    def sanitize_filename(self, name):
        """清理檔案名稱"""
        name = re.sub(r'[^\w\s-]', '', name)
        return name[:100].lower().replace(' ', '_')

    def escape_html(self, text):
        """轉義 HTML"""
        return html.escape(str(text))

    def new_article(self, title=None, difficulty=None, tags=None):
        # ... 前面代碼 ...

        # 安全的檔案名稱生成
        filename = f"htb_{self.sanitize_filename(title)}.md"
        filepath = self.articles_dir / filename

        # 驗證路徑
        filepath = filepath.resolve()
        if not str(filepath).startswith(str(self.articles_dir.resolve())):
            raise ValueError("不安全的檔案路徑")

        # ... 中間代碼 ...

        # 安全的編輯器調用
        if input("立即編輯? (y/n): ").lower() == 'y':
            editor = os.environ.get('EDITOR', 'vim')
            subprocess.run([editor, str(filepath)])

    def generate_sidebar_articles(self, all_articles, current_file):
        """生成文章列表側邊欄 - 安全版本"""
        html = '<h3>📝 其他 Write-ups</h3><div class="sidebar-articles">'
        for article in all_articles:
            active_class = ' active' if article['filename'] == current_file else ''
            # 使用 HTML 轉義
            title = self.escape_html(article['title'])
            difficulty = self.escape_html(article['difficulty'].title())
            date = self.escape_html(article['date'])

            html += f'''
            <a href="{article['filename']}.html" class="sidebar-article-item{active_class}">
                <div class="sidebar-article-title">{title}</div>
                <div class="sidebar-article-meta">
                    <span class="sidebar-difficulty {article['difficulty']}">{difficulty}</span>
                    <span>{date}</span>
                </div>
            </a>'''
        html += '</div>'
        return html
```

---

## 📝 安全檢查清單

### 開發階段
- [ ] 所有用戶輸入進行驗證和清理
- [ ] 使用參數化查詢（如適用）
- [ ] 轉義所有動態生成的 HTML
- [ ] 使用 `subprocess` 代替 `os.system`
- [ ] 限制文件大小和上傳類型
- [ ] 添加速率限制（如適用）

### 部署階段
- [ ] 移除調試資訊
- [ ] 設置適當的 CORS 政策
- [ ] 使用 HTTPS
- [ ] 定期更新依賴套件
- [ ] 監控錯誤日誌

### 維護階段
- [ ] 每月執行 `pip audit`
- [ ] 定期更新 GitHub Actions
- [ ] 審查存取日誌
- [ ] 備份重要資料

---

## 📚 安全資源

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Markdown Security](https://github.com/commonmark/commonmark-spec/wiki/markdown-security)

---

## 🆘 緊急聯絡

如發現安全漏洞，請：
1. **不要**公開披露
2. 私下聯絡維護者
3. 提供詳細的漏洞報告
4. 等待修復後再公開

---

**檢查人員：** Claude (AI Security Auditor)
**下次檢查：** 建議每季度進行一次安全審查
**版本：** 1.0
