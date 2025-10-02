# 🚀 GitHub Pages 自動部署指南

本指南說明如何將 HackwithControler Blog 部署到 GitHub Pages，並設定自動部署系統。

## 📋 目錄

1. [前置準備](#前置準備)
2. [初次設定](#初次設定)
3. [配置 GitHub Pages](#配置-github-pages)
4. [新增文章流程](#新增文章流程)
5. [常見問題](#常見問題)

---

## 前置準備

### 必要條件

- ✅ GitHub 帳號
- ✅ Git 已安裝並設定
- ✅ Python 3.8+ 已安裝
- ✅ 已安裝相依套件 (`pip install -r requirements.txt`)

---

## 初次設定

### 1. 創建 GitHub 倉庫

在 GitHub 上創建一個新的倉庫：

```bash
倉庫名稱：<你的用戶名>.github.io
# 例如：hackwithcontroler.github.io

描述：HackwithControler - 專業資安技術部落格
可見性：Public (必須是 Public 才能使用 GitHub Pages)
```

> **注意**：如果倉庫名稱為 `<username>.github.io`，網站會部署到 `https://<username>.github.io/`
>
> 如果使用其他名稱（如 `blog`），網站會部署到 `https://<username>.github.io/blog/`

### 2. 初始化本地 Git 倉庫

```bash
cd /Users/wangjj/Downloads/youtube/HackwithControlBlog

# 初始化 Git
git init

# 設定主分支名稱為 main
git branch -M main

# 添加遠端倉庫（替換成你的倉庫 URL）
git remote add origin https://github.com/<你的用戶名>/<倉庫名稱>.git
# 例如：git remote add origin https://github.com/hackwithcontroler/hackwithcontroler.github.io.git
```

### 3. 第一次提交並推送

```bash
# 建置部落格
python3 blog.py build

# 添加所有文件
git add .

# 提交
git commit -m "🎉 Initial commit - HackwithControler Blog"

# 推送到 GitHub
git push -u origin main
```

---

## 配置 GitHub Pages

### 1. 啟用 GitHub Pages

前往你的 GitHub 倉庫頁面：

1. 點擊 **Settings** (設定)
2. 左側選單點擊 **Pages**
3. **Source** (來源) 選擇：**GitHub Actions**

### 2. 驗證 GitHub Actions 權限

1. 前往 **Settings** > **Actions** > **General**
2. **Workflow permissions** 選擇：
   - ✅ **Read and write permissions**
3. 勾選：
   - ✅ **Allow GitHub Actions to create and approve pull requests**
4. 點擊 **Save**

### 3. 檢查部署狀態

1. 前往倉庫的 **Actions** 頁籤
2. 你應該會看到 "Deploy to GitHub Pages" workflow 正在執行
3. 等待約 2-3 分鐘，狀態變成 ✅ 綠色勾勾

### 4. 訪問你的網站

```
https://<你的用戶名>.github.io/
```

🎉 恭喜！你的部落格已成功部署！

---

## 新增文章流程

### 方法一：使用自動化腳本（推薦）

```bash
# 1. 新增文章
python3 blog.py new

# 2. 編輯文章
# 在 articles/ 目錄下編輯你的 Markdown 文件

# 3. 本地預覽
python3 blog.py serve
# 訪問 http://localhost:8009

# 4. 部署到 GitHub Pages
./deploy.sh
```

**deploy.sh 會自動執行：**
- ✅ 建置所有文章
- ✅ 提交變更到 Git
- ✅ 推送到 GitHub
- ✅ 觸發 GitHub Actions 自動部署

### 方法二：手動操作

```bash
# 1. 建置
python3 blog.py build

# 2. 提交
git add .
git commit -m "📝 新增文章: HTB Machine Name"

# 3. 推送
git push origin main
```

推送後，GitHub Actions 會自動：
1. 檢查程式碼
2. 安裝相依套件
3. 建置部落格
4. 部署到 GitHub Pages

---

## 自動部署工作流程

### GitHub Actions 流程

```
推送到 main 分支
    ↓
觸發 GitHub Actions
    ↓
安裝 Python + 相依套件
    ↓
執行 python3 blog.py build
    ↓
上傳建置結果
    ↓
部署到 GitHub Pages
    ↓
✅ 網站更新完成
```

### Workflow 文件位置

`.github/workflows/deploy.yml`

### 查看部署狀態

```
https://github.com/<你的用戶名>/<倉庫名稱>/actions
```

---

## 常見問題

### Q1: 推送後網站沒有更新？

**解決方法：**
1. 檢查 GitHub Actions 是否成功執行
2. 前往倉庫的 **Actions** 頁籤查看錯誤訊息
3. 常見錯誤：
   - 權限不足：檢查 Actions 權限設定
   - 建置失敗：檢查 `requirements.txt` 是否完整
   - Python 版本問題：確保本地和 Actions 使用相同版本

### Q2: 404 錯誤？

**原因：** 可能是 GitHub Pages 設定錯誤

**解決方法：**
1. 檢查 **Settings** > **Pages** > **Source** 是否選擇 **GitHub Actions**
2. 檢查倉庫是否為 Public
3. 清除瀏覽器快取並重新訪問

### Q3: CSS/JS 文件無法載入？

**原因：** 路徑設定問題

**解決方法：**
如果倉庫名稱不是 `<username>.github.io`，需要修改 `index.html` 中的路徑：

```html
<!-- 原本 -->
<link rel="stylesheet" href="static/css/main.css">

<!-- 改為 -->
<link rel="stylesheet" href="/倉庫名稱/static/css/main.css">
```

### Q4: 如何自訂網域？

**步驟：**
1. 在 DNS 提供商設定 CNAME 記錄指向 `<username>.github.io`
2. 在倉庫根目錄創建 `CNAME` 文件，內容為你的網域名稱
3. 前往 **Settings** > **Pages** > **Custom domain** 輸入網域
4. 勾選 **Enforce HTTPS**

### Q5: 如何回滾到先前版本？

```bash
# 查看提交歷史
git log --oneline

# 回滾到指定 commit
git revert <commit-hash>

# 推送
git push origin main
```

---

## 📊 部署統計與監控

### 查看部署歷史

```bash
# 前往
https://github.com/<你的用戶名>/<倉庫名稱>/deployments
```

### 啟用 Workflow Badge

在 `README.md` 中添加：

```markdown
![Deploy Status](https://github.com/<你的用戶名>/<倉庫名稱>/workflows/Deploy%20to%20GitHub%20Pages/badge.svg)
```

---

## 🔧 進階設定

### 自訂 Workflow 觸發條件

編輯 `.github/workflows/deploy.yml`：

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'articles/**'  # 只有 articles 目錄變更時才觸發
      - 'static/**'
      - 'index.html'
      - 'blog.py'
```

### 定時自動重建

```yaml
on:
  schedule:
    - cron: '0 0 * * 0'  # 每週日 00:00 自動重建
```

---

## 📝 工作流程圖

```
本地開發
    ↓
新增/編輯 Markdown 文章
    ↓
執行 ./deploy.sh
    ↓
    ├─ 建置文章 (blog.py build)
    ├─ Git commit
    └─ Git push
        ↓
    GitHub 接收推送
        ↓
    觸發 GitHub Actions
        ↓
        ├─ Checkout 程式碼
        ├─ 安裝 Python 環境
        ├─ 安裝相依套件
        ├─ 執行 blog.py build
        └─ 部署到 GitHub Pages
            ↓
        ✅ 網站更新完成
            ↓
        訪問 https://<username>.github.io/
```

---

## 🎯 快速參考

### 日常使用指令

```bash
# 新增文章
python3 blog.py new

# 本地預覽
python3 blog.py serve

# 部署
./deploy.sh
```

### 檢查清單

部署前確認：
- [ ] 文章 Front Matter 完整（title, date, difficulty, tags）
- [ ] 本地預覽正常
- [ ] 圖片路徑正確
- [ ] 沒有敏感資訊
- [ ] 建置成功

---

## 📚 相關資源

- [GitHub Pages 官方文件](https://docs.github.com/en/pages)
- [GitHub Actions 文件](https://docs.github.com/en/actions)
- [本專案 README](README.md)
- [使用說明](使用說明.md)

---

**最後更新：** 2025-01-03

**維護者：** HackwithControler

如有問題，請參考 [Issues](https://github.com/<你的用戶名>/<倉庫名稱>/issues)
