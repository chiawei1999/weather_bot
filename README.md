# LINE Bot 天氣查詢專案

這是一個使用 Python + FastAPI + LINE Messaging API 製作的天氣查詢 Bot，用戶可以透過 LINE 的 Rich Menu 點選「台北市」或「新北市」行政區，快速取得即時與未來的氣象資訊。

## 📌 功能簡介
- 查詢「台北市」與「新北市」各行政區天氣
- 使用 LINE Rich Menu 與 Flex Message 提升互動體驗
- 整合中央氣象署 Open Data API
- 自動化部署至 AWS EC2（支援 GitHub Actions + Docker）

## 🧱 技術架構
- 語言：Python 3.10
- Web 框架：FastAPI
- LINE SDK：line-bot-sdk v2.4.1
- 前端互動：Rich Menu + Flex Message
- 天氣資料來源：中央氣象署 F-D0047-061/069 API
- 部署方式：Docker + GitHub Actions + AWS EC2

## 📁 專案結構
```
weather-bot/
├── app.py                  # FastAPI 主程式
├── weather_request.py      # 處理氣象 API
├── Area_FlexMessage.py     # 建立行政區按鈕選單
├── RichMenu.py             # 建立與設定 Rich Menu
├── .env                    # API 金鑰與 LINE 設定
├── requirements.txt        # 套件需求
├── Dockerfile              # Docker 建置指令
└── .github/workflows/      # GitHub Actions 設定檔
```

## 🚀 快速啟動（本地端）
```bash
# 安裝依賴套件
pip install -r requirements.txt

# 啟動服務
uvicorn app:app --reload --port 8000
```

## 🐳 Docker 部署（建議用於雲端）
```bash
docker build -t weather-bot .
docker run -d -p 80:8000 --env-file .env weather-bot
```

## 🤖 GitHub Actions CI/CD 自動部署
當你推送至 `main` 分支時：
1. Actions 自動 SCP 專案檔案至 EC2
2. 在 EC2 上重建 Docker 映像並重啟服務

### GitHub Secrets 需要設定：
- `EC2_HOST`：EC2 公網 IP
- `EC2_USER`：登入使用者（如 ubuntu）
- `EC2_SSH_KEY`：私鑰內容（不含換行）

## 📦 套件依賴
```txt
fastapi==0.110.0
uvicorn==0.29.0
line-bot-sdk==2.4.1
python-dotenv==1.0.1
requests==2.31.0
Pillow==10.2.0
```

## 📄 授權
MIT License. 本專案僅供學術研究與學習用途使用。

---
Made with ❤️ by 劉家瑋

