from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage

from weather_request import fetch_weather, parse_weather
from Area_FlexMessage import generate_flex_bubbles, taipei_districts, new_taipei_districts
from RichMenu import setup_line_rich_menu, ensure_rich_menu_image_exists

from dotenv import dotenv_values
from contextlib import asynccontextmanager
import uvicorn

# 載入環境變數
config = dotenv_values(".env")
LINE_CHANNEL_ACCESS_TOKEN = config["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = config["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# FastAPI 應用與 lifespan：初始化 Rich Menu
@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_rich_menu_image_exists()
    setup_line_rich_menu(line_bot_api)
    yield

app = FastAPI(lifespan=lifespan)

# Webhook 接收端點
@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    body_text = body.decode("utf-8")

    try:
        handler.handle(body_text, signature)
    except InvalidSignatureError:
        return JSONResponse(content={"message": "Invalid signature."}, status_code=400)

    return JSONResponse(content={"message": "OK"}, status_code=200)

# 處理訊息事件
@handler.add(MessageEvent)
def handle_message(event):
    if not isinstance(event.message, TextMessage):
        return

    user_text = event.message.text.strip()

    # 使用者查詢城市行政區
    if user_text == "我想要台北的氣象資訊":
        flex = generate_flex_bubbles("台北", taipei_districts)
        line_bot_api.reply_message(event.reply_token, FlexSendMessage("請選擇台北市的行政區", flex))
        return

    if user_text == "我想要新北的氣象資訊":
        flex = generate_flex_bubbles("新北", new_taipei_districts)
        line_bot_api.reply_message(event.reply_token, FlexSendMessage("請選擇新北市的行政區", flex))
        return

    # 使用者點選行政區
    if user_text.startswith("我想要台北") and user_text.endswith("的氣象資訊"):
        district = user_text.replace("我想要台北", "").replace("的氣象資訊", "")
        if district in taipei_districts:
            _reply_weather(event.reply_token, district)
        else:
            _reply_invalid_district(event.reply_token, district)
        return

    if user_text.startswith("我想要新北") and user_text.endswith("的氣象資訊"):
        district = user_text.replace("我想要新北", "").replace("的氣象資訊", "")
        if district in new_taipei_districts:
            _reply_weather(event.reply_token, district)
        else:
            _reply_invalid_district(event.reply_token, district)
        return

    # 未知指令
    line_bot_api.reply_message(event.reply_token, TextSendMessage("請使用 LINE Rich Menu 點選城市來查詢天氣資訊！"))

# 回傳天氣資訊
def _reply_weather(reply_token, location):
    data = fetch_weather(location)
    if data:
        result = parse_weather(data, location)
        line_bot_api.reply_message(reply_token, TextSendMessage(result))
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(f"取得 {location} 的氣象資料失敗，請稍後再試。"))

# 回傳行政區錯誤
def _reply_invalid_district(reply_token, district):
    line_bot_api.reply_message(reply_token, TextSendMessage(f"無法識別行政區「{district}」，請使用選單選擇有效的行政區。"))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
