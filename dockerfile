FROM python:3.10-slim

# 設定工作資料夾
WORKDIR /app

# 複製檔案
COPY . .

# 安裝依賴套件
RUN pip install --no-cache-dir -r requirements.txt

# 明確暴露 API port
EXPOSE 8000

# 預設執行 FastAPI 伺服器
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
