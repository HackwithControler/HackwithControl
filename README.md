# HackwithControler - 資安技術部落格

[![Deploy Status](https://github.com/<your-username>/<your-repo>/workflows/Deploy%20to%20GitHub%20Pages/badge.svg)](https://github.com/<your-username>/<your-repo>/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

專業資安技術部落格系統，專注於 Hack The Box write-ups、滲透測試技術與 CVE 漏洞研究。

🌐 **Live Demo:** `https://<your-username>.github.io/`

## ✨ 特色功能

- 🎯 **自動部署** - 推送到 GitHub 自動建置並部署到 GitHub Pages
- 📝 **Markdown 寫作** - 使用 Markdown 撰寫，自動轉換為精美 HTML
- 🎨 **現代化設計** - Matrix 背景、Terminal 動畫、響應式設計
- 🔍 **SEO 優化** - 完整的 meta 標籤、Open Graph、結構化資料
- 🏷️ **標籤系統** - 自動生成標籤雲，支援標籤篩選
- 📊 **難度分類** - Easy/Medium/Hard/Insane 四級難度系統
- ⏱️ **智能閱讀時間** - 根據文章類型自動計算閱讀時間
- 🔎 **即時搜尋** - 標題、描述、標籤全文搜尋
- ♿ **可訪問性** - 完整的 ARIA 標籤支援

## 📁 專案結構

```
HackwithControlBlog/
├── .github/
│   └── workflows/
│       └── deploy.yml      # GitHub Actions 自動部署
├── index.html              # 首頁（SEO 優化）
├── articles/               # Markdown 文章 & 生成的 HTML
├── static/
│   ├── css/
│   │   └── main.css       # 統一樣式表
│   └── js/
│       ├── home.js        # 首頁互動功能
│       └── article.js     # 文章頁功能
├── blog.py                 # 部落格管理系統
├── deploy.sh               # 一鍵部署腳本
├── requirements.txt        # Python 依賴
├── DEPLOYMENT.md           # 詳細部署指南
└── QUICKSTART_DEPLOY.md    # 快速部署指南
```

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip3 install -r requirements.txt
```

### 2. 初始化專案

```bash
python3 blog.py init
```

這會創建：
- `articles/` 目錄
- `article-template.md` 模板文件
- 範例文章 `articles/example.md`

### 3. 新增文章

**互動式新增：**
```bash
python3 blog.py new
```

**快速新增：**
```bash
python3 blog.py new "Analytics" "Easy" "HTB,Linux,Web"
# 或使用腳本
./new.sh "Analytics" "Easy" "HTB,Linux,Web"
```

### 4. 編輯文章

文章使用 Markdown 格式，支援 Front Matter：

```markdown
---
title: "HTB: Analytics"
difficulty: Easy
date: 2025-01-15
tags: [HTB, Linux, Web]
featured: false
excerpt: "簡短描述文章內容"
---

## 機器資訊
- 平台: Hack The Box
- 難度: Easy
- IP: 10.10.11.xxx

## 偵察
\`\`\`bash
nmap -sC -sV 10.10.11.xxx
\`\`\`

## Initial Access
...

## 權限提升
...

## Flags
\`\`\`
user.txt: xxx
root.txt: xxx
\`\`\`
```

### 5. 建置網站

```bash
python3 blog.py build
```

這會：
- 將所有 `.md` 文章轉換為 HTML
- 自動更新 `index.html` 的文章列表
- 生成響應式的文章卡片

### 6. 本地預覽

```bash
python3 blog.py serve
# 或指定端口
python3 blog.py serve 3000
```

然後開啟瀏覽器訪問 `http://localhost:8000`

## 🚀 部署到 GitHub Pages

### 快速部署（推薦）

```bash
# 1. 創建 GitHub 倉庫 <your-username>.github.io
# 2. 初始化並連結
git init
git branch -M main
git remote add origin https://github.com/<your-username>/<your-username>.github.io.git

# 3. 第一次推送
python3 blog.py build
git add .
git commit -m "🎉 Initial commit"
git push -u origin main

# 4. 啟用 GitHub Pages
# 前往 Settings → Pages → Source: GitHub Actions
```

### 日常更新（自動部署）

```bash
# 新增文章後，執行一鍵部署
./deploy.sh
```

**就這麼簡單！** 推送後 GitHub Actions 會自動建置並部署，2-3 分鐘後網站就會更新。

📚 **詳細部署指南：** [DEPLOYMENT.md](DEPLOYMENT.md)
⚡ **快速開始：** [QUICKSTART_DEPLOY.md](QUICKSTART_DEPLOY.md)

---

## 📝 命令列表

| 命令 | 說明 |
|------|------|
| `python3 blog.py init` | 初始化專案結構 |
| `python3 blog.py new` | 互動式新增文章 |
| `python3 blog.py new "Title" "Diff" "Tags"` | 快速新增文章 |
| `python3 blog.py build` | 建置所有文章並更新首頁 |
| `python3 blog.py list` | 列出所有文章 |
| `python3 blog.py serve [port]` | 啟動本地伺服器預覽 |
| `./deploy.sh` | 一鍵部署到 GitHub Pages |

## 🔄 典型工作流程

```bash
# 1. 新增文章
./new.sh "Surveillance" "Medium" "HTB,Linux,Docker"

# 2. 編輯文章
vim articles/htb_surveillance.md

# 3. 建置
python3 blog.py build

# 4. 預覽
python3 blog.py serve

# 5. 部署
# 將整個目錄上傳到 GitHub Pages 或其他靜態網站託管服務
```

## 🎨 功能特色

- ✅ **Markdown 支援**：完整的 Markdown 語法，含程式碼高亮
- ✅ **自動建置**：自動生成 HTML 並更新首頁
- ✅ **響應式設計**：支援桌面和行動裝置
- ✅ **暗黑風格**：專業的資安主題配色
- ✅ **文章管理**：簡單的命令列介面
- ✅ **標籤系統**：文章分類和標記
- ✅ **難度標示**：Easy / Medium / Hard

## 📦 部署

### GitHub Pages

1. 初始化 Git 倉庫：
```bash
git init
git add .
git commit -m "Initial commit"
```

2. 推送到 GitHub：
```bash
git remote add origin https://github.com/你的用戶名/你的倉庫.git
git branch -M main
git push -u origin main
```

3. 在 GitHub 倉庫設定中啟用 GitHub Pages

### 其他平台

- **Netlify**：直接拖放整個目錄
- **Vercel**：連接 Git 倉庫自動部署
- **Cloudflare Pages**：支援靜態網站託管

## 🛠️ 自訂

### 修改樣式

編輯 `static/css/main.css` 來自訂顏色、字體等：

```css
:root {
    --primary: #00ff41;  /* 主要顏色 */
    --bg: #0a0e27;       /* 背景色 */
    --text: #e4e4e7;     /* 文字顏色 */
}
```

### 修改模板

編輯 `article-template.md` 來自訂新文章的預設模板

### 修改首頁

直接編輯 `index.html`，保留以下標記：

```html
<!-- ARTICLE_LIST_START -->
<!-- 這裡的內容會被自動替換 -->
<!-- ARTICLE_LIST_END -->
```

## 📄 授權

MIT License

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📮 聯絡

有問題或建議？歡迎開 Issue 討論。
