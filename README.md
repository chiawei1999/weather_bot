# 🌤 LINE Bot 天氣查詢專案

這是一個以 Python + FastAPI + LINE Messaging API 製作的氣象查詢機器人，用戶可透過 LINE Rich Menu 快速查詢「台北市」與「新北市」各行政區的天氣狀況。

本專案支援 Cloudflare Tunnel + GitHub Actions 自動部署至 AWS EC2，並使用 Docker 容器化運行。

---

## 📌 功能簡介

- 點選 Rich Menu 快速查詢行政區天氣
- 整合中央氣象署 F-D0047-061/069 天氣資料
- 使用 Flex Message 呈現行政區選單
- Docker 打包 + GitHub Actions CI/CD
- 使用 Cloudflare Tunnel 快速建置 HTTPS Webhook

---

## 🧱 技術架構

| 類別 | 技術 |
|------|------|
| 語言 | Python 3.10 |
| Web 框架 | FastAPI |
| SDK | LINE Messaging API SDK v2.4.1 |
| 天氣資料來源 | 中央氣象署 OpenData API |
| 容器化 | Docker |
| 部署平台 | AWS EC2（Ubuntu） |
| 自動部署 | GitHub Actions |
| HTTPS 反向代理 | Cloudflare Tunnel（trycloudflare.com） |

---

## 📁 專案結構

```
weather-bot/
├── app.py                  # FastAPI 主程式
├── weather_request.py      # 處理氣象 API 請求
├── Area_FlexMessage.py     # Flex Message 行政區按鈕
├── RichMenu.py             # Rich Menu 設定
├── .env                    # API 金鑰與 LINE 設定
├── Dockerfile              # Docker 打包設定
├── requirements.txt        # Python 套件
└── .github/workflows/
    └── deploy.yml          # GitHub Actions 自動部署流程
```

---

## 🚀 快速啟動（本地測試）

```bash
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

---

## 🐳 Docker 部署（建議用於 EC2）

```bash
docker build -t weather-bot .
docker run -d -p 80:8000 --env-file .env --network host --name weather-bot weather-bot
```

---

## 🤖 GitHub Actions CI/CD 自動部署

只要 Push 到 `main`，將會自動：

1. 將專案傳到 EC2
2. 建立 `.env` 檔案
3. Docker build & run（含 host 網路設定）
4. 啟動 cloudflared systemd
5. 自動建立 HTTPS Webhook 隧道（trycloudflare.com）

---

### 🔐 GitHub Secrets 需要設定：

| 名稱 | 用途 |
|------|------|
| `EC2_HOST` | EC2 公網 IP |
| `EC2_USER` | 登入用戶名（Ubuntu 預設為 `ubuntu`） |
| `EC2_SSH_KEY` | EC2 的私鑰（`.pem` 內容） |
| `WEATHERBOTENV` | `.env` 內容（包含 LINE token、secret、CWA 授權碼） |

---

## 🌐 Webhook 設定範例（LINE Developers）

```txt
Webhook URL: https://xxxx.trycloudflare.com/callback
```

> *每次重開 tunnel 會換網址，如需固定網址建議使用 Named Tunnel*

---

## 📦 套件依賴

```txt
fastapi==0.110.0
uvicorn==0.29.0
line-bot-sdk==2.4.1
python-dotenv==1.0.1
requests==2.28.1
Pillow==10.2.0
```

---

## 📄 授權說明

MIT License  
本專案僅供學術研究與學習用途使用，請勿用於商業用途。

---

Made with ☕ & ❤️ by 劉家瑋