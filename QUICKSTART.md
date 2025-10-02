# 🚀 快速開始指南

## 新增文章只需三步驟

### 1️⃣ 創建文章

```bash
./new.sh "機器名稱" "難度" "標籤"
```

**範例：**
```bash
./new.sh "Boardlight" "Easy" "HTB,Linux,Dolibarr"
```

### 2️⃣ 編輯內容

```bash
vim articles/htb_boardlight.md
```

**最小文章結構：**

```markdown
---
title: "HTB: Boardlight"
difficulty: Easy
date: 2024-12-25
tags: [HTB, Linux, Dolibarr]
excerpt: "簡短描述..."
---

## 機器資訊
- IP: 10.10.11.xxx

## 偵察
（你的偵察步驟）

## Initial Access
（你的攻擊步驟）

## 權限提升
（你的提權步驟）

## Flags
```
user.txt: xxx
root.txt: xxx
```
```

### 3️⃣ 建置並預覽

```bash
python3 blog.py build
python3 blog.py serve
```

訪問 `http://localhost:8000` 查看效果！

---

## 📋 命令速查

| 做什麼 | 命令 |
|--------|------|
| 新增文章 | `./new.sh "標題" "難度" "標籤"` |
| 建置網站 | `python3 blog.py build` |
| 本地預覽 | `python3 blog.py serve` |
| 列出文章 | `python3 blog.py list` |
| 部署上線 | `./deploy.sh` |

---

## 🎯 完整範例

```bash
# 創建新文章
./new.sh "Keeper" "Easy" "HTB,Linux,KeePass,CVE-2023-32784"

# 編輯內容
vim articles/htb_keeper.md

# （撰寫你的 write-up...）

# 建置
python3 blog.py build

# 預覽
python3 blog.py serve

# 滿意後部署
./deploy.sh
```

---

## ✅ 文章會自動包含

當你執行 `build` 後，每篇文章自動擁有：

- ✅ **左側邊欄**：所有文章列表（可切換）
- ✅ **右側邊欄**：自動生成的目錄 (TOC)
- ✅ **滾動高亮**：當前閱讀位置自動高亮
- ✅ **響應式設計**：手機、平板、電腦都能完美顯示
- ✅ **首頁更新**：自動加入文章卡片

---

## 💡 記住這三個命令就夠了

```bash
./new.sh "標題" "難度" "標籤"  # 創建
vim articles/htb_xxx.md       # 編輯
python3 blog.py build         # 建置
```

**其他所有事情系統都會自動處理！** ✨

---

詳細說明請參考 [使用說明.md](使用說明.md)
