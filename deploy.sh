#!/bin/bash

# HackwithControler Blog 部署腳本
# 用於新增文章後自動建置並推送到 GitHub，觸發 GitHub Actions 自動部署

set -e  # 遇到錯誤立即停止

echo "🚀 開始部署 HackwithControler Blog..."
echo ""

# 1. 檢查 Git 倉庫
if [ ! -d ".git" ]; then
    echo "❌ 未找到 Git 倉庫"
    echo "💡 請先執行："
    echo "   git init"
    echo "   git remote add origin <你的 GitHub 倉庫 URL>"
    exit 1
fi

# 2. 建置所有文章
echo "📝 建置文章..."
python3 blog.py build

if [ $? -ne 0 ]; then
    echo "❌ 建置失敗！"
    exit 1
fi
echo "✅ 建置完成"
echo ""

# 3. 顯示變更的文件
echo "📋 變更的文件："
git status --short
echo ""

# 4. 提交訊息
read -p "提交訊息 (直接 Enter 使用預設): " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="📝 Update blog content - $(date +%Y-%m-%d)"
fi

# 5. Git 操作
echo "📦 提交更改到 Git..."
git add .

# 檢查是否有變更
if git diff --staged --quiet; then
    echo "⚠️  沒有變更需要提交"
    exit 0
fi

git commit -m "$commit_msg"

# 6. 推送到 GitHub
echo ""
echo "🌐 推送到 GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 部署成功！"
    echo "🤖 GitHub Actions 將自動建置並部署到 GitHub Pages"
    echo "⏱️  預計 2-3 分鐘後完成部署"
    echo ""
    echo "🔗 查看部署狀態："
    echo "   https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"
else
    echo "❌ 推送失敗，請檢查："
    echo "   1. 遠端倉庫設定是否正確"
    echo "   2. 是否有推送權限"
    echo "   3. 網路連線是否正常"
    exit 1
fi

echo "🎉 完成！"
