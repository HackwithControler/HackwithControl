# ⚡ 快速部署到 GitHub Pages

## 5 分鐘完成部署

### 步驟 1: 創建 GitHub 倉庫

前往 [GitHub](https://github.com/new) 創建新倉庫：

```
倉庫名稱：<你的用戶名>.github.io
描述：HackwithControler Blog
可見性：Public ✅
```

### 步驟 2: 初始化並推送

```bash
# 初始化 Git
git init
git branch -M main

# 連結遠端倉庫（替換成你的 URL）
git remote add origin https://github.com/<你的用戶名>/<你的用戶名>.github.io.git

# 建置部落格
python3 blog.py build

# 第一次提交
git add .
git commit -m "🎉 Initial commit"
git push -u origin main
```

### 步驟 3: 啟用 GitHub Pages

1. 前往倉庫 **Settings** → **Pages**
2. **Source** 選擇：**GitHub Actions**
3. **Actions** → **General** → **Workflow permissions**:
   - 選擇 **Read and write permissions** ✅
   - 勾選 **Allow GitHub Actions to create and approve pull requests** ✅

### 步驟 4: 等待部署完成

前往 **Actions** 頁籤，等待 2-3 分鐘，看到 ✅ 綠色勾勾即完成！

訪問：`https://<你的用戶名>.github.io/`

---

## 🎯 日常使用

### 新增文章並自動部署

```bash
# 1. 新增文章
python3 blog.py new

# 2. 編輯 Markdown 文件
# (在 articles/ 目錄)

# 3. 本地預覽
python3 blog.py serve

# 4. 一鍵部署
./deploy.sh
```

**就這麼簡單！** 🎉

推送後，GitHub Actions 會自動建置並部署，2-3 分鐘後網站就會更新。

---

## 🔍 查看部署狀態

```
https://github.com/<你的用戶名>/<倉庫名稱>/actions
```

---

## ⚠️ 常見問題

### 問題：推送失敗？

```bash
# 檢查遠端設定
git remote -v

# 重新設定
git remote set-url origin https://github.com/<正確的URL>
```

### 問題：網站 404？

1. 檢查倉庫是否為 **Public**
2. 檢查 **Settings** → **Pages** → **Source** 是否為 **GitHub Actions**
3. 清除瀏覽器快取

### 問題：CSS 無法載入？

如果倉庫名稱不是 `<username>.github.io`，需修改路徑：

```html
<!-- index.html -->
<link rel="stylesheet" href="/倉庫名稱/static/css/main.css">
```

---

## 📚 完整文件

詳細設定請參考 [DEPLOYMENT.md](DEPLOYMENT.md)
